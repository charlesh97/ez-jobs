#!/usr/bin/env python3
"""
Test Discord notifications with sample job data
"""

import os
import json
# Import the scraper class from the main module
import importlib.util
spec = importlib.util.spec_from_file_location("ez_apply", "ez-apply.py")
ez_apply = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ez_apply)
OpenAICareersScraper = ez_apply.OpenAICareersScraper
JobPosting = ez_apply.JobPosting

def test_discord_notification():
    """Test Discord notification with a sample job"""
    
    # Check if Discord webhook is configured
    discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
    
    if not discord_webhook:
        print("❌ DISCORD_WEBHOOK_URL not set")
        print("To test Discord notifications:")
        print("1. Set up a Discord webhook")
        print("2. Run: export DISCORD_WEBHOOK_URL='your_webhook_url'")
        print("3. Run this script again")
        return False
    
    # Create a sample job
    sample_job = JobPosting(
        title="Electrical Engineer - Test",
        applyLink="https://jobs.ashbyhq.com/openai/test-job-001",
        careerLink="https://openai.com/careers/test-job-001"
    )
    
    # Create scraper instance
    scraper = OpenAICareersScraper(discord_webhook_url=discord_webhook)
    
    print("🔔 Testing Discord notification...")
    print(f"Job: {sample_job.title}")
    print(f"Apply Link: {sample_job.applyLink}")
    print(f"Career Link: {sample_job.careerLink}")
    
    # Send notification
    scraper.send_discord_notification(sample_job)
    
    print("✅ Discord notification test completed!")
    print("Check your Discord channel for the test message.")
    
    return True

if __name__ == "__main__":
    test_discord_notification()
