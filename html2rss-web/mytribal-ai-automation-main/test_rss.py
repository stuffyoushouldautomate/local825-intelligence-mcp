#!/usr/bin/env python3
"""
Simple RSS feed test script
"""

import feedparser
import requests

def test_rss_feeds():
    """Test various RSS feeds"""
    
    feeds = [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml", 
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://www.reddit.com/r/technology/hot.rss?limit=3"
    ]
    
    for url in feeds:
        print(f"\n🔍 Testing: {url}")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            if feed.entries:
                print(f"✅ Success! Found {len(feed.entries)} entries")
                print(f"   First entry: {feed.entries[0].title[:60]}...")
                if hasattr(feed.entries[0], 'contentSnippet'):
                    print(f"   Snippet: {feed.entries[0].contentSnippet[:80]}...")
                elif hasattr(feed.entries[0], 'summary'):
                    print(f"   Summary: {feed.entries[0].summary[:80]}...")
            else:
                print("❌ No entries found")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_rss_feeds()

