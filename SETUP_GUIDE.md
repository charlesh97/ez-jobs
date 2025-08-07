# Quick Setup Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Test the Scraper
```bash
python3 test_scraper.py
```

### 3. Run the Scraper (with sample data)
```bash
python3 ez-apply.py
```

### 4. Set Up Discord Notifications (Optional)
1. Go to your Discord server settings
2. Navigate to **Integrations** > **Webhooks**
3. Create a new webhook and copy the URL
4. Set the environment variable:
```bash
export DISCORD_WEBHOOK_URL="your_webhook_url_here"
```

### 5. Set Up Daily Scheduling
```bash
python3 scheduler.py
```

## 📁 Files Created
- `known_jobs.pkl` - Database of seen jobs
- `job_scraper.log` - Scraper activity logs
- `scheduler.log` - Scheduler logs (if using scheduler.py)

## 🔧 Configuration
Edit `config.py` to customize:
- Job keywords to monitor
- Schedule time
- Logging level
- Request timeout

## 🧪 Testing with Sample Data
The scraper includes `sample_jobs.json` with 5 sample electrical engineering jobs for testing. When API endpoints are unavailable, it will automatically fall back to using this file.

## 📝 Current Status
✅ **Working Features:**
- Job filtering for electrical engineering positions
- Local storage with pickle files
- Discord notifications (when webhook is configured)
- Daily scheduling
- Comprehensive logging
- Sample data for testing

⚠️ **Known Limitations:**
- OpenAI's careers website is protected by Cloudflare
- API endpoints may not be publicly available
- Uses sample data for demonstration

## 🎯 Next Steps
1. Test with sample data to verify functionality
2. Set up Discord webhook for notifications
3. Configure daily scheduling
4. Monitor logs for any issues
5. Consider implementing advanced scraping techniques if needed
