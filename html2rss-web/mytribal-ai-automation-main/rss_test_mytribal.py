#!/usr/bin/env python3
"""
RSS Feed Test Script for mytribal.ai
This script tests RSS feeds without requiring API keys
"""

import feedparser
import requests
from datetime import datetime
import time

def test_mytribal_rss():
    """Test RSS feeds that might be available on mytribal.ai"""
    
    # Common RSS feed patterns for websites
    potential_feeds = [
        "https://mytribal.ai/feed/",
        "https://mytribal.ai/rss/",
        "https://mytribal.ai/feed.xml",
        "https://mytribal.ai/rss.xml",
        "https://mytribal.ai/blog/feed/",
        "https://mytribal.ai/news/feed/",
        "https://mytribal.ai/feed/rss/",
        "https://mytribal.ai/feed/atom/",
        "https://mytribal.ai/feed/rss2/",
        "https://mytribal.ai/feed/rdf/",
        "https://mytribal.ai/feed/feed.xml",
        "https://mytribal.ai/feed/index.xml",
        "https://mytribal.ai/feed/posts.xml",
        "https://mytribal.ai/feed/articles.xml"
    ]
    
    print("🔍 Testing potential RSS feeds for mytribal.ai...")
    print("=" * 60)
    
    working_feeds = []
    
    for url in potential_feeds:
        print(f"\n📡 Testing: {url}")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                print(f"✅ HTTP 200 - Content length: {len(response.content)} bytes")
                
                # Try to parse as RSS
                feed = feedparser.parse(response.content)
                
                if feed.entries and len(feed.entries) > 0:
                    print(f"🎉 RSS Feed Found! {len(feed.entries)} entries")
                    print(f"   Feed Title: {feed.feed.get('title', 'No title')}")
                    print(f"   Feed Description: {feed.feed.get('description', 'No description')[:100]}...")
                    
                    # Show latest entries
                    for i, entry in enumerate(feed.entries[:3], 1):
                        print(f"   {i}. {entry.title}")
                        if hasattr(entry, 'published'):
                            print(f"      Published: {entry.published}")
                        elif hasattr(entry, 'updated'):
                            print(f"      Updated: {entry.updated}")
                        
                        # Check for content
                        if hasattr(entry, 'contentSnippet'):
                            print(f"      Snippet: {entry.contentSnippet[:80]}...")
                        elif hasattr(entry, 'summary'):
                            print(f"      Summary: {entry.summary[:80]}...")
                    
                    working_feeds.append({
                        'url': url,
                        'feed': feed,
                        'entry_count': len(feed.entries)
                    })
                    
                else:
                    print("❌ No RSS entries found in response")
                    
            else:
                print(f"❌ HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request Error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Small delay between requests
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if working_feeds:
        print(f"✅ Found {len(working_feeds)} working RSS feeds!")
        for feed_info in working_feeds:
            print(f"\n🔗 {feed_info['url']}")
            print(f"   Entries: {feed_info['entry_count']}")
            print(f"   Title: {feed_info['feed'].feed.get('title', 'No title')}")
    else:
        print("❌ No working RSS feeds found")
        print("\n💡 Suggestions:")
        print("   - Check if mytribal.ai has RSS enabled")
        print("   - Look for RSS links in the website footer")
        print("   - Check the website's robots.txt file")
        print("   - Contact the website administrator")
    
    return working_feeds

def check_website_for_rss():
    """Check the main website for RSS feed links"""
    print("\n🌐 Checking mytribal.ai website for RSS feed links...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get("https://mytribal.ai", headers=headers, timeout=15)
        
        if response.status_code == 200:
            content = response.text.lower()
            
            # Look for RSS-related content
            rss_indicators = [
                'rss', 'feed', 'xml', 'atom', 'syndication',
                'subscribe', 'newsletter', 'updates'
            ]
            
            found_indicators = []
            for indicator in rss_indicators:
                if indicator in content:
                    found_indicators.append(indicator)
            
            if found_indicators:
                print(f"✅ Found RSS indicators: {', '.join(found_indicators)}")
            else:
                print("❌ No RSS indicators found on the main page")
                
        else:
            print(f"❌ Could not access main website: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking website: {e}")

if __name__ == "__main__":
    print("🚀 Starting RSS Feed Discovery for mytribal.ai")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check main website first
    check_website_for_rss()
    
    # Test potential RSS feeds
    working_feeds = test_mytribal_rss()
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if working_feeds:
        print("\n🎯 Next steps:")
        print("   1. Use the working RSS feed URL in your automation")
        print("   2. Update your main_improved.py script with the working feed")
        print("   3. Set up your .env file with API keys for full automation")
    else:
        print("\n🔍 Manual investigation needed:")
        print("   - Visit mytribal.ai and look for RSS feed links")
        print("   - Check the website's source code for RSS references")
        print("   - Look for social media feeds as alternatives")
