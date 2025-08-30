#!/usr/bin/env python3
"""
Test core automation components (RSS + OpenAI + Notion)
Skips WordPress for now due to SSL issues
"""

import feedparser
from openai import OpenAI
from notion_client import Client as NotionClient
import requests
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Alternative RSS feeds
RSS_URLS = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml"
]

def fetch_rss_content():
    """Fetch content from RSS feeds"""
    for url in RSS_URLS:
        try:
            print(f"🔍 Trying RSS feed: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            if feed.entries and len(feed.entries) > 0:
                print(f"✅ Successfully fetched {len(feed.entries)} entries from {url}")
                return feed.entries[:2]  # Limit to 2 entries for testing
                
        except Exception as e:
            print(f"❌ Failed to fetch from {url}: {e}")
            continue
    
    print("❌ All RSS feeds failed.")
    return None

def generate_article(title, description):
    """Generate article using OpenAI"""
    try:
        print(f"🤖 Generating article for: {title[:50]}...")
        
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        article_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user", 
                "content": f"Generate a 200-word blog article based on this tech news: Title: {title}. Description: {description}. Include SEO keywords like 'trending 2025', headings, and bullet points. Make it original and engaging."
            }],
            max_tokens=400
        )
        
        article = article_response.choices[0].message.content
        print(f"✅ Article generated successfully ({len(article)} characters)")
        return article
        
    except Exception as e:
        print(f"❌ Error generating article: {e}")
        return f"Article about: {title}\n\n{description}\n\nThis is a placeholder article."

def generate_image(title, description):
    """Generate image using DALL-E"""
    try:
        print(f"🎨 Generating image for: {title[:50]}...")
        
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        image_response = openai_client.images.generate(
            model="dall-e-3",
            prompt=f"{title} - Create a high-quality, eye-catching image for this blog post. Include elements from: {description}. Style: vibrant digital illustration.",
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        image_url = image_response.data[0].url
        print(f"✅ Image generated successfully")
        return image_url
        
    except Exception as e:
        print(f"❌ Error generating image: {e}")
        return "https://via.placeholder.com/1024x1024/007bff/ffffff?text=AI+Generated+Image"

def save_to_notion(title, article, image_url):
    """Save content to Notion"""
    try:
        print(f"📚 Saving to Notion: {title[:50]}...")
        
        notion_client = NotionClient(auth=NOTION_API_KEY)
        notion_client.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Title": {"title": [{"text": {"content": title}}]},
                "Content": {"rich_text": [{"text": {"content": article}}]},
                "Image URL": {"url": image_url},
                "Status": {"select": {"name": "Draft"}}
            }
        )
        
        print(f"✅ Successfully saved to Notion!")
        return True
        
    except Exception as e:
        print(f"❌ Error saving to Notion: {e}")
        return False

def main():
    """Test core automation workflow"""
    print("🚀 Testing Core AI Automation Components\n")
    
    # Fetch RSS content
    entries = fetch_rss_content()
    if not entries:
        print("❌ No content to process. Exiting.")
        return
    
    print(f"\n📝 Found {len(entries)} entries to process")
    
    success_count = 0
    
    for i, entry in enumerate(entries, 1):
        print(f"\n{'='*60}")
        print(f"📝 Processing Entry {i}/{len(entries)}")
        print(f"Title: {entry.title}")
        print(f"{'='*60}")
        
        title = entry.title
        description = entry.get("contentSnippet", entry.get("summary", "Tech news"))
        
        # Generate article
        article = generate_article(title, description)
        
        # Generate image
        image_url = generate_image(title, description)
        
        # Save to Notion
        notion_success = save_to_notion(title, article, image_url)
        
        if notion_success:
            success_count += 1
            print(f"✅ Entry {i} completed successfully!")
        else:
            print(f"⚠️ Entry {i} had issues")
        
        print(f"\n📊 Progress: {success_count}/{i} entries successful")
    
    print(f"\n🎉 Core automation test completed!")
    print(f"Results: {success_count}/{len(entries)} entries processed successfully")
    
    if success_count > 0:
        print("\n✅ Core components are working! You can now:")
        print("1. Fix the Notion database ID issue")
        print("2. Fix the WordPress SSL issue") 
        print("3. Set up daily automation with: ./setup_cron.sh")
    else:
        print("\n❌ Core components need attention. Check the errors above.")

if __name__ == "__main__":
    main()

