#!/usr/bin/env python3
"""
mytribal.ai RSS Automation Script
Pulls content from mytribal.ai RSS feeds and processes it
"""

import feedparser
import requests
from datetime import datetime, timedelta
import json
import time
import os

# Working RSS feeds from mytribal.ai
MYTRIBAL_RSS_FEEDS = [
    "https://mytribal.ai/feed/",
    "https://mytribal.ai/feed/rss/",
    "https://mytribal.ai/feed/atom/",
    "https://mytribal.ai/feed/rss2/"
]

def fetch_mytribal_rss():
    """Fetch RSS content from mytribal.ai"""
    print("🔍 Fetching RSS feeds from mytribal.ai...")
    
    all_entries = []
    
    for feed_url in MYTRIBAL_RSS_FEEDS:
        try:
            print(f"\n📡 Fetching: {feed_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(feed_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            if feed.entries:
                print(f"✅ Found {len(feed.entries)} entries")
                
                for entry in feed.entries:
                    # Extract entry data
                    entry_data = {
                        'title': entry.title,
                        'link': entry.get('link', ''),
                        'published': entry.get('published', entry.get('updated', '')),
                        'summary': entry.get('summary', entry.get('contentSnippet', '')),
                        'feed_url': feed_url,
                        'feed_title': feed.feed.get('title', 'mytribal.ai'),
                        'timestamp': datetime.now().isoformat()
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
                    except:
                        entry_data['parsed_date'] = None
                        entry_data['days_old'] = None
                    
                    all_entries.append(entry_data)
                
            else:
                print("❌ No entries found")
                
        except Exception as e:
            print(f"❌ Error fetching {feed_url}: {e}")
            continue
        
        time.sleep(1)  # Be respectful to the server
    
    return all_entries

def filter_recent_entries(entries, days_threshold=7):
    """Filter entries to only recent ones"""
    recent_entries = []
    
    for entry in entries:
        if entry['days_old'] is not None and entry['days_old'] <= days_threshold:
            recent_entries.append(entry)
    
    return recent_entries

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

def save_to_json(entries, filename="mytribal_rss_data.json"):
    """Save RSS data to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False, default=str)
        print(f"💾 Saved {len(entries)} entries to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving to JSON: {e}")
        return False

def display_entries(entries):
    """Display RSS entries in a readable format"""
    print(f"\n📊 Found {len(entries)} unique RSS entries:")
    print("=" * 80)
    
    for i, entry in enumerate(entries, 1):
        print(f"\n{i}. {entry['title']}")
        print(f"   🔗 Link: {entry['link']}")
        print(f"   📅 Published: {entry['published']}")
        if entry['days_old'] is not None:
            print(f"   ⏰ Age: {entry['days_old']} days ago")
        print(f"   📝 Summary: {entry['summary'][:100]}...")
        print(f"   📡 Source: {entry['feed_title']}")
        print("-" * 60)

def main():
    """Main RSS automation workflow"""
    print("🚀 Starting mytribal.ai RSS Automation...")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Fetch RSS content
    entries = fetch_mytribal_rss()
    
    if not entries:
        print("❌ No RSS content found. Exiting.")
        return
    
    print(f"\n📥 Total entries fetched: {len(entries)}")
    
    # Remove duplicates
    unique_entries = remove_duplicates(entries)
    print(f"🔄 After removing duplicates: {len(unique_entries)} entries")
    
    # Filter recent entries (last 7 days)
    recent_entries = filter_recent_entries(unique_entries, days_threshold=7)
    print(f"🕒 Recent entries (last 7 days): {len(recent_entries)} entries")
    
    # Display entries
    if recent_entries:
        display_entries(recent_entries)
    else:
        print("\n📅 No recent entries found in the last 7 days")
        print("Showing all entries instead:")
        display_entries(unique_entries)
    
    # Save to JSON
    save_to_json(unique_entries)
    
    # Summary
    print(f"\n🎉 RSS Automation completed!")
    print(f"   Total entries: {len(entries)}")
    print(f"   Unique entries: {len(unique_entries)}")
    print(f"   Recent entries: {len(recent_entries)}")
    print(f"   Data saved to: mytribal_rss_data.json")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
