#!/usr/bin/env python3
"""
Configuration file for the OpenAI Careers Job Scraper
Modify these settings to customize the scraper behavior.
"""

# Discord Configuration
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1403126483786006611/WwPtj093M8bN9jtqYa7DjIEdTQiqJ5kAE8eNPgz8w4_G36MGtrp6sYy01gCKC-IQjVeI'  # Set via environment variable DISCORD_WEBHOOK_URL

# Job Keywords to Monitor (must contain at least one of these)
TARGET_KEYWORDS = [
        'electrical',
        'hardware',
        'EE',
        'circuit',
        'robotics',
        'system software',
        'machine learning',
        'ML',
]

# Keywords to Avoid (job will be filtered out if it contains any of these)
AVOID_KEYWORDS = [
        'site',
        'data center',
        'firmware',
        'simulation',
]

# Scheduling Configuration
SCHEDULE_TIME = "13:00"  # Daily run time (24-hour format)
SCHEDULE_TIMEZONE = "PST"  # Timezone for scheduling

# Scraper Configuration
REQUEST_TIMEOUT = 30  # Seconds
MAX_DESCRIPTION_LENGTH = 200  # Characters to include in Discord message

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "job_scraper.log"

# File Paths
DATA_FILE = "known_jobs.pkl"  # Pickle file for storing known job IDs

# OpenAI Careers API
OPENAI_CAREERS_URL = "https://openai.com/careers/search/"

# User Agent for requests
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
