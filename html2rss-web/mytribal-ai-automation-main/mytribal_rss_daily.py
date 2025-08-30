#!/usr/bin/env python3
"""
mytribal.ai Daily RSS Automation Script
Focuses on today's posts and new content for daily processing
"""

import feedparser
import requests
from datetime import datetime, timedelta
import json
import time
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mytribal_rss_daily.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Working RSS feeds from mytribal.ai
MYTRIBAL_RSS_FEEDS = [
    "https://mytribal.ai/feed/",
    "https://mytribal.ai/feed/rss/",
    "https://mytribal.ai/feed/atom/",
    "https://mytribal.ai/feed/rss2/"
]

# Configuration for daily processing
CONFIG = {
    'data_dir': 'rss_data',
    'max_entries_per_run': 10,
    'today_only': True,  # Focus on today's posts
    'max_days_old': 1,   # Only process posts from today (0-1 days old)
    'backup_count': 5,   # Keep last 5 daily backup files
    'request_delay': 1,  # Delay between requests in seconds
}

def ensure_data_directory():
    """Ensure the data directory exists"""
    Path(CONFIG['data_dir']).mkdir(exist_ok=True)
    return CONFIG['data_dir']

def fetch_todays_rss():
    """Fetch RSS content from mytribal.ai, focusing on today's posts"""
    logger.info("🔍 Fetching today's RSS feeds from mytribal.ai...")
    
    all_entries = []
    today = datetime.now().date()
    
    for feed_url in MYTRIBAL_RSS_FEEDS:
        try:
            logger.info(f"📡 Fetching: {feed_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(feed_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            if feed.entries:
                logger.info(f"✅ Found {len(feed.entries)} entries from {feed_url}")
                
                for entry in feed.entries:
                    # Extract entry data
                    entry_data = {
                        'title': entry.title,
                        'link': entry.get('link', ''),
                        'published': entry.get('published', entry.get('updated', '')),
                        'summary': entry.get('summary', entry.get('contentSnippet', '')),
                        'feed_url': feed_url,
                        'feed_title': feed.feed.get('title', 'mytribal.ai'),
                        'timestamp': datetime.now().isoformat(),
                        'processed': False,
                        'processing_date': None,
                        'is_today': False
                    }
                    
                    # Parse publication date and check if it's today
                    try:
                        if entry_data['published']:
                            if 'T' in entry_data['published']:
                                # ISO format
                                pub_date = datetime.fromisoformat(entry_data['published'].replace('Z', '+00:00'))
                            else:
                                # RSS format
                                pub_date = datetime.strptime(entry_data['published'], '%a, %d %b %Y %H:%M:%S %z')
                            
                            entry_data['parsed_date'] = pub_date.isoformat()
                            entry_data['days_old'] = (datetime.now(pub_date.tzinfo) - pub_date).days
                            
                            # Check if post is from today
                            pub_date_local = pub_date.astimezone()
                            entry_data['is_today'] = (pub_date_local.date() == today)
                            
                            # Add time-based categorization
                            if entry_data['is_today']:
                                hour = pub_date_local.hour
                                if 6 <= hour < 12:
                                    entry_data['time_category'] = 'morning'
                                elif 12 <= hour < 18:
                                    entry_data['time_category'] = 'afternoon'
                                elif 18 <= hour < 22:
                                    entry_data['time_category'] = 'evening'
                                else:
                                    entry_data['time_category'] = 'night'
                            else:
                                entry_data['time_category'] = 'previous_days'
                            
                        else:
                            entry_data['parsed_date'] = None
                            entry_data['days_old'] = None
                            entry_data['is_today'] = False
                            entry_data['time_category'] = 'unknown'
                            
                    except Exception as e:
                        logger.warning(f"Could not parse date for entry: {entry.title[:50]}... Error: {e}")
                        entry_data['parsed_date'] = None
                        entry_data['days_old'] = None
                        entry_data['is_today'] = False
                        entry_data['time_category'] = 'unknown'
                    
                    all_entries.append(entry_data)
                
            else:
                logger.warning(f"❌ No entries found in {feed_url}")
                
        except Exception as e:
            logger.error(f"❌ Error fetching {feed_url}: {e}")
            continue
        
        time.sleep(CONFIG['request_delay'])
    
    return all_entries

def filter_todays_entries(entries):
    """Filter entries to focus on today's content"""
    if CONFIG['today_only']:
        # Only process today's entries
        todays_entries = [
            entry for entry in entries 
            if entry.get('is_today', False)
        ]
        logger.info(f"📅 Found {len(todays_entries)} entries from today")
        return todays_entries
    else:
        # Process recent entries within the day limit
        recent_entries = [
            entry for entry in entries 
            if entry.get('days_old', float('inf')) <= CONFIG['max_days_old']
        ]
        logger.info(f"📅 Found {len(recent_entries)} entries from last {CONFIG['max_days_old']} days")
        return recent_entries

def remove_duplicates(entries):
    """Remove duplicate entries based on title and link"""
    seen = set()
    unique_entries = []
    
    for entry in entries:
        identifier = f"{entry['title']}_{entry['link']}"
        
        if identifier not in seen:
            seen.add(identifier)
            unique_entries.append(entry)
    
    return unique_entries

def load_daily_data(data_dir):
    """Load today's RSS data"""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = Path(data_dir) / f"mytribal_rss_{today}.json"
    
    if daily_file.exists():
        try:
            with open(daily_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            logger.info(f"📂 Loaded today's data: {len(existing_data)} entries")
            return existing_data
        except Exception as e:
            logger.error(f"Error loading today's data: {e}")
    
    return []

def save_daily_data(data_dir, entries):
    """Save today's RSS data with date-specific filename"""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = Path(data_dir) / f"mytribal_rss_{today}.json"
    backup_dir = Path(data_dir) / "daily_backups"
    backup_dir.mkdir(exist_ok=True)
    
    # Create backup if file exists
    if daily_file.exists():
        timestamp = datetime.now().strftime("%H%M%S")
        backup_file = backup_dir / f"mytribal_rss_{today}_{timestamp}.json"
        try:
            daily_file.rename(backup_file)
            logger.info(f"💾 Created daily backup: {backup_file}")
        except Exception as e:
            logger.error(f"Error creating daily backup: {e}")
    
    # Save new data
    try:
        with open(daily_file, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"💾 Saved {len(entries)} entries to {daily_file}")
        
        # Clean up old daily backups
        cleanup_old_daily_backups(backup_dir)
        
        return True
    except Exception as e:
        logger.error(f"❌ Error saving daily data: {e}")
        return False

def cleanup_old_daily_backups(backup_dir):
    """Keep only the most recent daily backup files"""
    backup_files = sorted(backup_dir.glob("mytribal_rss_*.json"))
    
    if len(backup_files) > CONFIG['backup_count']:
        files_to_remove = backup_files[:-CONFIG['backup_count']]
        for file in files_to_remove:
            try:
                file.unlink()
                logger.info(f"🗑️ Removed old daily backup: {file}")
            except Exception as e:
                logger.error(f"Error removing daily backup {file}: {e}")

def create_daily_summary(entries):
    """Create a summary of today's processing"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    summary = {
        'date': today,
        'run_timestamp': datetime.now().isoformat(),
        'total_entries': len(entries),
        'todays_entries': len([e for e in entries if e.get('is_today', False)]),
        'entries_by_time': {},
        'feeds_processed': len(MYTRIBAL_RSS_FEEDS),
        'processing_stats': {
            'successful_parses': 0,
            'morning_posts': 0,
            'afternoon_posts': 0,
            'evening_posts': 0,
            'night_posts': 0
        }
    }
    
    # Count entries by time category
    for entry in entries:
        time_cat = entry.get('time_category', 'unknown')
        summary['entries_by_time'][time_cat] = summary['entries_by_time'].get(time_cat, 0) + 1
        
        # Count successful parses
        if entry.get('parsed_date'):
            summary['processing_stats']['successful_parses'] += 1
        
        # Count by time of day
        if time_cat == 'morning':
            summary['processing_stats']['morning_posts'] += 1
        elif time_cat == 'afternoon':
            summary['processing_stats']['afternoon_posts'] += 1
        elif time_cat == 'evening':
            summary['processing_stats']['evening_posts'] += 1
        elif time_cat == 'night':
            summary['processing_stats']['night_posts'] += 1
    
    return summary

def display_todays_content(entries):
    """Display today's content in a readable format"""
    todays_entries = [e for e in entries if e.get('is_today', False)]
    
    if not todays_entries:
        logger.info("📅 No posts found from today yet")
        return
    
    logger.info(f"\n📊 Today's Content ({len(todays_entries)} posts):")
    logger.info("=" * 80)
    
    for i, entry in enumerate(todays_entries, 1):
        logger.info(f"\n{i}. {entry['title']}")
        logger.info(f"   🔗 Link: {entry['link']}")
        logger.info(f"   📅 Published: {entry['published']}")
        logger.info(f"   ⏰ Time: {entry.get('time_category', 'unknown')}")
        logger.info(f"   📝 Summary: {entry['summary'][:100]}...")
        logger.info(f"   📡 Source: {entry['feed_title']}")
        logger.info("-" * 60)

def main():
    """Main daily RSS automation workflow"""
    logger.info("🚀 Starting mytribal.ai Daily RSS Automation...")
    start_time = datetime.now()
    
    try:
        # Ensure data directory exists
        data_dir = ensure_data_directory()
        
        # Load today's existing data
        existing_entries = load_daily_data(data_dir)
        
        # Fetch new RSS content
        new_entries = fetch_todays_rss()
        
        if not new_entries:
            logger.warning("❌ No RSS content found. Exiting.")
            return
        
        logger.info(f"📥 Total entries fetched: {len(new_entries)}")
        
        # Remove duplicates
        unique_entries = remove_duplicates(new_entries)
        logger.info(f"🔄 After removing duplicates: {len(unique_entries)} entries")
        
        # Filter for today's content
        todays_entries = filter_todays_entries(unique_entries)
        
        if not todays_entries:
            logger.info("📅 No new content from today found")
            return
        
        # Merge with existing data
        all_entries = existing_entries + todays_entries
        all_entries = remove_duplicates(all_entries)  # Remove duplicates again after merge
        
        # Sort by date (newest first)
        all_entries.sort(
            key=lambda x: x['parsed_date'] if x['parsed_date'] else '1970-01-01',
            reverse=True
        )
        
        # Save today's data
        if save_daily_data(data_dir, all_entries):
            # Create summary
            summary = create_daily_summary(all_entries)
            
            # Save summary
            summary_file = Path(data_dir) / f"daily_summary_{datetime.now().strftime('%Y-%m-%d')}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, default=str)
            
            # Display today's content
            display_todays_content(all_entries)
            
            # Log summary
            logger.info("\n📊 Daily Processing Summary:")
            logger.info(f"   Date: {summary['date']}")
            logger.info(f"   Total entries: {summary['total_entries']}")
            logger.info(f"   Today's entries: {summary['todays_entries']}")
            logger.info(f"   Feeds processed: {summary['feeds_processed']}")
            logger.info(f"   Successful parses: {summary['processing_stats']['successful_parses']}")
            
            logger.info(f"\n🎉 Daily RSS Automation completed successfully!")
            logger.info(f"   Data saved to: {data_dir}/")
            logger.info(f"   Summary saved to: {summary_file}")
        
    except Exception as e:
        logger.error(f"❌ Fatal error in daily RSS automation: {e}")
        raise
    
    finally:
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"⏰ Total runtime: {duration}")

if __name__ == "__main__":
    main()
