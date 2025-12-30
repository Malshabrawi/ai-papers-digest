#!/usr/bin/env python3
"""
Scheduler for AI Papers Daily Digest

Runs the main script daily at configured time (default: 9 PM)
"""
import schedule
import time
import os
from dotenv import load_dotenv
from datetime import datetime
from main import main


def run_daily_job():
    """Run the daily papers job"""
    print("\n" + "🔔" * 40)
    print(f"🔔 Scheduled job triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔔" * 40 + "\n")

    try:
        # Get topic from environment
        topic = os.getenv('TOPIC_FILTER', '').strip()
        topic = topic if topic else None

        # Run main job
        main(topic=topic)

        print("\n✅ Daily job completed successfully!")

    except Exception as e:
        print(f"\n❌ Error in scheduled job: {e}")
        import traceback
        traceback.print_exc()


def start_scheduler():
    """Start the scheduler with configured time"""
    load_dotenv()

    schedule_time = os.getenv('SCHEDULE_TIME', '21:00')
    topic = os.getenv('TOPIC_FILTER', '').strip()

    print("=" * 80)
    print("🤖 AI Papers Daily Digest - Scheduler")
    print("=" * 80)
    print(f"⏰ Schedule: Daily at {schedule_time}")
    print(f"🎯 Topic: {topic if topic else 'All trending AI papers'}")
    print(f"📧 Recipient: {os.getenv('RECIPIENT_EMAIL')}")
    print(f"🚀 Scheduler started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("\nPress Ctrl+C to stop the scheduler\n")

    # Schedule the job
    schedule.every().day.at(schedule_time).do(run_daily_job)

    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    except KeyboardInterrupt:
        print("\n\n⏹️  Scheduler stopped by user")
        print("Goodbye! 👋\n")


if __name__ == "__main__":
    start_scheduler()
