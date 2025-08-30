# Daily Automation Setup Guide

This guide shows you how to automate your AI content generation workflow to run daily.

## Option 1: Cron Job (Recommended for macOS/Linux)

### Quick Setup
1. Make the setup script executable:
   ```bash
   chmod +x setup_cron.sh
   ```

2. Run the setup script:
   ```bash
   ./setup_cron.sh
   ```

This will automatically create a cron job that runs your automation daily at 9:00 AM.

### Manual Cron Setup
If you prefer to set it up manually:

1. Open your crontab:
   ```bash
   crontab -e
   ```

2. Add this line (adjust the path to match your project location):
   ```bash
   0 9 * * * cd /Users/keymuth/mytribal-ai-automation && python3 main.py >> automation.log 2>&1
   ```

3. Save and exit (Ctrl+X in nano, or :wq in vim)

## Option 2: Python Scheduler

### Setup
1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the scheduler:
   ```bash
   python3 scheduler.py
   ```

The scheduler will:
- Run your automation immediately for testing
- Schedule it to run daily at 9:00 AM
- Keep running in the background
- Log all activities to `scheduler.log`

### Keep Scheduler Running
To keep the scheduler running after you close your terminal:

1. Use `nohup`:
   ```bash
   nohup python3 scheduler.py > scheduler_output.log 2>&1 &
   ```

2. Or use `screen`:
   ```bash
   screen -S automation
   python3 scheduler.py
   # Press Ctrl+A, then D to detach
   # Use 'screen -r automation' to reattach
   ```

## Option 3: macOS LaunchAgent

### Setup
1. Copy the plist file to LaunchAgents:
   ```bash
   cp com.mytribal.automation.plist ~/Library/LaunchAgents/
   ```

2. Load the agent:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.mytribal.automation.plist
   ```

3. Start the agent:
   ```bash
   launchctl start com.mytribal.automation
   ```

### Management
- Check status: `launchctl list | grep mytribal`
- Stop: `launchctl stop com.mytribal.automation`
- Unload: `launchctl unload ~/Library/LaunchAgents/com.mytribal.automation.plist`

## Testing Your Automation

Before setting up daily automation, test it manually:

```bash
python3 main.py
```

Check that:
- Reddit posts are fetched
- Articles are generated
- Images are created
- Content is saved to Notion
- Posts are published to WordPress

## Monitoring

### Logs
- **Cron/LaunchAgent**: Check `automation.log` and `automation_error.log`
- **Python Scheduler**: Check `scheduler.log`

### Check Status
- **Cron**: `crontab -l`
- **LaunchAgent**: `launchctl list | grep mytribal`
- **Python Scheduler**: Check if the process is running

## Troubleshooting

### Common Issues
1. **Permission denied**: Make sure scripts are executable (`chmod +x`)
2. **Path issues**: Verify all paths in the automation scripts
3. **Environment variables**: Ensure `.env` file is accessible
4. **Python path**: Verify `python3` is in your PATH

### Debug Mode
Add logging to your main.py for better debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Recommendation

For your use case, I recommend **Option 1 (Cron Job)** because:
- It's the most reliable and standard approach
- It runs independently of your user session
- It's easy to manage and debug
- It's built into macOS

The cron job will run your automation every day at 9:00 AM, even when you're not logged in (as long as your Mac is running).

