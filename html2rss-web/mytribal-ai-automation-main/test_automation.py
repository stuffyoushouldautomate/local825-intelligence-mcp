#!/usr/bin/env python3
"""
Test script for the AI automation workflow
Tests each component individually to identify any issues
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Test if all required environment variables are set"""
    print("🔍 Testing environment variables...")
    
    required_vars = [
        "OPENAI_API_KEY",
        "NOTION_API_KEY", 
        "NOTION_DATABASE_ID",
        "WP_URL",
        "WP_USERNAME",
        "WP_APP_PASSWORD"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f"your_{var.lower()}_here":
            missing_vars.append(var)
            print(f"❌ {var}: Not set or using template value")
        else:
            print(f"✅ {var}: Set (length: {len(value)})")
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with your actual API keys and credentials")
        return False
    
    print("✅ All environment variables are set!")
    return True

def test_dependencies():
    """Test if all required Python packages are installed"""
    print("\n🔍 Testing Python dependencies...")
    
    required_packages = [
        "feedparser",
        "openai", 
        "notion_client",
        "wordpress_xmlrpc",
        "requests",
        "dotenv"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: Installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}: Not installed")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n🔍 Testing OpenAI API connection...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Test with a simple request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello, automation test!'"}],
            max_tokens=10
        )
        
        print(f"✅ OpenAI API: Connected successfully")
        print(f"   Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API: Connection failed - {e}")
        return False

def test_notion_connection():
    """Test Notion API connection"""
    print("\n🔍 Testing Notion API connection...")
    
    try:
        from notion_client import Client as NotionClient
        client = NotionClient(auth=os.getenv("NOTION_API_KEY"))
        
        # Test by trying to retrieve the database
        database_id = os.getenv("NOTION_DATABASE_ID")
        database = client.databases.retrieve(database_id)
        
        print(f"✅ Notion API: Connected successfully")
        print(f"   Database: {database.get('title', [{}])[0].get('plain_text', 'Untitled')}")
        return True
        
    except Exception as e:
        print(f"❌ Notion API: Connection failed - {e}")
        return False

def test_wordpress_connection():
    """Test WordPress connection"""
    print("\n🔍 Testing WordPress connection...")
    
    try:
        from wordpress_xmlrpc import Client as WPClient
        client = WPClient(
            os.getenv("WP_URL"),
            os.getenv("WP_USERNAME"),
            os.getenv("WP_APP_PASSWORD")
        )
        
        # Test by getting user info
        from wordpress_xmlrpc.methods.users import GetUser
        user = client.call(GetUser(1))
        
        print(f"✅ WordPress: Connected successfully")
        print(f"   Site: {os.getenv('WP_URL')}")
        print(f"   User: {user.get('user_login', 'Unknown')}")
        return True
        
    except Exception as e:
        print(f"❌ WordPress: Connection failed - {e}")
        return False

def test_rss_feed():
    """Test RSS feed fetching"""
    print("\n🔍 Testing RSS feed...")
    
    try:
        import feedparser
        rss_url = "https://www.reddit.com/r/technology/hot.rss?limit=3"
        
        feed = feedparser.parse(rss_url)
        
        if feed.entries:
            print(f"✅ RSS Feed: Successfully fetched {len(feed.entries)} entries")
            print(f"   First entry: {feed.entries[0].title[:50]}...")
            return True
        else:
            print("❌ RSS Feed: No entries found")
            return False
            
    except Exception as e:
        print(f"❌ RSS Feed: Failed to fetch - {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting AI Automation Test Suite\n")
    
    tests = [
        test_environment_variables,
        test_dependencies,
        test_openai_connection,
        test_notion_connection,
        test_wordpress_connection,
        test_rss_feed
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your automation is ready to run.")
        print("You can now run: python3 main.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues before running the full automation.")
        print("Check the error messages above for guidance.")

if __name__ == "__main__":
    main()

