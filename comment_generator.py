"""
SARNA v4.0 — Comment & DM Generator
=====================================
Calls Gemini 2.0 Flash with the dual-layer compliance prompt to generate:
  1. A public value comment (max 150 words, ultra-casual)
  2. A private bridge DM (max 100 words, contextual follow-up)

Includes:
  - Strict 4.5-second sleep between API calls (protects 15 RPM free tier)
  - Banned word scanning with automatic retry (max 2 retries)
  - Pre-written fallback templates when Gemini fails
  - JSON output parsing with error recovery
"""

import json
import os
import random
import re
import time

from google import genai

from config import (
    GEMINI_MODEL,
    GEMINI_SLEEP_BETWEEN_CALLS,
    GEMINI_MAX_RETRIES,
    BANNED_WORDS,
    SYSTEM_PROMPT_TEMPLATE,
    SUBREDDIT_COMPLIANCE,
    FALLBACK_TEMPLATES,
)


# =============================================================================
# Gemini initialization
# =============================================================================
def init_gemini() -> genai.Client | None:
    """Initialize the Gemini client. Returns None if API key is missing."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("  ⚠️  GEMINI_API_KEY not set — will use fallback templates only")
        return None

    client = genai.Client(api_key=api_key)
    print(f"  ✅ Gemini model ready ({GEMINI_MODEL})")
    return client


# =============================================================================
# Banned word detection
# =============================================================================
def check_blacklist(text: str) -> list[str]:
    """
    Scan text for banned corporate jargon and promotional phrases.
    Returns list of found violations (empty if clean).
    """
    text_lower = text.lower()
    violations = [word for word in BANNED_WORDS if word in text_lower]
    return violations


# =============================================================================
# JSON response parsing
# =============================================================================
def parse_llm_json(raw_response: str) -> dict | None:
    """
    Parse the LLM response into a dict with 'comment' and 'dm' keys.
    Handles markdown code fences, extra whitespace, and other LLM quirks.
    """
    text = raw_response.strip()

    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object within the text
        match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
        else:
            return None

    # Validate required keys
    # Accept both "comment"/"dm" and "value_comment"/"bridge_dm" key variants
    comment = data.get("comment") or data.get("value_comment", "")
    dm = data.get("dm") or data.get("bridge_dm", "")

    if not comment:
        return None

    return {"comment": comment, "dm": dm}


# =============================================================================
# Core generation function
# =============================================================================
def _build_prompt(post: dict) -> str:
    """Build the user prompt containing the post data for Gemini."""
    title = post.get("title", "")
    body = post.get("body", "")[:500]  # Cap body at 500 chars for token efficiency

    return (
        f"POST TITLE: {title}\n\n"
        f"POST BODY: {body if body else '(no body text — title only)'}\n\n"
        f"This post was found in r/{post.get('subreddit', 'unknown')}. "
        f"Generate the JSON output now."
    )


def _build_system_prompt(subreddit: str) -> str:
    """Build the dual-layer system prompt for the given subreddit."""
    compliance = SUBREDDIT_COMPLIANCE.get(subreddit, {})
    layer_1 = compliance.get("layer_1_rules", "No specific rules available. Be helpful and non-promotional.")
    layer_2 = compliance.get("layer_2_culture", "Be casual, knowledgeable, and genuine.")

    return SYSTEM_PROMPT_TEMPLATE.format(
        subreddit_name=subreddit,
        layer_1_rules=layer_1,
        layer_2_culture=layer_2,
    )


def generate_with_gemini(
    client: genai.Client,
    post: dict,
) -> dict | None:
    """
    Generate comment + DM using Gemini with retry logic.

    Returns dict with 'comment' and 'dm' keys, or None on total failure.
    """
    subreddit = post.get("subreddit", "unknown")
    system_prompt = _build_system_prompt(subreddit)
    user_prompt = _build_prompt(post)

    for attempt in range(1, GEMINI_MAX_RETRIES + 2):  # 1 initial + 2 retries = 3 total
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\nUSER REQUEST:\n{user_prompt}",
            )

            raw_text = response.text
            if not raw_text:
                print(f"    ⚠️  Empty Gemini response (attempt {attempt})")
                continue

            # Parse JSON
            parsed = parse_llm_json(raw_text)
            if not parsed:
                print(f"    ⚠️  Invalid JSON from Gemini (attempt {attempt})")
                if attempt <= GEMINI_MAX_RETRIES:
                    time.sleep(GEMINI_SLEEP_BETWEEN_CALLS)
                continue

            # Check for banned words in both outputs
            comment_violations = check_blacklist(parsed["comment"])
            dm_violations = check_blacklist(parsed.get("dm", ""))
            all_violations = comment_violations + dm_violations

            if all_violations:
                print(f"    ⚠️  Banned words detected: {all_violations[:3]} (attempt {attempt})")
                if attempt <= GEMINI_MAX_RETRIES:
                    # Add stricter instruction for retry
                    user_prompt += (
                        f"\n\nCRITICAL RETRY: Your previous output contained banned words: "
                        f"{', '.join(all_violations)}. "
                        f"Remove ALL corporate jargon. Sound like a real human. "
                        f"Use lowercase, contractions, casual fillers."
                    )
                    time.sleep(GEMINI_SLEEP_BETWEEN_CALLS)
                    continue
                else:
                    # Max retries hit — fall through to fallback
                    print(f"    ❌ Banned words persist after {GEMINI_MAX_RETRIES} retries")
                    return None

            # Clean output — success
            return parsed

        except Exception as e:
            print(f"    ❌ Gemini API error (attempt {attempt}): {e}")
            if attempt <= GEMINI_MAX_RETRIES:
                time.sleep(GEMINI_SLEEP_BETWEEN_CALLS)
            continue

    return None  # All attempts exhausted


# =============================================================================
# Fallback template selection
# =============================================================================
def get_fallback_template(post: dict) -> dict:
    """
    Select a pre-written fallback template.
    Picks randomly from the template bank.
    """
    template = random.choice(FALLBACK_TEMPLATES)
    print(f"    ↩️  Using fallback template")
    return {
        "comment": template["comment"],
        "dm": template["dm"],
    }


# =============================================================================
# Main interface
# =============================================================================
def generate_comment_and_dm(
    post: dict,
    client: genai.Client | None = None,
) -> dict:
    """
    Generate a public comment and private DM for a Reddit post.

    Tries Gemini first, falls back to pre-written templates on failure.

    Args:
        post: Dict with 'title', 'body', 'subreddit', 'url' keys
        model: Initialized Gemini model (or None for template-only mode)

    Returns:
        Dict with 'comment' (str) and 'dm' (str) keys. Always returns something.
    """
    if client is not None:
        result = generate_with_gemini(client, post)
        if result:
            return result
        print(f"    ↩️  Gemini failed completely, falling back to template...")

    return get_fallback_template(post)


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

    sample_post = {
        "title": "My Shopify store gets 500 visitors/day but only 2-3 sales. What am I doing wrong?",
        "body": (
            "I've been running Facebook and Instagram ads for my clothing store "
            "for 3 months. Getting decent traffic but my conversion rate is 0.3%. "
            "I've tried changing product photos and descriptions but nothing works. "
            "Any advice?"
        ),
        "subreddit": "shopify",
        "url": "https://reddit.com/r/shopify/comments/test123/test_post/",
    }

    if "--test" in sys.argv:
        print("🧪 Running comment generator test...\n")

    client = init_gemini()

    print("\n=== Generating comment + DM ===")
    result = generate_comment_and_dm(sample_post, client)
    print(f"\n📝 Comment ({len(result['comment'].split())} words):")
    print(result["comment"])
    print(f"\n💬 DM ({len(result['dm'].split())} words):")
    print(result["dm"])

    # Verify no banned words
    violations = check_blacklist(result["comment"]) + check_blacklist(result["dm"])
    if violations:
        print(f"\n⚠️  VIOLATIONS: {violations}")
    else:
        print(f"\n✅ No banned words detected")
