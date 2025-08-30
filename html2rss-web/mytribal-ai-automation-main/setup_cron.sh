#!/bin/bash

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)

# Create the cron job command
CRON_COMMAND="0 9 * * * cd $PROJECT_DIR && $PYTHON_PATH main.py >> $PROJECT_DIR/automation.log 2>&1"

echo "Setting up daily automation at 9:00 AM..."
echo "Project directory: $PROJECT_DIR"
echo "Python path: $PYTHON_PATH"
echo ""

# Add the cron job
(crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -

echo "Cron job added successfully!"
echo "The automation will run daily at 9:00 AM"
echo "Logs will be saved to: $PROJECT_DIR/automation.log"
echo ""
echo "To view current cron jobs: crontab -l"
echo "To edit cron jobs: crontab -e"
echo "To remove all cron jobs: crontab -r"
