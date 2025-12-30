#!/bin/bash
# Check AI Papers Scheduler Status

echo "======================================"
echo "AI Papers Scheduler - Status Check"
echo "======================================"
echo ""

# Check if service is loaded
SERVICE_STATUS=$(launchctl list | grep aipapers)
if [ -n "$SERVICE_STATUS" ]; then
    echo "✅ Service Status: RUNNING"
    echo "   PID: $(echo $SERVICE_STATUS | awk '{print $1}')"
else
    echo "❌ Service Status: NOT RUNNING"
    exit 1
fi

echo ""

# Check process
PROCESS=$(ps aux | grep scheduler.py | grep -v grep)
if [ -n "$PROCESS" ]; then
    echo "✅ Process Running: YES"
    echo "   $(echo $PROCESS | awk '{print $11, $12}')"
else
    echo "❌ Process Running: NO"
fi

echo ""

# Check configuration
echo "📋 Configuration:"
cd /Users/othmanfairaq/my_code/python_ai_papers
source .env
echo "   Schedule: $SCHEDULE_TIME (Daily)"
echo "   Email: $RECIPIENT_EMAIL"
echo "   Papers: $NUM_PAPERS per day"
if [ -z "$TOPIC_FILTER" ]; then
    echo "   Topic: All trending AI papers"
else
    echo "   Topic: $TOPIC_FILTER"
fi

echo ""

# Check logs
echo "📝 Recent Logs:"
if [ -f scheduler.log ]; then
    echo "   Standard log: $(wc -l < scheduler.log) lines"
else
    echo "   Standard log: Not created yet (will appear at first run)"
fi

if [ -f scheduler_error.log ]; then
    ERROR_LINES=$(wc -l < scheduler_error.log)
    if [ "$ERROR_LINES" -gt 0 ]; then
        echo "   Error log: $ERROR_LINES lines (warnings only)"
    fi
fi

echo ""
echo "======================================"
echo "Next scheduled run: Today at $SCHEDULE_TIME"
echo "======================================"
echo ""
echo "Commands:"
echo "  Stop:  launchctl unload ~/Library/LaunchAgents/com.aipapers.scheduler.plist"
echo "  Logs:  tail -f /Users/othmanfairaq/my_code/python_ai_papers/scheduler.log"
echo "  Test:  cd /Users/othmanfairaq/my_code/python_ai_papers && source ai_papers_env/bin/activate && python main.py"
