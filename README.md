# AI Papers Daily Digest 🤖📚

Automatically fetch the most viral AI research papers daily, summarize them using Google Gemini AI, download PDFs, and receive a beautiful email digest - all running in the background!

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## ✨ Features

- 📚 **Auto-fetch** trending AI papers from Hugging Face & arXiv
- 🤖 **AI Summaries** using Google Gemini 2.5 Flash
- 📥 **PDF Downloads** organized by date in local folders
- 📧 **Beautiful HTML Emails** with paper summaries and links
- 🎯 **Topic Filtering** (e.g., "agentic ai", "LLMs", "computer vision")
- ⏰ **Scheduled Execution** - runs automatically daily
- 🔄 **Auto-restart** capability (survives system reboots)
- 📱 **Email Delivery** - receive papers directly in your inbox

## 📸 What You'll Receive

Every day, you'll get:
- ✅ Email with 5 viral AI papers (customizable)
- ✅ AI-generated summaries with key findings and impact
- ✅ Direct links to full papers on arXiv
- ✅ PDFs downloaded to organized `papers/YYYY-MM-DD/` folders
- ✅ Comprehensive INDEX.txt file with all paper details

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Gmail account (for sending emails)
- Google Gemini API key ([Get free API key](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ai-papers-digest.git
cd ai-papers-digest
```

2. **Create virtual environment**
```bash
python3 -m venv ai_papers_env
source ai_papers_env/bin/activate  # On Windows: ai_papers_env\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
nano .env  # Edit with your credentials
```

Required credentials:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `RECIPIENT_EMAIL`: Email where you'll receive papers
- `SENDER_EMAIL`: Your Gmail address
- `GMAIL_APP_PASSWORD`: Gmail App Password ([How to generate](https://support.google.com/accounts/answer/185833))

5. **Test the application**
```bash
python main.py
```

You should receive an email and see PDFs downloaded!

## 📖 Usage

### Manual Execution

```bash
# Fetch trending AI papers
python main.py

# Search for specific topic
python main.py "agentic ai"
python main.py "large language models"
python main.py "computer vision"
```

### Scheduled Execution (Automatic Daily)

```bash
# Start scheduler (runs daily at configured time)
python scheduler.py
```

Keep this running in the background, or use one of the auto-start methods below.

## 🔧 Configuration

Edit `.env` to customize:

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Your Google Gemini API key | Required |
| `RECIPIENT_EMAIL` | Email to receive digest | Required |
| `SENDER_EMAIL` | Gmail account for sending | Required |
| `GMAIL_APP_PASSWORD` | Gmail app password | Required |
| `SCHEDULE_TIME` | Daily run time (24h format) | `21:00` (9 PM) |
| `NUM_PAPERS` | Number of papers to fetch | `5` |
| `TOPIC_FILTER` | Topic to search for | Empty (trending) |

## 🤖 Running in Background

### Option 1: Using `nohup` (Linux/Mac)

```bash
nohup python scheduler.py > scheduler.log 2>&1 &
```

**Stop:**
```bash
ps aux | grep scheduler.py  # Find PID
kill <PID>
```

### Option 2: Using `systemd` (Linux)

Create `/etc/systemd/system/ai-papers.service`:

```ini
[Unit]
Description=AI Papers Daily Digest
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/ai-papers-digest
ExecStart=/path/to/ai_papers_env/bin/python scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ai-papers
sudo systemctl start ai-papers
sudo systemctl status ai-papers
```

### Option 3: Using `launchd` (macOS)

See [INSTALL_SERVICE.md](INSTALL_SERVICE.md) for detailed macOS setup instructions.

### Option 4: Using `cron`

```bash
crontab -e
```

Add (runs at 9 PM daily):
```
0 21 * * * cd /path/to/ai-papers-digest && /path/to/ai_papers_env/bin/python main.py >> cron.log 2>&1
```

## 📁 Project Structure

```
ai-papers-digest/
├── main.py              # Main application orchestrator
├── scheduler.py         # Daily scheduler
├── fetch_papers.py      # Fetch papers from arXiv/Hugging Face
├── summarizer.py        # Gemini AI summarization
├── email_sender.py      # Email formatting and sending
├── download_pdfs.py     # PDF downloader
├── requirements.txt     # Python dependencies
├── .env.example         # Configuration template
├── .gitignore          # Git ignore file
├── README.md           # This file
└── papers/             # Downloaded PDFs (auto-created)
    └── YYYY-MM-DD/     # Daily folders
        ├── INDEX.txt   # Papers index
        └── *.pdf       # Downloaded papers
```

## 🎨 Email Preview

The HTML email includes:
- Paper titles and authors
- Publication dates and sources
- AI-generated summaries with:
  - Main contributions
  - Key findings (bullet points)
  - Potential impact
- Direct links to PDFs and arXiv pages
- Beautiful, responsive design

## 🔍 Advanced Usage

### Filter by Specific Topics

Edit `.env`:
```bash
# For agentic AI papers
TOPIC_FILTER=agentic ai

# For LLM papers
TOPIC_FILTER=large language models

# For computer vision papers
TOPIC_FILTER=computer vision

# For all trending papers
TOPIC_FILTER=
```

### Change Paper Sources

Edit `fetch_papers.py` to add more sources like Papers with Code, semantic scholar, etc.

### Customize Email Template

Modify `format_html_email()` in `email_sender.py` to change the email design.

### Use Different AI Models

Edit `summarizer.py` to use:
- `models/gemini-1.5-flash` (faster)
- `models/gemini-1.5-pro` (more accurate)
- Or integrate OpenAI, Anthropic, etc.

## 🐛 Troubleshooting

### Email not sending
- Verify Gmail App Password (not regular password)
- Ensure 2FA is enabled on Google account
- Check spam folder

### Gemini API errors
- Verify API key is correct
- Check quota at [AI Studio](https://aistudio.google.com/)
- Free tier has daily limits (resets daily)

### PDFs not downloading
- Check internet connection
- Verify write permissions on `papers/` folder
- Some papers may have restricted access

### Scheduler not running
- Ensure Python path is correct in service config
- Check logs for errors
- Verify schedule time format (24-hour)

## 💰 Cost Estimation

### Google Gemini API
- **Free tier**: 60 requests/minute, 1500 requests/day
- 5 papers daily = 5 API calls
- **Cost**: FREE (within limits)

### Gmail
- **Cost**: FREE

### Total Monthly Cost
- **$0** (using free tiers)

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest new features
- 🔧 Submit pull requests
- 📖 Improve documentation

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Hugging Face](https://huggingface.co/) for daily papers API
- [arXiv](https://arxiv.org/) for research papers
- [Google Gemini](https://ai.google.dev/) for AI summarization
- The open-source community

## ⭐ Star History

If you find this project useful, please consider giving it a star!

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Made with ❤️ for AI researchers and enthusiasts**
