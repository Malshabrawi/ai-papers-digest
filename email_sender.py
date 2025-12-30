"""
Send email with paper summaries
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict


def format_html_email(papers: List[Dict], topic: str = None) -> str:
    """
    Format papers into beautiful HTML email

    Args:
        papers: List of paper dictionaries with summaries
        topic: Optional topic filter used

    Returns:
        HTML string for email body
    """
    today = datetime.now().strftime('%A, %B %d, %Y')
    topic_text = f" - Topic: {topic}" if topic else ""

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1a73e8;
            border-bottom: 3px solid #1a73e8;
            padding-bottom: 15px;
            margin-top: 0;
        }}
        .header-info {{
            color: #666;
            font-size: 0.95em;
            margin-bottom: 30px;
        }}
        .paper {{
            background: #f8f9fa;
            border-left: 5px solid #34a853;
            padding: 25px;
            margin: 25px 0;
            border-radius: 8px;
        }}
        .paper-number {{
            color: #1a73e8;
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .paper-title {{
            color: #202124;
            font-size: 1.4em;
            font-weight: bold;
            margin-bottom: 15px;
            line-height: 1.3;
        }}
        .paper-meta {{
            color: #5f6368;
            font-size: 0.9em;
            margin-bottom: 15px;
            padding: 10px;
            background: white;
            border-radius: 5px;
        }}
        .meta-item {{
            margin: 5px 0;
        }}
        .paper-summary {{
            background: white;
            padding: 20px;
            border-radius: 5px;
            margin-top: 15px;
            white-space: pre-wrap;
        }}
        .summary-label {{
            color: #1a73e8;
            font-weight: bold;
            font-size: 1.05em;
            margin-bottom: 10px;
        }}
        .link-button {{
            display: inline-block;
            background: #1a73e8;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 15px;
            font-weight: 500;
        }}
        .link-button:hover {{
            background: #1557b0;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e8eaed;
            color: #5f6368;
            font-size: 0.9em;
        }}
        .badge {{
            display: inline-block;
            background: #ea4335;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            margin-left: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Daily AI Papers Digest</h1>
        <div class="header-info">
            📅 {today}{topic_text}<br>
            📚 {len(papers)} papers summarized by Gemini AI
        </div>
"""

    for i, paper in enumerate(papers, 1):
        published_date = datetime.fromisoformat(paper['published_date'].replace('Z', '+00:00'))
        formatted_date = published_date.strftime('%B %d, %Y')

        html += f"""
        <div class="paper">
            <div class="paper-number">📄 Paper #{i}</div>
            <div class="paper-title">{paper['title']}</div>

            <div class="paper-meta">
                <div class="meta-item">👥 <strong>Authors:</strong> {paper['authors'][:150]}{'...' if len(paper['authors']) > 150 else ''}</div>
                <div class="meta-item">📅 <strong>Published:</strong> {formatted_date}</div>
                <div class="meta-item">🌐 <strong>Source:</strong> {paper['source']}</div>
                {f'<div class="meta-item">⬆️ <strong>Upvotes:</strong> {paper["upvotes"]}</div>' if paper.get('upvotes', 0) > 0 else ''}
            </div>

            <div class="paper-summary">
                <div class="summary-label">🔍 AI Summary (Gemini)</div>
                {paper['summary'].replace(chr(10), '<br>')}
            </div>

            <a href="{paper['pdf_url']}" class="link-button">📥 Download PDF</a>
            <a href="https://arxiv.org/abs/{paper['arxiv_id']}" class="link-button" style="background: #34a853;">📖 View on arXiv</a>
        </div>
"""

    html += """
        <div class="footer">
            <p>🤖 Generated automatically by your AI Papers Fetcher</p>
            <p>Powered by Gemini AI | Papers from arXiv & Hugging Face</p>
        </div>
    </div>
</body>
</html>
"""
    return html


def send_email(
    recipient: str,
    sender: str,
    password: str,
    papers: List[Dict],
    topic: str = None
) -> bool:
    """
    Send email with paper summaries

    Args:
        recipient: Recipient email address
        sender: Sender Gmail address
        password: Gmail app password
        papers: List of papers with summaries
        topic: Optional topic filter

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        today = datetime.now().strftime('%B %d, %Y')
        topic_text = f" - {topic}" if topic else ""

        msg['Subject'] = f"🤖 AI Papers Digest - {today}{topic_text} ({len(papers)} papers)"
        msg['From'] = sender
        msg['To'] = recipient

        # Create HTML content
        html_content = format_html_email(papers, topic)
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        # Send email via Gmail SMTP
        print("Connecting to Gmail SMTP server...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)

        print(f"✅ Email sent successfully to {recipient}")
        return True

    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


if __name__ == "__main__":
    # Test email formatting
    from dotenv import load_dotenv
    import os

    load_dotenv()

    test_papers = [{
        'title': 'Test Paper: Attention Is All You Need',
        'authors': 'John Doe, Jane Smith',
        'abstract': 'Test abstract...',
        'arxiv_id': '1706.03762',
        'pdf_url': 'https://arxiv.org/pdf/1706.03762.pdf',
        'published_date': datetime.now().isoformat(),
        'upvotes': 42,
        'source': 'Test Source',
        'summary': 'Main Contribution:\nThis paper introduces the Transformer architecture.\n\nKey Findings:\n- Self-attention mechanisms\n- No recurrence needed\n- Better parallelization\n\nPotential Impact:\nRevolutionized NLP and led to models like GPT and BERT.'
    }]

    html = format_html_email(test_papers)
    print("HTML email generated successfully!")
    print(f"Length: {len(html)} characters")
