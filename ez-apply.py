#!/usr/bin/env python3
"""
OpenAI Careers Job Scraper
Monitors OpenAI careers website for electrical engineering positions
and sends Discord notifications for new job postings.
"""

import requests
import pickle
import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Set
import logging
from dataclasses import dataclass
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import sys
# Import configuration
try:
    from config import *
except ImportError:
    # Fallback configuration if config.py doesn't exist
    TARGET_KEYWORDS = [
        'electrical',
        'hardware',
        'EE',
        'circuit',
        'robotics',
    ]
    REQUEST_TIMEOUT = 30
    MAX_DESCRIPTION_LENGTH = 200
    LOG_LEVEL = "INFO"
    LOG_FILE = "job_scraper.log"
    DATA_FILE = "known_jobs.pkl"
    OPENAI_CAREERS_URL = "https://openai.com/api/jobs"
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)  # Explicitly use stdout
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class JobPosting:
    """Data class for job posting information"""
    title: str
    applyLink: str
    careerLink: str

class OpenAICareersScraper:
    """Scraper for OpenAI careers website"""
    
    def __init__(self, discord_webhook_url: str = None):
        self.base_url = OPENAI_CAREERS_URL
        self.discord_webhook_url = discord_webhook_url
        self.data_file = DATA_FILE
        self.known_job_titles: Set[str] = set()
        self.load_known_jobs()
        
        # Keywords for electrical engineering positions
        self.target_keywords = TARGET_KEYWORDS
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def load_known_jobs(self):
        """Load previously seen job IDs from pickle file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'rb') as f:
                    self.known_job_titles = pickle.load(f)
                logger.info(f"Loaded {len(self.known_job_titles)} known job IDs")
            else:
                logger.info("No existing job data found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading known jobs: {e}")
            self.known_job_titles = set()

    def save_known_jobs(self):
        """Save known job IDs to pickle file"""
        try:
            with open(self.data_file, 'wb') as f:
                pickle.dump(self.known_job_titles, f)
            logger.info(f"Saved {len(self.known_job_titles)} job IDs to {self.data_file}")
        except Exception as e:
            logger.error(f"Error saving known jobs: {e}")

    def fetch_jobs(self) -> List[Dict]:
        """Fetch all jobs from OpenAI careers search page using Selenium"""
        try:
            logger.info("Fetching jobs from OpenAI careers search page...")
            
            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"--user-agent={USER_AGENT}")
            
            driver = None
            try:
                # Initialize the Chrome driver
                logger.info("Initializing Chrome driver...")
                driver = webdriver.Chrome(options=chrome_options)
                
                # Navigate to the careers page
                careers_url = "https://openai.com/careers/search/"
                logger.info(f"Navigating to {careers_url}")
                driver.get(careers_url)
                
                # Wait for the page to load
                time.sleep(5)
                
                # Get the page source
                page_source = driver.page_source
                
                # Look for the embedded JSON data
                # The jobs data is embedded in a script tag with window.__NEXT_DATA__
                import re
                
                # Extract jobs using href patterns
                # Look for career links: href="/careers/..." -> job title
                # Look for apply links: href="https://jobs..." -> job application link
                
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(page_source, 'html.parser')
                
                jobs = []
                
                # Find all links with href="/careers/..."
                career_links = soup.find_all('a', href=lambda x: x and x.startswith('/careers/'))
                
                for career_link in career_links:
                    job_title = career_link.get_text(strip=True)
                    career_href = career_link.get('href')
                    
                    if job_title and career_href:
                        # Look for corresponding application link
                        # Try to find a nearby link with href="https://jobs..."
                        apply_link = None
                        
                        # Look in the same parent container for the apply link
                        parent = career_link.parent
                        if parent:
                            apply_links = parent.find_all('a', href=lambda x: x and x.startswith('https://jobs.'))
                            if apply_links:
                                apply_link = apply_links[0].get('href')
                        
                        # If not found in parent, search more broadly
                        if not apply_link:
                            # Look for apply links that might be related
                            all_apply_links = soup.find_all('a', href=lambda x: x and x.startswith('https://jobs.'))
                            # For now, we'll use the career link as the apply link if we can't find a specific one
                            apply_link = f"https://openai.com{career_href}"
                        
                        job_data = {
                            "title": job_title,
                            "applyLink": apply_link,
                            "careerLink": f"https://openai.com{career_href}"
                        }
                        jobs.append(job_data)
                
                if jobs:
                    logger.info(f"Successfully extracted {len(jobs)} jobs using href patterns")
                    return jobs
                
                # If the above pattern didn't work, try a more flexible approach
                # Look for any JSON-like structure containing job data
                json_pattern = r'window\.__NEXT_DATA__\s*=\s*({.*?});'
                match = re.search(json_pattern, page_source, re.DOTALL)
                
                if match:
                    json_str = match.group(1)
                    try:
                        data = json.loads(json_str)
                        
                        # Navigate through the JSON structure to find jobs
                        jobs = []
                        
                        # Try different possible paths for jobs data
                        possible_paths = [
                            ['props', 'pageProps', 'jobs'],
                            ['props', 'pageProps', 'data', 'jobs'],
                            ['props', 'pageProps', 'initialData', 'jobs'],
                            ['props', 'pageProps', 'jobsData'],
                            ['props', 'pageProps', 'data']
                        ]
                        
                        for path in possible_paths:
                            current = data
                            try:
                                for key in path:
                                    current = current[key]
                                if isinstance(current, list) and len(current) > 0:
                                    jobs = current
                                    logger.info(f"Found {len(jobs)} jobs using path: {path}")
                                    break
                            except (KeyError, TypeError):
                                continue
                        
                        if not jobs:
                            # If we can't find jobs in the expected structure, 
                            # let's look for any array that contains job-like objects
                            def find_jobs_recursive(obj, depth=0):
                                if depth > 5:  # Prevent infinite recursion
                                    return None
                                
                                if isinstance(obj, list) and len(obj) > 0:
                                    # Check if this looks like a jobs array
                                    first_item = obj[0]
                                    if isinstance(first_item, dict):
                                        # Look for job-like fields
                                        job_fields = ['title', 'applyLink', 'careerLink']
                                        if any(field in first_item for field in job_fields):
                                            return obj
                                
                                if isinstance(obj, dict):
                                    for key, value in obj.items():
                                        result = find_jobs_recursive(value, depth + 1)
                                        if result:
                                            return result
                                
                                return None
                            
                            jobs = find_jobs_recursive(data) or []
                            
                            if jobs:
                                logger.info(f"Found {len(jobs)} jobs using recursive search")
                        
                        if jobs:
                            logger.info(f"Successfully extracted {len(jobs)} jobs from careers page")
                            return jobs
                        else:
                            logger.warning("No jobs found in the page data")
                            return []
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON data: {e}")
                        return []
                
                logger.warning("Could not find job data in the page")
                return []
                    
            except WebDriverException as e:
                logger.error(f"WebDriver error: {e}")
                return []
            except Exception as e:
                logger.error(f"Unexpected error during Selenium scraping: {e}")
                return []
            finally:
                if driver:
                    driver.quit()
                    
        except Exception as e:
            logger.error(f"Error fetching jobs: {e}")
            return []





    def is_relevant_job(self, job: Dict) -> bool:
        """Check if job is relevant for electrical engineering"""
        title = job.get('title', '').lower()
        
        # First check if any avoid keyword is in the title (if so, reject immediately)
        for avoid_keyword in AVOID_KEYWORDS:
            if avoid_keyword.lower() in title:
                logger.debug(f"Job '{job.get('title', '')}' rejected due to avoid keyword: '{avoid_keyword}'")
                return False
        
        # Then check if any target keyword is in the title
        for keyword in self.target_keywords:
            if keyword in title:
                logger.debug(f"Job '{job.get('title', '')}' accepted due to target keyword: '{keyword}'")
                return True
        
        return False

    def parse_job(self, job_data: Dict) -> JobPosting:
        """Parse job data into JobPosting object"""
        return JobPosting(
            title=job_data.get('title', ''),
            applyLink=job_data.get('applyLink', ''),
            careerLink=job_data.get('careerLink', '')
        )

    def send_discord_notification(self, job: JobPosting):
        """Send Discord notification for new job posting"""
        if not self.discord_webhook_url:
            logger.warning("No Discord webhook URL configured, skipping notification")
            return

        embed = {
            "title": f"🔌 New Job at OpenAI!",
            "description": f"**{job.title}**",
            "url": job.careerLink,
            "color": 0x00ff00,  # Green color
            "fields": [
                {
                    "name": "🔗 Apply Now",
                    "value": f"[Click here to apply]({job.applyLink})",
                    "inline": False
                }
            ],
            "timestamp": datetime.utcnow().isoformat()
        }

        payload = {
            "embeds": [embed],
            "username": "OpenAI Job Bot",
        }

        try:
            response = requests.post(
                self.discord_webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Discord notification sent for job: {job.title}")
        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")

    def scrape_and_notify(self):
        """Main scraping function"""
        logger.info("Starting job scraping process...")
        
        # Fetch all jobs
        all_jobs = self.fetch_jobs()
        if not all_jobs:
            logger.error("No jobs fetched, aborting")
            return

        # Filter for relevant jobs
        relevant_jobs = [job for job in all_jobs if self.is_relevant_job(job)]
        logger.info(f"Found {len(relevant_jobs)} relevant electrical engineering jobs")

        # Check for new jobs
        new_jobs = []
        for job_data in relevant_jobs:
            job_title = job_data.get('title', '')
            if job_title not in self.known_job_titles:
                job = self.parse_job(job_data)
                new_jobs.append(job)
                self.known_job_titles.add(job_title)
                logger.info(f"New job found: {job.title}")
            else:
                logger.info(f"Job already seen: {job_title}")

        # Send notifications for new jobs
        if new_jobs:
            logger.info(f"Sending notifications for {len(new_jobs)} new jobs")
            for job in new_jobs:
                self.send_discord_notification(job)
        else:
            logger.info("No new jobs found")
            # Send a Discord notification that no ew jobs were found
            if self.discord_webhook_url:
                payload = {
                    "embeds": [{
                        "title": "No New Jobs",
                        "description": "No new relevant job postings were found in the latest scan.",
                        "color": 0x808080,
                        "timestamp": datetime.utcnow().isoformat(),
                        "footer": {
                            "text": "OpenAI Careers Job Scraper"
                        }
                    }],
                    "username": "OpenAI Job Bot",
                }
                try:
                    response = requests.post(
                        self.discord_webhook_url,
                        json=payload,
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                    response.raise_for_status()
                    logger.info("Discord notification sent: No new jobs found")
                except Exception as e:
                    logger.error(f"Error sending Discord notification for no new jobs: {e}")

        # Save updated job IDs
        self.save_known_jobs()
        logger.info("Job scraping process completed")

def main():
    """Main function to run the scraper"""
    # Get Discord webhook URL from environment or config
    discord_webhook = os.getenv('DISCORD_WEBHOOK_URL') or DISCORD_WEBHOOK_URL
    
    if not discord_webhook:
        logger.warning("DISCORD_WEBHOOK_URL not set. Notifications will be skipped.")
        logger.info("To set up Discord notifications:")
        logger.info("1. Go to your Discord server settings")
        logger.info("2. Navigate to Integrations > Webhooks")
        logger.info("3. Create a new webhook and copy the URL")
        logger.info("4. Set the DISCORD_WEBHOOK_URL environment variable or update config.py")
    
    scraper = OpenAICareersScraper(discord_webhook_url=discord_webhook)
    scraper.scrape_and_notify()

if __name__ == "__main__":
    main()
