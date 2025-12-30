#!/usr/bin/env python3
"""
Test Gmail credentials
"""
import smtplib
from dotenv import load_dotenv
import os

load_dotenv()

sender = os.getenv('SENDER_EMAIL')
password = os.getenv('GMAIL_APP_PASSWORD')

print("=" * 60)
print("Testing Gmail Connection")
print("=" * 60)
print(f"Email: {sender}")
print(f"Password length: {len(password)} characters")
print()

try:
    print("Attempting to connect to Gmail SMTP server...")
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) as server:
        print("✅ Connected to Gmail SMTP server")

        print("Attempting to login...")
        server.login(sender, password)
        print("✅ Login successful!")
        print()
        print("=" * 60)
        print("✨ Your Gmail credentials are working!")
        print("=" * 60)

except smtplib.SMTPAuthenticationError as e:
    print("❌ Authentication failed!")
    print()
    print("This means the password is incorrect.")
    print()
    print("SOLUTION: You need to generate a Gmail App Password")
    print()
    print("Steps:")
    print("1. Go to: https://myaccount.google.com/security")
    print("2. Enable 2-Step Verification (if not already enabled)")
    print("3. Go to: https://myaccount.google.com/apppasswords")
    print("4. Create a new app password:")
    print("   - Select app: 'Mail'")
    print("   - Select device: 'Other' (name it 'AI Papers')")
    print("5. Copy the 16-character password")
    print("6. Paste it in the .env file as GMAIL_APP_PASSWORD")
    print()
    print(f"Error details: {e}")

except Exception as e:
    print(f"❌ Connection error: {e}")
    print()
    print("Check your internet connection and try again.")
