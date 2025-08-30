# Troubleshooting Guide

## Issues Found During Testing

### 1. OpenAI API Key Issue ❌
**Problem**: Invalid API key provided
**Solution**: 
- Go to [OpenAI Platform](https://platform.openai.com/api-keys)
- Create a new API key or check if your current one is valid
- Make sure you have credits in your OpenAI account
- Update your `.env` file with the new key

### 2. Notion Database ID Issue ❌
**Problem**: Using a page ID instead of a database ID
**Solution**:
- The ID you provided (`a82760ef-7436-45cc-a6f5-382f1c7004a1`) is a page, not a database
- To find your database ID:
  1. Open your Notion database in the browser
  2. Look at the URL: `https://notion.so/workspace/[database-id]?v=...`
  3. Copy the database ID (32 characters, separated by hyphens)
  4. Update your `.env` file

### 3. WordPress SSL Certificate Issue ❌
**Problem**: SSL certificate verification failed
**Solution**:
- This is likely a self-signed certificate or local development issue
- For testing, you can temporarily disable SSL verification (not recommended for production)
- Or ensure your WordPress site has a valid SSL certificate

### 4. RSS Feed Issue ❌
**Problem**: No entries found from Reddit
**Solution**:
- Reddit may be blocking automated requests
- Try using a different RSS feed or add user-agent headers
- Consider using Reddit's official API instead

## Quick Fixes

### Fix OpenAI API Key
1. Visit: https://platform.openai.com/api-keys
2. Create new key or copy existing valid key
3. Update `.env` file

### Fix Notion Database ID
1. Open your Notion database
2. Copy the database ID from the URL
3. Update `.env` file

### Fix WordPress SSL (Temporary)
Add this to your `.env` file:
```
WP_SSL_VERIFY=false
```

### Alternative RSS Sources
Try these instead of Reddit:
- TechCrunch: `https://techcrunch.com/feed/`
- The Verge: `https://www.theverge.com/rss/index.xml`
- Ars Technica: `https://feeds.arstechnica.com/arstechnica/index`

## Testing Steps
1. Fix the issues above
2. Run `python3 test_automation.py` again
3. Once all tests pass, run `python3 main.py`
4. Set up daily automation with `./setup_cron.sh`

