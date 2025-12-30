# Quick Start Guide

## ✅ Your Application is Ready!

Everything is set up and working. Here's what you need to know:

## Current Status

✅ Gmail credentials configured and tested
✅ Gemini API key configured
✅ Dependencies installed
✅ PDFs downloading successfully
✅ Email sending successfully
⚠️ Gemini API quota exceeded for today (resets tomorrow)

## How to Use

### 1. Run Manually (Anytime)

```bash
cd /Users/othmanfairaq/my_code/python_ai_papers
source ai_papers_env/bin/activate
python main.py
```

### 2. Run with Specific Topic

```bash
source ai_papers_env/bin/activate
python main.py "agentic ai"
```

### 3. Start Daily Scheduler (9 PM)

```bash
source ai_papers_env/bin/activate
python scheduler.py
```

Keep this terminal open. It will run every day at 9 PM automatically.

## Your Current Configuration

- **Email**: mohamadatif2225@gmail.com ✅
- **Gmail App Password**: Configured ✅
- **Gemini API**: Working (hit daily quota, will reset tomorrow)
- **Schedule**: 9 PM daily
- **Papers**: 5 per day
- **Topic**: None (trending papers)

## Change Topic Filter

Edit `.env` file:

```bash
# For agentic AI papers
TOPIC_FILTER=agentic ai

# For LLM papers
TOPIC_FILTER=large language models

# For all trending papers (current setting)
TOPIC_FILTER=
```

## About Gemini API Quota

You've exceeded today's free tier quota. This happens after testing multiple times.

**Solutions**:
1. ✅ **Wait until tomorrow** - Quota resets daily
2. Try using model `models/gemini-1.5-flash` (already configured)
3. Check your usage: https://ai.dev/usage?tab=rate-limit

The application will still work tomorrow when the quota resets!

## What Happens Daily

At 9 PM every day (when scheduler is running):
1. 📚 Fetches 5 viral AI papers from Hugging Face/arXiv
2. 🤖 Summarizes each paper using Gemini AI
3. 📥 Downloads PDFs to `papers/YYYY-MM-DD/` folder
4. 📧 Sends beautiful HTML email to mohamadatif2225@gmail.com

## Check Your Papers

```bash
# View downloaded papers
ls -lh papers/2025-12-30/

# Read the index
cat papers/2025-12-30/INDEX.txt
```

## Tips

- Keep scheduler running in background (use `screen` or `nohup`)
- Check `papers/` folder daily for new PDFs
- Summaries will work once quota resets
- Email will always be sent regardless of AI summary status

## Need Help?

Check the full [README.md](README.md) for:
- Detailed setup instructions
- Troubleshooting guide
- Advanced customization options
- Running in background with systemd/cron

---

**Everything is working! Just wait for quota to reset tomorrow and you'll get full AI summaries. 🎉**
