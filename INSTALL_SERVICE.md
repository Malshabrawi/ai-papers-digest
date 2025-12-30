# How to Make AI Papers Run Automatically (Even After Restart)

## Option 1: Simple - Run Only When Laptop is On

```bash
cd /Users/othmanfairaq/my_code/python_ai_papers
source ai_papers_env/bin/activate
python scheduler.py
```

**To stop**: Press `Ctrl+C`

---

## Option 2: Background - Survives Terminal Close

```bash
cd /Users/othmanfairaq/my_code/python_ai_papers
source ai_papers_env/bin/activate
nohup python scheduler.py > scheduler.log 2>&1 &
```

**To check if running**:
```bash
ps aux | grep scheduler.py
```

**To stop**:
```bash
# Find the process
ps aux | grep scheduler.py

# Kill it (replace 12345 with actual PID from above)
kill 12345
```

**To see logs**:
```bash
tail -f scheduler.log
```

---

## Option 3: Auto-Start Service (BEST - Survives Restarts!)

### Install the Service

```bash
# Copy the plist file to LaunchAgents
cp /Users/othmanfairaq/my_code/python_ai_papers/com.aipapers.scheduler.plist ~/Library/LaunchAgents/

# Load the service (start it)
launchctl load ~/Library/LaunchAgents/com.aipapers.scheduler.plist
```

### Check if Running

```bash
launchctl list | grep aipapers
```

If you see output, it's running!

### View Logs

```bash
# Standard output
tail -f /Users/othmanfairaq/my_code/python_ai_papers/scheduler.log

# Errors (if any)
tail -f /Users/othmanfairaq/my_code/python_ai_papers/scheduler_error.log
```

### Stop the Service

```bash
launchctl unload ~/Library/LaunchAgents/com.aipapers.scheduler.plist
```

### Start Again

```bash
launchctl load ~/Library/LaunchAgents/com.aipapers.scheduler.plist
```

### Remove Completely

```bash
# Stop it first
launchctl unload ~/Library/LaunchAgents/com.aipapers.scheduler.plist

# Remove the file
rm ~/Library/LaunchAgents/com.aipapers.scheduler.plist
```

---

## What Each Option Does

| Option | Survives Terminal Close? | Survives Laptop Restart? | Easy to Setup? |
|--------|-------------------------|-------------------------|----------------|
| Option 1 | ❌ No | ❌ No | ✅ Very Easy |
| Option 2 | ✅ Yes | ❌ No | ✅ Easy |
| Option 3 | ✅ Yes | ✅ **YES** | ⚠️ Medium |

---

## Recommendation

**For most users**: Use **Option 3** (launchd service)

Why?
- ✅ Automatically starts when Mac boots
- ✅ Keeps running in background
- ✅ No need to remember to start it
- ✅ Runs even if you close all terminals

**When laptop shuts down**:
- Option 1 & 2: ❌ Script stops, won't run at 9 PM
- Option 3: ✅ Script auto-restarts when Mac boots, runs at 9 PM

---

## Quick Start (Recommended)

```bash
# Install as service (Option 3)
cp /Users/othmanfairaq/my_code/python_ai_papers/com.aipapers.scheduler.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.aipapers.scheduler.plist

# Verify it's running
launchctl list | grep aipapers

# Check logs
tail -f /Users/othmanfairaq/my_code/python_ai_papers/scheduler.log
```

Done! It will now run every day at 9 PM automatically, even after restarts.

---

## Troubleshooting

**Service not starting?**
```bash
# Check for errors
cat /Users/othmanfairaq/my_code/python_ai_papers/scheduler_error.log

# Restart the service
launchctl unload ~/Library/LaunchAgents/com.aipapers.scheduler.plist
launchctl load ~/Library/LaunchAgents/com.aipapers.scheduler.plist
```

**Want to test without waiting until 9 PM?**
```bash
# Stop the service temporarily
launchctl unload ~/Library/LaunchAgents/com.aipapers.scheduler.plist

# Run manually to test
cd /Users/othmanfairaq/my_code/python_ai_papers
source ai_papers_env/bin/activate
python main.py

# Start service again
launchctl load ~/Library/LaunchAgents/com.aipapers.scheduler.plist
```
