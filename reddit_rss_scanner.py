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
    RSS_FEED_URL,
    INTENT_KEYWORDS,
    VALUE_KEYWORDS,
    MAX_POSTS_PER_RUN,
    MAX_POST_AGE_DAYS,
    PROCESSED_POSTS_FILE,
    PROCESSED_POSTS_MAX,
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
    Fetch and parse the aggregated 10-subreddit RSS feed.

    Returns a list of raw entry dicts with extracted fields:
    - post_id, title, body, url, subreddit, published_utc
    """
    ua = user_agent or os.environ.get(
        "REDDIT_USER_AGENT",
        "python:sarna_monitor:v4.0 (by /u/sarna_bot)",
    )

    print(f"  📡 Fetching RSS: {RSS_FEED_URL[:80]}...")

    try:
        resp = requests.get(
            RSS_FEED_URL,
            headers={"User-Agent": ua},
            timeout=30,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ❌ RSS fetch failed: {e}")
        return []

    feed = feedparser.parse(resp.text)

    if feed.bozo and not feed.entries:
        print(f"  ❌ RSS parse error: {feed.bozo_exception}")
        return []

    entries = []
    for entry in feed.entries:
        # Extract post ID from the entry link URL
        # URL format: https://www.reddit.com/r/shopify/comments/abc123/title/
        post_id = _extract_post_id(entry.get("link", "") or entry.get("id", ""))
        if not post_id:
            continue

        # Extract subreddit from category tags or URL
        subreddit = _extract_subreddit(entry)

        # Extract clean text body from HTML summary
        raw_body = entry.get("summary", "") or ""
        body = strip_html(raw_body)

        # Parse publish time
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

    print(f"  📥 Parsed {len(entries)} entries from RSS feed")
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
# Keyword filtering (60/40 intent/value split)
# =============================================================================
def filter_by_keywords(entries: list[dict]) -> list[dict]:
    """
    Apply the 60/40 intent/value keyword filter.
    Returns entries sorted by match type (intent first, then value).
    """
    intent_matches = []
    value_matches = []

    for entry in entries:
        searchable = f"{entry['title']} {entry['body']}".lower()

        # Check intent keywords (60% priority)
        intent_score = sum(1 for kw in INTENT_KEYWORDS if kw in searchable)

        # Check value keywords (40%)
        value_score = sum(1 for kw in VALUE_KEYWORDS if kw in searchable)

        if intent_score > 0:
            entry["match_type"] = "intent"
            entry["match_score"] = intent_score
            intent_matches.append(entry)
        elif value_score > 0:
            entry["match_type"] = "value"
            entry["match_score"] = value_score
            value_matches.append(entry)

    # Sort each group by match score (highest first)
    intent_matches.sort(key=lambda x: -x["match_score"])
    value_matches.sort(key=lambda x: -x["match_score"])

    # Apply 60/40 split: 6 intent + 4 value (from max 10)
    max_intent = int(MAX_POSTS_PER_RUN * 0.6)  # 6
    max_value = MAX_POSTS_PER_RUN - max_intent   # 4

    selected = intent_matches[:max_intent] + value_matches[:max_value]

    print(f"  🎯 Keyword filter: {len(intent_matches)} intent, {len(value_matches)} value")
    print(f"  ✂️  Selected: {min(len(intent_matches), max_intent)} intent + "
          f"{min(len(value_matches), max_value)} value = {len(selected)} total")

    return selected


# =============================================================================
# Freshness filter
# =============================================================================
def filter_by_freshness(entries: list[dict]) -> list[dict]:
    """Filter out posts older than MAX_POST_AGE_DAYS."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=MAX_POST_AGE_DAYS)
    fresh = []

    for entry in entries:
        pub_time = entry.get("published_utc")
        if pub_time is None:
            # If no timestamp, include it (benefit of the doubt)
            fresh.append(entry)
        elif pub_time >= cutoff:
            # Calculate age for logging
            age_hours = (now - pub_time).total_seconds() / 3600
            entry["age_hours"] = round(age_hours, 1)
            fresh.append(entry)

    filtered_count = len(entries) - len(fresh)
    if filtered_count > 0:
        print(f"  ⏰ Freshness filter: dropped {filtered_count} posts older than {MAX_POST_AGE_DAYS} days")

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
    Full scan pipeline: fetch → filter freshness → deduplicate → filter keywords → cap.

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

    # Step 4: Apply keyword filter (60/40 split)
    qualified = filter_by_keywords(new_entries)

    # Step 5: Cap to max posts per run
    if len(qualified) > MAX_POSTS_PER_RUN:
        qualified = qualified[:MAX_POSTS_PER_RUN]
        print(f"  ✂️  Capped at {MAX_POSTS_PER_RUN} posts")

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
        print(f"  Score:     {p.get('match_score', 0)} keyword hits")
        print(f"  URL:       {p['url']}")
    print(f"\nTotal qualified: {len(posts)}")
