#!/usr/bin/env python3
"""
Test script for the OpenAI Careers Job Scraper
Runs the scraper in test mode without sending Discord notifications.
"""

import os
import sys
# Import the scraper class from the main module
import importlib.util
spec = importlib.util.spec_from_file_location("ez_apply", "ez-apply.py")
ez_apply = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ez_apply)
OpenAICareersScraper = ez_apply.OpenAICareersScraper

def test_scraper():
    """Test the scraper functionality"""
    print("🧪 Testing OpenAI Careers Job Scraper...")
    print("=" * 50)
    
    # Create scraper without Discord webhook for testing
    scraper = OpenAICareersScraper(discord_webhook_url=None)
    
    # Test job fetching
    print("📡 Fetching jobs from OpenAI careers...")
    jobs = scraper.fetch_jobs()
    
    if not jobs:
        print("❌ Failed to fetch jobs")
        return False
    
    print(f"✅ Successfully fetched {len(jobs)} total jobs")
    
    # Test job filtering
    print("\n🔍 Filtering for electrical engineering jobs...")
    relevant_jobs = [job for job in jobs if scraper.is_relevant_job(job)]
    
    print(f"✅ Found {len(relevant_jobs)} relevant electrical engineering jobs")
    print(relevant_jobs)
    
    if relevant_jobs:
        print("\n📋 Relevant jobs found:")
        for i, job_data in enumerate(relevant_jobs[:5], 1):  # Show first 5
            job = scraper.parse_job(job_data)
            print(f"  {i}. {job.title}")
            print(f"     Apply: {job.applyLink}")
            print(f"     Career Page: {job.careerLink}")
            print()
    
    # Test pickle functionality
    print("💾 Testing pickle storage...")
    original_count = len(scraper.known_job_titles)
    scraper.save_known_jobs()
    
    # Reload and verify
    scraper.load_known_jobs()
    new_count = len(scraper.known_job_titles)
    
    if original_count == new_count:
        print("✅ Pickle storage working correctly")
    else:
        print(f"⚠️  Pickle storage issue: {original_count} -> {new_count}")
    
    print("\n🎉 Test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_scraper()
    sys.exit(0 if success else 1)
