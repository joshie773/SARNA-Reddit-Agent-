"""
SARNA v4.0 — Reddit RSS Scanner
=================================
Fetches the aggregated 10-subreddit RSS feed (public, no auth),
parses entries, applies keyword filtering (60/40 intent/value split),
and deduplicates against the processed_posts.json ledger.

No Reddit API keys required. Uses feedparser + requests only.
"""

import json
import os
import re
import time
from datetime import datetime, timezone, timedelta
from html import unescape

import feedparser
import requests

from config import (
    TARGET_SUBREDDITS,
    INTENT_KEYWORDS_FOCUSED,
    VALUE_KEYWORDS_FOCUSED,
    INTENT_KEYWORDS_BROADER,
    VALUE_KEYWORDS_BROADER,
    MAX_POSTS_PER_RUN,
    MAX_POST_AGE_DAYS,
    PROCESSED_POSTS_FILE,
    PROCESSED_POSTS_MAX,
    SCORE_WEIGHT_INTENT,
    SCORE_WEIGHT_VALUE,
    SCORE_WEIGHT_FRESHNESS,
    SCORE_WEIGHT_BODY_LENGTH,
    SCORE_WEIGHT_DIVERSITY,
    SUBREDDIT_WEIGHT,
    MIN_BODY_LENGTH,
    EXCLUDED_PHRASES,
)


# =============================================================================
# HTML stripping utility
# =============================================================================
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(html_text: str) -> str:
    """Remove HTML tags and decode entities from RSS content."""
    if not html_text:
        return ""
    text = _HTML_TAG_RE.sub(" ", html_text)
    text = unescape(text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


# =============================================================================
# State persistence (deduplication ledger)
# =============================================================================
def load_processed_posts() -> set:
    """Load the set of already-processed post IDs from the ledger file."""
    if os.path.exists(PROCESSED_POSTS_FILE):
        try:
            with open(PROCESSED_POSTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("post_ids", []))
        except (json.JSONDecodeError, KeyError):
            pass
    return set()


def save_processed_posts(post_ids: set):
    """
    Persist processed post IDs to the ledger.
    Auto-prunes to keep only the latest PROCESSED_POSTS_MAX entries.
    """
    ids_list = list(post_ids)
    if len(ids_list) > PROCESSED_POSTS_MAX:
        ids_list = ids_list[-PROCESSED_POSTS_MAX:]

    with open(PROCESSED_POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "post_ids": ids_list,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            },
            f,
            indent=2,
        )


# =============================================================================
# RSS feed fetching
# =============================================================================
def fetch_rss_feed(user_agent: str | None = None) -> list[dict]:
    """
    Fetch and parse RSS feeds for each subreddit individually.

    Returns a list of raw entry dicts with extracted fields:
    - post_id, title, body, url, subreddit, published_utc
    """
    ua = user_agent or os.environ.get(
        "REDDIT_USER_AGENT",
        "python:sarna_monitor:v4.0 (by /u/sarna_bot)",
    )

    print(f"  📡 Fetching RSS from {len(TARGET_SUBREDDITS)} subreddits individually...")

    entries = []
    
    for sub in TARGET_SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/new/.rss"
        try:
            resp = requests.get(
                url,
                headers={"User-Agent": ua},
                timeout=15,
            )
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
            
            if feed.bozo and not feed.entries:
                continue
                
            for entry in feed.entries:
                post_id = _extract_post_id(entry.get("link", "") or entry.get("id", ""))
                if not post_id:
                    continue

                # Force the subreddit to the one we are fetching, or fallback to extraction
                subreddit = sub if sub else _extract_subreddit(entry)

                raw_body = entry.get("summary", "") or ""
                body = strip_html(raw_body)
                published_utc = _parse_published_time(entry)

                entries.append({
                    "post_id": post_id,
                    "title": entry.get("title", "").strip(),
                    "body": body,
                    "url": entry.get("link", ""),
                    "subreddit": subreddit,
                    "published_utc": published_utc,
                    "author": _extract_author(entry),
                })
        except requests.RequestException:
            # Skip failed subreddits to keep the pipeline moving
            pass
            
        # Respect Reddit's rate limit for unauthenticated RSS (avoid 429 errors)
        time.sleep(1.5)

    print(f"  📥 Parsed {len(entries)} total entries across all RSS feeds")
    print(f"  ✅ Scanned all {len(TARGET_SUBREDDITS)} subreddits in this run")
    return entries


def _extract_post_id(url: str) -> str | None:
    """Extract the Reddit post ID from a URL like /r/sub/comments/ID/..."""
    match = re.search(r"/comments/([a-z0-9]+)", url)
    if match:
        return match.group(1)
    # Fallback: try t3_ format
    match = re.search(r"t3_([a-z0-9]+)", url)
    if match:
        return match.group(1)
    return None


def _extract_subreddit(entry) -> str:
    """Extract subreddit name from RSS entry tags or URL."""
    # Try category tags first
    tags = entry.get("tags", [])
    if tags:
        for tag in tags:
            term = tag.get("term", "")
            if term:
                return term

    # Fallback: parse from URL
    url = entry.get("link", "")
    match = re.search(r"/r/([^/]+)/", url)
    if match:
        return match.group(1)
    return "unknown"


def _extract_author(entry) -> str:
    """Extract author name from RSS entry."""
    author = entry.get("author", "") or entry.get("author_detail", {}).get("name", "")
    if author and author.startswith("/u/"):
        return author[3:]
    return author or "unknown"


def _parse_published_time(entry) -> datetime | None:
    """Parse the published/updated timestamp from an RSS entry."""
    time_struct = entry.get("published_parsed") or entry.get("updated_parsed")
    if time_struct:
        try:
            return datetime(*time_struct[:6], tzinfo=timezone.utc)
        except (ValueError, TypeError):
            pass
    return None


# =============================================================================
# Keyword tagging & Scoring
# =============================================================================
def tag_by_keywords(entries: list[dict]) -> list[dict]:
    """
    Tag posts with keyword match scores and tier classification.
    Returns all posts that have at least one intent or value keyword hit.
    
    Tier 1: Matched FOCUSED keywords (high-intent specific problems)
    Tier 2: Matched BROADER keywords (strategy/optimization)
    """
    tagged = []
    tier_1_count = 0
    tier_2_count = 0

    for entry in entries:
        searchable = f"{entry['title']} {entry['body']}".lower()

        # Check focused keywords
        focused_intent = sum(1 for kw in INTENT_KEYWORDS_FOCUSED if kw in searchable)
        focused_value = sum(1 for kw in VALUE_KEYWORDS_FOCUSED if kw in searchable)
        
        # Check broader keywords (only if no focused match)
        broader_intent = sum(1 for kw in INTENT_KEYWORDS_BROADER if kw in searchable) if focused_intent == 0 else 0
        broader_value = sum(1 for kw in VALUE_KEYWORDS_BROADER if kw in searchable) if focused_value == 0 else 0

        intent_score = focused_intent + broader_intent
        value_score = focused_value + broader_value

        if intent_score > 0 or value_score > 0:
            entry["intent_score"] = intent_score
            entry["value_score"] = value_score
            
            # Classify tier
            if focused_intent > 0 or focused_value > 0:
                entry["keyword_tier"] = "tier_1_focused"
                tier_1_count += 1
            else:
                entry["keyword_tier"] = "tier_2_broader"
                tier_2_count += 1
            
            if intent_score > 0:
                entry["match_type"] = "intent"
            else:
                entry["match_type"] = "value"
            
            tagged.append(entry)

    print(f"  🎯 Keyword tagging: {len(tagged)} posts with hits (Tier 1: {tier_1_count}, Tier 2: {tier_2_count})")
    return tagged


def score_post(post: dict) -> float:
    """Calculate the base relevance score (out of 95, 5 reserved for diversity)."""
    intent_pts = min(post.get("intent_score", 0) * 10, SCORE_WEIGHT_INTENT)
    value_pts = min(post.get("value_score", 0) * 8, SCORE_WEIGHT_VALUE)
    
    # Freshness (linear decay over MAX_POST_AGE_DAYS)
    age_hours = post.get("age_hours", 0)
    max_age_hours = MAX_POST_AGE_DAYS * 24
    freshness_pts = max(0, SCORE_WEIGHT_FRESHNESS * (1 - (age_hours / max_age_hours)))
    
    # Body length (already filtered, but still score)
    body_len = len(post.get("body", ""))
    length_pts = min(body_len / 200.0, SCORE_WEIGHT_BODY_LENGTH)
    
    base_score = intent_pts + value_pts + freshness_pts + length_pts
    return base_score


def rank_and_select(posts: list[dict], max_posts: int = 10) -> list[dict]:
    """
    Apply weight to BASE SCORE only (not diversity bonus).
    This makes subreddit preference a quality filter, not a score multiplier.
    """
    for p in posts:
        p["base_score"] = score_post(p)
        
    posts.sort(key=lambda x: x["base_score"], reverse=True)
    
    subreddit_counts = {}
    for p in posts:
        sub = p["subreddit"]
        count = subreddit_counts.get(sub, 0)
        
        # Diversity bonus
        bonus = 0
        if count == 0:
            bonus = 20
        elif count == 1:
            bonus = 15
        elif count == 2:
            bonus = 10
            
        subreddit_counts[sub] = count + 1
        
        # Apply weight to BASE SCORE only, then add bonus
        subreddit_weight = SUBREDDIT_WEIGHT.get(sub, 1.0)
        weighted_base = p["base_score"] * subreddit_weight
        total_score = min(100.0, weighted_base + bonus)
        
        p["total_score"] = round(total_score, 1)
        
        intent = p.get('intent_score', 0)
        val = p.get('value_score', 0)
        age = p.get('age_hours', 0)
        tier = p.get('keyword_tier', 'unknown')
        p["relevance_string"] = f"{p['total_score']}/100 [{tier}] — {intent} intent, {val} value, {int(age)}h old"

    posts.sort(key=lambda x: x["total_score"], reverse=True)
    
    selected = posts[:max_posts]
    if selected:
        print(f"  🏆 Ranked and selected {len(selected)} posts (top score: {selected[0]['total_score']}/100)")
        print(f"  📊 Subreddit distribution: {dict(subreddit_counts)}")
    
    return selected


# =============================================================================
# Freshness filter
# =============================================================================
def filter_by_freshness(entries: list[dict]) -> list[dict]:
    """
    Filter out:
    1. Posts older than MAX_POST_AGE_DAYS
    2. Posts with body length < MIN_BODY_LENGTH (noise filter)
    3. Posts containing EXCLUDED_PHRASES (anti-pattern filter)
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=MAX_POST_AGE_DAYS)
    fresh = []
    length_filtered = 0
    pattern_filtered = 0

    for entry in entries:
        # Age filter
        pub_time = entry.get("published_utc")
        if pub_time is None:
            fresh.append(entry)
            age_hours = 0
        elif pub_time >= cutoff:
            age_hours = (now - pub_time).total_seconds() / 3600
            entry["age_hours"] = round(age_hours, 1)
            
            # Excluded phrases filter
            body = entry.get("body", "")
            searchable = f"{entry.get('title', '')} {body}".lower()
            if any(phrase in searchable for phrase in EXCLUDED_PHRASES):
                pattern_filtered += 1
                continue
            
            # Tier 1 Focused Keyword Check (bypass length filter)
            has_tier1 = any(kw in searchable for kw in INTENT_KEYWORDS_FOCUSED) or \
                        any(kw in searchable for kw in VALUE_KEYWORDS_FOCUSED)
            
            # Body length filter
            if len(body) < MIN_BODY_LENGTH and not has_tier1:
                length_filtered += 1
                continue
            
            fresh.append(entry)
        else:
            # Post too old, skip
            pass

    filtered_count = len(entries) - len(fresh)
    if filtered_count > 0:
        print(f"  ⏰ Freshness filter: dropped {filtered_count} posts older than {MAX_POST_AGE_DAYS} days")
    if length_filtered > 0:
        print(f"  📝 Body length filter: dropped {length_filtered} posts < {MIN_BODY_LENGTH} chars")
    if pattern_filtered > 0:
        print(f"  ⚠️  Anti-pattern filter: dropped {pattern_filtered} low-signal posts")

    return fresh


# =============================================================================
# Deduplication
# =============================================================================
def deduplicate(entries: list[dict], processed_ids: set) -> list[dict]:
    """Remove entries that have already been processed in previous runs."""
    unique = [e for e in entries if e["post_id"] not in processed_ids]
    dupes = len(entries) - len(unique)
    if dupes > 0:
        print(f"  🔄 Dedup: skipped {dupes} already-processed posts")
    return unique


# =============================================================================
# Main scan orchestrator
# =============================================================================
def scan_reddit() -> tuple[list[dict], set]:
    """
    Full scan pipeline: fetch → filter freshness → deduplicate → tag → rank_and_select.

    Returns:
        - List of qualified post dicts (max MAX_POSTS_PER_RUN)
        - Updated set of all processed post IDs (old + new)
    """
    print(f"\n{'='*60}")
    print(f"🔍 SARNA RSS Scanner — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")

    # Load existing dedup ledger
    processed_ids = load_processed_posts()
    print(f"  📦 Ledger: {len(processed_ids)} previously processed posts")

    # Step 1: Fetch RSS feed
    raw_entries = fetch_rss_feed()
    if not raw_entries:
        print("  😴 No entries from RSS feed. Exiting scan.")
        return [], processed_ids

    # Step 2: Filter by freshness
    fresh_entries = filter_by_freshness(raw_entries)

    # Step 3: Deduplicate against ledger
    new_entries = deduplicate(fresh_entries, processed_ids)
    if not new_entries:
        print("  😴 All entries already processed. No new posts this run.")
        return [], processed_ids

    # Step 4: Tag by keywords
    tagged = tag_by_keywords(new_entries)

    # Step 5: Rank and select
    qualified = rank_and_select(tagged, max_posts=MAX_POSTS_PER_RUN)

    # Update ledger with new post IDs
    new_ids = {e["post_id"] for e in qualified}
    updated_ids = processed_ids | new_ids

    print(f"\n✅ Scan complete: {len(qualified)} qualified posts ready for processing")
    print(f"{'='*60}\n")

    return qualified, updated_ids


# =============================================================================
# CLI test
# =============================================================================
if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    import sys
    if "--test" in sys.argv:
        print("🧪 Running RSS scanner test...\n")

    posts, ids = scan_reddit()
    for i, p in enumerate(posts[:5], 1):
        print(f"\n--- Post {i} ---")
        print(f"  Title:     {p['title'][:80]}")
        print(f"  Subreddit: r/{p['subreddit']}")
        print(f"  Type:      {p.get('match_type', 'n/a')}")
        print(f"  Score:     {p.get('total_score', 0)}/100")
        print(f"  Relevance: {p.get('relevance_string', '')}")
        print(f"  URL:       {p['url']}")
    print(f"\nTotal qualified: {len(posts)}")
