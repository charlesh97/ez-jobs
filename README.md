# OpenAI Careers Job Scraper

A Python web scraper that monitors OpenAI's careers website for electrical engineering positions and sends Discord notifications for new job postings.

⚠️ **Important Note**: OpenAI's careers website is protected by Cloudflare, which may block automated requests. This scraper includes multiple fallback methods and alternative approaches to handle this limitation.

## Features

- 🔍 **Smart Job Filtering**: Automatically filters for electrical engineering, hardware engineering, and related positions
- 💾 **Local Storage**: Uses pickle files to track previously seen jobs and avoid duplicate notifications
- 🔔 **Discord Notifications**: Sends rich Discord embeds with job details and direct links
- ⏰ **Daily Scheduling**: Runs automatically once per day at 9:00 AM
- 📝 **Comprehensive Logging**: Detailed logs for monitoring and debugging

## Job Keywords Monitored

The scraper looks for the following keywords in job titles, departments, and descriptions:

- Electrical Engineer
- Electrical Engineering
- System Electrical Engineer
- Hardware Engineer
- Hardware Engineering
- Electronics Engineer
- Electronics Engineering
- Power Systems Engineer
- Electrical Systems Engineer

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Discord Webhook

1. Go to your Discord server settings
2. Navigate to **Integrations** > **Webhooks**
3. Click **New Webhook**
4. Give it a name (e.g., "OpenAI Job Bot")
5. Copy the webhook URL
6. Set it as an environment variable:

```bash
export DISCORD_WEBHOOK_URL="your_webhook_url_here"
```

### 3. Test the Scraper

Run the scraper manually to test it:

```bash
python ez-apply.py
```

### 4. Set Up Daily Scheduling

#### Option A: Using the Python Scheduler (Recommended for Development)

```bash
python scheduler.py
```

This will run the scraper immediately and then schedule it to run daily at 9:00 AM.

#### Option B: Using System Cron (Recommended for Production)

Add this line to your crontab (`crontab -e`):

```bash
0 9 * * * cd /path/to/ez-apply && /usr/bin/python3 ez-apply.py >> job_scraper.log 2>&1
```

This runs the scraper daily at 9:00 AM.

## File Structure

```
ez-apply/
├── ez-apply.py          # Main scraper script
├── scheduler.py         # Daily scheduler
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── known_jobs.pkl      # Database of seen jobs (created automatically)
├── job_scraper.log     # Scraper logs (created automatically)
└── scheduler.log       # Scheduler logs (created automatically)
```

## Usage

### Manual Run

```bash
python ez-apply.py
```

### Scheduled Run

```bash
python scheduler.py
```

### Environment Variables

- `DISCORD_WEBHOOK_URL`: Your Discord webhook URL for notifications

## Discord Notification Format

The bot sends rich Discord embeds with:

- 🔌 **Title**: "New Electrical Engineering Job at OpenAI!"
- **Job Title**: The actual job title
- **Location**: Job location
- **Department**: Department name
- **Description**: First 200 characters of job description
- **Direct Link**: Clickable link to the job posting
- **Timestamp**: When the job was posted

## Logging

The scraper creates detailed logs in:

- `job_scraper.log`: Main scraper activity
- `scheduler.log`: Scheduler activity (if using scheduler.py)

Log levels include:
- INFO: Normal operation
- WARNING: Non-critical issues (e.g., missing Discord webhook)
- ERROR: Critical issues that need attention

## Troubleshooting

### Common Issues

1. **No Discord notifications**: Check that `DISCORD_WEBHOOK_URL` is set correctly
2. **Scraper fails**: Check the logs for error messages
3. **Duplicate notifications**: The pickle file might be corrupted - delete `known_jobs.pkl` to reset
4. **Rate limiting**: The scraper includes delays and proper headers to avoid being blocked
5. **Cloudflare protection**: OpenAI's website may block automated requests

### Cloudflare Protection Solutions

If you encounter Cloudflare protection issues, try these solutions:

#### Option 1: Use a Different User Agent
Update the `USER_AGENT` in `config.py` to a more recent browser version.

#### Option 2: Add Delays Between Requests
The scraper already includes delays, but you can increase them in the configuration.

#### Option 3: Use a Proxy Service
Consider using a proxy service or VPN to avoid IP-based blocking.

#### Option 4: Manual Data Input
For testing purposes, you can manually create a JSON file with job data:

```bash
# Create a sample jobs.json file
echo '[
  {
    "id": "test-job-1",
    "title": "Electrical Engineer",
    "location": "San Francisco, CA",
    "department": "Hardware",
    "description": "We are looking for an electrical engineer...",
    "posted_date": "2024-01-01"
  }
]' > jobs.json
```

Then modify the scraper to read from this file for testing.

#### Option 5: Use Selenium (Advanced)
For more robust scraping, you can implement Selenium-based scraping:

```bash
pip install selenium webdriver-manager
```

This would require additional code to handle browser automation and bypass Cloudflare protection.

### Reset Job Database

To start fresh and see all jobs as "new":

```bash
rm known_jobs.pkl
```

### Check Logs

```bash
tail -f job_scraper.log
```

## Customization

### Adding New Job Keywords

Edit the `target_keywords` list in `ez-apply.py`:

```python
self.target_keywords = [
    'electrical engineer',
    'hardware engineer',
    'your_new_keyword',  # Add here
]
```

### Changing Schedule Time

In `scheduler.py`, modify the schedule line:

```python
schedule.every().day.at("14:30").do(run_scraper)  # 2:30 PM
```

### Custom Discord Message

Modify the `send_discord_notification` method in `ez-apply.py` to customize the notification format.

## Security Notes

- Never commit your Discord webhook URL to version control
- Use environment variables for sensitive configuration
- The scraper respects rate limits and includes proper headers

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.
