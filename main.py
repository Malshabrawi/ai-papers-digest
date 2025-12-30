#!/usr/bin/env python3
"""
AI Papers Daily Digest - Main Application

Fetches viral AI papers, summarizes them with Gemini AI,
downloads PDFs, and sends email digest.
"""
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

from fetch_papers import get_papers
from summarizer import summarize_papers
from download_pdfs import download_all_papers, create_index_file
from email_sender import send_email


def main(topic: str = None):
    """
    Main function to fetch, summarize, download, and email papers

    Args:
        topic: Optional topic filter (e.g., "agentic ai")
    """
    print("=" * 80)
    print("🤖 AI Papers Daily Digest")
    print("=" * 80)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load environment variables
    load_dotenv()

    # Get configuration
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    sender_email = os.getenv('SENDER_EMAIL')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD')
    num_papers = int(os.getenv('NUM_PAPERS', 5))
    topic_filter = topic or os.getenv('TOPIC_FILTER', '').strip()

    # Validate required environment variables
    if not gemini_api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file")
        sys.exit(1)

    if not all([recipient_email, sender_email, gmail_password]):
        print("❌ Error: Email configuration missing in .env file")
        print("   Required: RECIPIENT_EMAIL, SENDER_EMAIL, GMAIL_APP_PASSWORD")
        sys.exit(1)

    if topic_filter:
        print(f"🎯 Topic filter: {topic_filter}")
    else:
        print("📚 Fetching trending papers (no topic filter)")

    print(f"📊 Target: {num_papers} papers")
    print()

    # Step 1: Fetch papers
    print("=" * 80)
    print("STEP 1: Fetching Papers")
    print("=" * 80)
    papers = get_papers(topic=topic_filter, num_papers=num_papers)

    if not papers:
        print("❌ No papers found. Exiting.")
        sys.exit(1)

    print(f"✅ Fetched {len(papers)} papers\n")

    # Step 2: Summarize papers
    print("=" * 80)
    print("STEP 2: Summarizing with Gemini AI")
    print("=" * 80)
    summarized_papers = summarize_papers(papers, gemini_api_key)
    print(f"✅ Summarized {len(summarized_papers)} papers\n")

    # Step 3: Download PDFs
    print("=" * 80)
    print("STEP 3: Downloading PDFs")
    print("=" * 80)
    download_result = download_all_papers(summarized_papers, base_folder="papers")
    create_index_file(summarized_papers, download_result['folder_path'])
    print(f"✅ Papers saved to: {download_result['folder_path']}\n")

    # Step 4: Send email
    print("=" * 80)
    print("STEP 4: Sending Email")
    print("=" * 80)
    email_success = send_email(
        recipient=recipient_email,
        sender=sender_email,
        password=gmail_password,
        papers=summarized_papers,
        topic=topic_filter if topic_filter else None
    )

    # Summary
    print("\n" + "=" * 80)
    print("📊 EXECUTION SUMMARY")
    print("=" * 80)
    print(f"✅ Papers fetched: {len(papers)}")
    print(f"✅ Papers summarized: {len(summarized_papers)}")
    print(f"✅ PDFs downloaded: {len(download_result['downloaded_files'])}/{len(papers)}")
    print(f"✅ Email sent: {'Yes' if email_success else 'No'}")
    print(f"📁 Papers folder: {download_result['folder_path']}")
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    if email_success and len(download_result['downloaded_files']) == len(papers):
        print("\n✨ All tasks completed successfully!")
        return 0
    else:
        print("\n⚠️  Some tasks completed with warnings.")
        return 1


if __name__ == "__main__":
    # Check for topic argument
    topic_arg = None
    if len(sys.argv) > 1:
        topic_arg = ' '.join(sys.argv[1:])
        print(f"Using topic from command line: {topic_arg}")

    exit_code = main(topic=topic_arg)
    sys.exit(exit_code)
