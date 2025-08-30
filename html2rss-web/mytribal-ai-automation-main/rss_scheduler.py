#!/usr/bin/env python3
"""
RSS Scheduler for mytribal.ai
Runs RSS automation at regular intervals
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
        logging.FileHandler('rss_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_rss_automation():
    """Run the RSS automation script"""
    try:
        logger.info("🚀 Starting scheduled RSS automation...")
        
        # Run the RSS automation script
        result = subprocess.run(
            ['python3', 'mytribal_rss_production.py'],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        if result.returncode == 0:
            logger.info("✅ RSS automation completed successfully")
            logger.info(f"Output: {result.stdout}")
        else:
            logger.error(f"❌ RSS automation failed with return code {result.returncode}")
            logger.error(f"Error: {result.stderr}")
            
    except Exception as e:
        logger.error(f"❌ Error running RSS automation: {e}")

def main():
    """Main scheduler function"""
    logger.info("📅 Starting RSS Scheduler for mytribal.ai...")
    
    # Schedule RSS automation to run every 6 hours
    schedule.every(6).hours.do(run_rss_automation)
    
    # Also run it once immediately
    logger.info("🔄 Running initial RSS automation...")
    run_rss_automation()
    
    logger.info("⏰ RSS Scheduler is running. RSS automation will run every 6 hours.")
    logger.info("Press Ctrl+C to stop the scheduler.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logger.info("🛑 RSS Scheduler stopped by user")
    except Exception as e:
        logger.error(f"❌ Scheduler error: {e}")

if __name__ == "__main__":
    main()
