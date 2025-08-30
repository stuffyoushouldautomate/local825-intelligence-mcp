#!/usr/bin/env python3
"""
Daily Automation Scheduler
Runs the main automation workflow every day at 9:00 AM
"""

import schedule
import time
import subprocess
import sys
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_automation():
    """Run the main automation workflow"""
    try:
        logging.info("Starting daily automation...")
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        main_script = os.path.join(script_dir, 'main.py')
        
        # Run the main automation script
        result = subprocess.run([sys.executable, main_script], 
                              capture_output=True, text=True, cwd=script_dir)
        
        if result.returncode == 0:
            logging.info("Automation completed successfully!")
            if result.stdout:
                logging.info(f"Output: {result.stdout}")
        else:
            logging.error(f"Automation failed with return code {result.returncode}")
            if result.stderr:
                logging.error(f"Error: {result.stderr}")
                
    except Exception as e:
        logging.error(f"Error running automation: {e}")

def main():
    """Main scheduler function"""
    logging.info("Starting automation scheduler...")
    
    # Schedule the automation to run daily at 9:00 AM
    schedule.every().day.at("09:00").do(run_automation)
    
    # Also run once immediately for testing
    logging.info("Running initial automation for testing...")
    run_automation()
    
    logging.info("Scheduler running. Automation will execute daily at 9:00 AM")
    logging.info("Press Ctrl+C to stop the scheduler")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()

