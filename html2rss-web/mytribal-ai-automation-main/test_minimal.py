#!/usr/bin/env python3
"""
Minimal test script - tests only working components
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_openai_only():
    """Test just OpenAI to make sure it works"""
    print("🤖 Testing OpenAI API only...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Test with a simple request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Write a 50-word summary about AI automation"}],
            max_tokens=100
        )
        
        print("✅ OpenAI API working!")
        print(f"Generated content: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API failed: {e}")
        return False

def test_rss_only():
    """Test just RSS feeds"""
    print("\n📡 Testing RSS feeds only...")
    
    try:
        import feedparser
        import requests
        
        url = "https://techcrunch.com/feed/"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        feed = feedparser.parse(response.content)
        
        if feed.entries:
            print(f"✅ RSS working! Found {len(feed.entries)} entries")
            print(f"First: {feed.entries[0].title[:50]}...")
            return True
        else:
            print("❌ No RSS entries found")
            return False
            
    except Exception as e:
        print(f"❌ RSS failed: {e}")
        return False

def main():
    """Run minimal tests"""
    print("🧪 Running minimal tests...\n")
    
    openai_ok = test_openai_only()
    rss_ok = test_rss_only()
    
    print(f"\n📊 Results:")
    print(f"OpenAI: {'✅' if openai_ok else '❌'}")
    print(f"RSS: {'✅' if openai_ok else '❌'}")
    
    if openai_ok and rss_ok:
        print("\n🎉 Core components working! Ready to test full automation.")
        print("Run: python3 main_improved.py")
    else:
        print("\n⚠️ Some core components failed. Check the errors above.")

if __name__ == "__main__":
    main()

