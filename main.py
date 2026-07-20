"""
SARNA v4.0 — Main Orchestrator
================================
Entry point for both execution loops:

  python main.py --mode ingestion      # Hourly RSS scan → Gemini → Sheets
  python main.py --mode notification   # Twice-daily email digest

  python main.py --mode ingestion --test   # Test ingestion (dry run)
  python main.py --mode notification --test # Test notification

The two loops are decoupled by design:
  - Ingestion runs every 60 minutes (captures data before RSS buffer flushes)
  - Notification runs at 9 AM & 9 PM IST (digest for human review)
"""

import argparse
import sys
import time
from datetime import datetime

# Load .env for local development (GitHub Actions uses secrets directly)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from config import GEMINI_SLEEP_BETWEEN_CALLS
from reddit_rss_scanner import scan_reddit, save_processed_posts
from comment_generator import init_gemini, generate_comment_and_dm
from google_sheets_writer import authenticate_sheets, build_row, append_rows
from email_notifier import run_notification


# =============================================================================
# Ingestion Pipeline
# =============================================================================
def run_ingestion(test_mode: bool = False):
    """
    Full ingestion pipeline:
    1. Scan RSS feed for qualified posts
    2. Initialize Gemini model
    3. Authenticate Google Sheets
    4. For each post: generate comment + DM → build row → collect
    5. Batch-append all rows to Sheet
    6. Save processed posts ledger

    If test_mode is True, runs everything but skips Sheet writes.
    """
    start_time = time.time()
    now = datetime.now()

    print(f"\n{'🚀' * 30}")
    print(f"  SARNA v4.0 — Ingestion Loop")
    print(f"  {now.strftime('%A, %B %d, %Y at %I:%M %p')}")
    if test_mode:
        print(f"  ⚠️  TEST MODE — Sheets writes will be skipped")
    print(f"{'🚀' * 30}\n")

    # =========================================================================
    # Step 1: Scan Reddit RSS for qualified posts
    # =========================================================================
    posts, updated_ids = scan_reddit()

    if not posts:
        print("😴 No new qualified posts found. Saving ledger and exiting.")
        save_processed_posts(updated_ids)
        _print_summary(0, 0, start_time, test_mode)
        return

    # =========================================================================
    # Step 2: Initialize Gemini
    # =========================================================================
    print("🤖 Step 2: Initializing Gemini...")
    gemini_client = init_gemini()

    # =========================================================================
    # Step 3: Authenticate Google Sheets (unless test mode)
    # =========================================================================
    service, sheet_id = None, None
    if not test_mode:
        print("\n📊 Step 3: Authenticating Google Sheets...")
        service, sheet_id = authenticate_sheets()
        if not service:
            print("  ⚠️  Sheets auth failed — will generate comments but cannot write")

    # =========================================================================
    # Step 4: Generate comment + DM for each post
    # =========================================================================
    print(f"\n💬 Step 4: Generating comments for {len(posts)} posts...")
    rows = []
    success_count = 0

    for i, post in enumerate(posts, 1):
        print(f"\n  [{i}/{len(posts)}] r/{post['subreddit']}: {post['title'][:60]}...")

        try:
            # Generate comment and DM
            result = generate_comment_and_dm(post, gemini_client)
            comment = result["comment"]
            dm = result["dm"]

            # Build Sheet row
            row = build_row(post, comment, dm)
            rows.append(row)
            success_count += 1

            print(f"    ✅ Comment: {len(comment.split())} words | DM: {len(dm.split())} words")

        except Exception as e:
            # If ONE post fails, log and continue — never crash the pipeline
            print(f"    ❌ Failed to process post: {e}")
            continue

        # Rate limit: 4.5-second sleep between Gemini calls
        if gemini_client and i < len(posts):
            print(f"    ⏳ Rate limit sleep ({GEMINI_SLEEP_BETWEEN_CALLS}s)...")
            time.sleep(GEMINI_SLEEP_BETWEEN_CALLS)

    # =========================================================================
    # Step 5: Batch-append rows to Google Sheet
    # =========================================================================
    if rows and service and sheet_id and not test_mode:
        print(f"\n📊 Step 5: Writing {len(rows)} rows to Google Sheet...")
        append_rows(service, sheet_id, rows)
    elif test_mode and rows:
        print(f"\n📊 Step 5: TEST MODE — {len(rows)} rows generated but NOT written to Sheet")
        for j, row in enumerate(rows, 1):
            print(f"  Row {j}: {row[0]} | {row[2][:60]}...")

    # =========================================================================
    # Step 6: Save processed posts ledger
    # =========================================================================
    print(f"\n💾 Step 6: Saving processed posts ledger...")
    save_processed_posts(updated_ids)
    print(f"  ✅ Ledger updated: {len(updated_ids)} total tracked IDs")

    # =========================================================================
    # Summary
    # =========================================================================
    _print_summary(success_count, len(posts), start_time, test_mode)


def _print_summary(success: int, total: int, start_time: float, test_mode: bool):
    """Print the run summary."""
    elapsed = round(time.time() - start_time, 1)
    print(f"\n{'='*60}")
    print(f"✅ Ingestion run complete in {elapsed}s")
    print(f"   📋 Posts scanned: {total}")
    print(f"   💬 Comments generated: {success}")
    if test_mode:
        print(f"   📊 Sheet writes: SKIPPED (test mode)")
    print(f"{'='*60}\n")


# =============================================================================
# CLI entry point
# =============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="SARNA v4.0 — Sahajta AI Reddit Networking Agent"
    )
    parser.add_argument(
        "--mode",
        choices=["ingestion", "notification"],
        required=True,
        help="Execution mode: 'ingestion' (RSS scan + Gemini + Sheets) or 'notification' (email digest)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode: runs pipeline but skips external writes (Sheets, email)",
    )

    args = parser.parse_args()

    if args.mode == "ingestion":
        run_ingestion(test_mode=args.test)

    elif args.mode == "notification":
        if args.test:
            print("🧪 Notification test mode — will attempt real Sheet read + email send")
        run_notification()


if __name__ == "__main__":
    main()
