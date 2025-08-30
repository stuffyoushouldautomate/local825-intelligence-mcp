#!/usr/bin/env python3
"""
mytribal.ai RSS Production Automation Script
Integrates with existing automation setup for content generation and publishing
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
        logging.FileHandler('mytribal_rss.log'),
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

# Configuration
CONFIG = {
    'data_dir': 'rss_data',
    'max_entries_per_run': 5,
    'days_threshold': 30,  # Process entries from last 30 days
    'backup_count': 10,    # Keep last 10 backup files
    'request_delay': 1,    # Delay between requests in seconds
}

def ensure_data_directory():
    """Ensure the data directory exists"""
    Path(CONFIG['data_dir']).mkdir(exist_ok=True)
    return CONFIG['data_dir']

def fetch_mytribal_rss():
    """Fetch RSS content from mytribal.ai with error handling"""
    logger.info("🔍 Fetching RSS feeds from mytribal.ai...")
    
    all_entries = []
    
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
                        'processing_date': None
                    }
                    
                    # Parse publication date
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
                        else:
                            entry_data['parsed_date'] = None
                            entry_data['days_old'] = None
                    except Exception as e:
                        logger.warning(f"Could not parse date for entry: {entry.title[:50]}... Error: {e}")
                        entry_data['parsed_date'] = None
                        entry_data['days_old'] = None
                    
                    all_entries.append(entry_data)
                
            else:
                logger.warning(f"❌ No entries found in {feed_url}")
                
        except Exception as e:
            logger.error(f"❌ Error fetching {feed_url}: {e}")
            continue
        
        time.sleep(CONFIG['request_delay'])  # Be respectful to the server
    
    return all_entries

def filter_and_sort_entries(entries):
    """Filter entries and sort by date"""
    # Filter by age threshold
    recent_entries = [
        entry for entry in entries 
        if entry['days_old'] is not None and entry['days_old'] <= CONFIG['days_threshold']
    ]
    
    # Sort by date (newest first)
    recent_entries.sort(key=lambda x: x['days_old'] if x['days_old'] is not None else float('inf'))
    
    # Limit entries per run
    return recent_entries[:CONFIG['max_entries_per_run']]

def remove_duplicates(entries):
    """Remove duplicate entries based on title and link"""
    seen = set()
    unique_entries = []
    
    for entry in entries:
        # Create a unique identifier
        identifier = f"{entry['title']}_{entry['link']}"
        
        if identifier not in seen:
            seen.add(identifier)
            unique_entries.append(entry)
    
    return unique_entries

def load_existing_data(data_dir):
    """Load existing RSS data to avoid reprocessing"""
    data_file = Path(data_dir) / "mytribal_rss_master.json"
    
    if data_file.exists():
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            logger.info(f"📂 Loaded existing data: {len(existing_data)} entries")
            return existing_data
        except Exception as e:
            logger.error(f"Error loading existing data: {e}")
    
    return []

def merge_new_entries(existing_entries, new_entries):
    """Merge new entries with existing ones, avoiding duplicates"""
    # Create a set of existing entry identifiers
    existing_ids = {
        f"{entry['title']}_{entry['link']}" 
        for entry in existing_entries
    }
    
    # Add only truly new entries
    truly_new = []
    for entry in new_entries:
        entry_id = f"{entry['title']}_{entry['link']}"
        if entry_id not in existing_ids:
            truly_new.append(entry)
            existing_ids.add(entry_id)
    
    # Combine existing and new entries
    all_entries = existing_entries + truly_new
    
    # Sort by date (newest first)
    all_entries.sort(
        key=lambda x: x['parsed_date'] if x['parsed_date'] else '1970-01-01',
        reverse=True
    )
    
    return all_entries, truly_new

def save_data(data_dir, entries, filename="mytribal_rss_master.json"):
    """Save RSS data with backup"""
    data_file = Path(data_dir) / filename
    backup_dir = Path(data_dir) / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    # Create backup
    if data_file.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"mytribal_rss_backup_{timestamp}.json"
        try:
            data_file.rename(backup_file)
            logger.info(f"💾 Created backup: {backup_file}")
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
    
    # Save new data
    try:
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"💾 Saved {len(entries)} entries to {data_file}")
        
        # Clean up old backups
        cleanup_old_backups(backup_dir)
        
        return True
    except Exception as e:
        logger.error(f"❌ Error saving data: {e}")
        return False

def cleanup_old_backups(backup_dir):
    """Keep only the most recent backup files"""
    backup_files = sorted(backup_dir.glob("mytribal_rss_backup_*.json"))
    
    if len(backup_files) > CONFIG['backup_count']:
        files_to_remove = backup_files[:-CONFIG['backup_count']]
        for file in files_to_remove:
            try:
                file.unlink()
                logger.info(f"🗑️ Removed old backup: {file}")
            except Exception as e:
                logger.error(f"Error removing backup {file}: {e}")

def create_processing_summary(entries, new_entries):
    """Create a summary of the processing run"""
    summary = {
        'run_timestamp': datetime.now().isoformat(),
        'total_entries': len(entries),
        'new_entries': len(new_entries),
        'entries_by_age': {},
        'processing_stats': {
            'feeds_processed': len(MYTRIBAL_RSS_FEEDS),
            'duplicates_removed': 0,
            'successful_parses': 0
        }
    }
    
    # Count entries by age
    for entry in entries:
        age = entry.get('days_old', 'unknown')
        if age == 'unknown':
            age = 'unknown'
        elif age <= 1:
            age = '1 day or less'
        elif age <= 7:
            age = '2-7 days'
        elif age <= 30:
            age = '8-30 days'
        else:
            age = '30+ days'
        
        summary['entries_by_age'][age] = summary['entries_by_age'].get(age, 0) + 1
    
    # Count successful parses
    summary['processing_stats']['successful_parses'] = sum(
        1 for entry in entries if entry.get('parsed_date')
    )
    
    return summary

def main():
    """Main RSS automation workflow"""
    logger.info("🚀 Starting mytribal.ai RSS Production Automation...")
    start_time = datetime.now()
    
    try:
        # Ensure data directory exists
        data_dir = ensure_data_directory()
        
        # Load existing data
        existing_entries = load_existing_data(data_dir)
        
        # Fetch new RSS content
        new_entries = fetch_mytribal_rss()
        
        if not new_entries:
            logger.warning("❌ No RSS content found. Exiting.")
            return
        
        logger.info(f"📥 Total entries fetched: {len(new_entries)}")
        
        # Remove duplicates from new entries
        unique_new_entries = remove_duplicates(new_entries)
        logger.info(f"🔄 After removing duplicates: {len(unique_new_entries)} entries")
        
        # Filter and sort entries
        filtered_entries = filter_and_sort_entries(unique_new_entries)
        logger.info(f"🎯 Entries to process: {len(filtered_entries)}")
        
        # Merge with existing data
        all_entries, truly_new = merge_new_entries(existing_entries, filtered_entries)
        logger.info(f"📊 Total entries in database: {len(all_entries)}")
        logger.info(f"🆕 New entries added: {len(truly_new)}")
        
        # Save data
        if save_data(data_dir, all_entries):
            # Create summary
            summary = create_processing_summary(all_entries, truly_new)
            
            # Save summary
            summary_file = Path(data_dir) / "processing_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, default=str)
            
            # Log summary
            logger.info("📊 Processing Summary:")
            logger.info(f"   Total entries: {summary['total_entries']}")
            logger.info(f"   New entries: {summary['new_entries']}")
            logger.info(f"   Feeds processed: {summary['processing_stats']['feeds_processed']}")
            logger.info(f"   Successful parses: {summary['processing_stats']['successful_parses']}")
            
            # Show new entries
            if truly_new:
                logger.info("\n🆕 New entries added:")
                for i, entry in enumerate(truly_new, 1):
                    logger.info(f"   {i}. {entry['title'][:60]}...")
                    logger.info(f"      Age: {entry.get('days_old', 'unknown')} days")
                    logger.info(f"      Link: {entry['link']}")
            
            logger.info(f"\n🎉 RSS Automation completed successfully!")
            logger.info(f"   Data saved to: {data_dir}/")
            logger.info(f"   Summary saved to: {summary_file}")
        
    except Exception as e:
        logger.error(f"❌ Fatal error in RSS automation: {e}")
        raise
    
    finally:
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"⏰ Total runtime: {duration}")

if __name__ == "__main__":
    main()
