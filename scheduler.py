#!/usr/bin/env python3
"""
Daily Job Scraper Scheduler
Runs the OpenAI careers scraper once per day at a specified time.
"""

import schedule
import time
import logging
from datetime import datetime
import subprocess
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_scraper():
    """Run the job scraper"""
    try:
        logger.info("Starting scheduled job scraper run...")
        
        # Run the scraper script with real-time output
        logger.info("Starting scraper subprocess...")
        process = subprocess.Popen(
            [sys.executable, 'ez-apply.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Read output in real-time
        try:
            for line in process.stdout:
                logger.info(f"SCRAPER: {line.strip()}")
            
            process.wait(timeout=300)  # 5 minute timeout
            
            if process.returncode == 0:
                logger.info("Job scraper completed successfully")
            else:
                logger.error(f"Job scraper failed with return code {process.returncode}")
                
        except subprocess.TimeoutExpired:
            process.kill()
            logger.error("Job scraper timed out after 5 minutes")
                
    except subprocess.TimeoutExpired:
        logger.error("Job scraper timed out after 5 minutes")
    except Exception as e:
        logger.error(f"Error running job scraper: {e}")

def main():
    """Main scheduler function"""
    logger.info("Starting job scraper scheduler...")
    
    # Import configuration
    try:
        from config import SCHEDULE_TIME
    except ImportError:
        SCHEDULE_TIME = "13:00"
    
    # Schedule the job to run daily at the configured time
    schedule.every().day.at(SCHEDULE_TIME).do(run_scraper)
    
    # Also run once immediately on startup
    logger.info("Running initial scraper check...")
    run_scraper()
    
    logger.info("Scheduler running. Press Ctrl+C to stop.")
    logger.info(f"Next scheduled run: {SCHEDULE_TIME} daily")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")

if __name__ == "__main__":
    main()
