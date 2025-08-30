#!/usr/bin/env python3
"""
Daily RSS Scheduler for mytribal.ai
Runs daily RSS automation to check for new content
"""

import schedule
import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_rss_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_daily_rss_automation():
    """Run the daily RSS automation script"""
    try:
        logger.info("🚀 Starting scheduled daily RSS automation...")
        
        # Run the daily RSS automation script
        result = subprocess.run(
            ['python3', 'mytribal_rss_daily.py'],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        if result.returncode == 0:
            logger.info("✅ Daily RSS automation completed successfully")
            # Log the output for debugging
            if result.stdout:
                logger.info(f"Output: {result.stdout}")
        else:
            logger.error(f"❌ Daily RSS automation failed with return code {result.returncode}")
            if result.stderr:
                logger.error(f"Error: {result.stderr}")
            
    except Exception as e:
        logger.error(f"❌ Error running daily RSS automation: {e}")

def run_immediate_check():
    """Run an immediate RSS check"""
    logger.info("🔄 Running immediate RSS check...")
    run_daily_rss_automation()

def main():
    """Main daily scheduler function"""
    logger.info("📅 Starting Daily RSS Scheduler for mytribal.ai...")
    
    # Schedule daily RSS automation
    # Run at 9:00 AM every day
    schedule.every().day.at("09:00").do(run_daily_rss_automation)
    
    # Also run at 3:00 PM for afternoon check
    schedule.every().day.at("15:00").do(run_daily_rss_automation)
    
    # Run it once immediately to check current status
    logger.info("🔄 Running immediate RSS check...")
    run_immediate_check()
    
    logger.info("⏰ Daily RSS Scheduler is running with the following schedule:")
    logger.info("   - 9:00 AM: Morning RSS check")
    logger.info("   - 3:00 PM: Afternoon RSS check")
    logger.info("   - Immediate check completed")
    logger.info("Press Ctrl+C to stop the scheduler.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logger.info("🛑 Daily RSS Scheduler stopped by user")
    except Exception as e:
        logger.error(f"❌ Scheduler error: {e}")

if __name__ == "__main__":
    main()
