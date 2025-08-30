import feedparser
from openai import OpenAI
from notion_client import Client as NotionClient
from wordpress_xmlrpc import Client as WPClient
from wordpress_xmlrpc.methods.posts import NewPost
import requests
from dotenv import load_dotenv
import os
import ssl
import urllib3
import json
from datetime import datetime

# Disable SSL warnings for testing (remove in production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()  # Load variables from .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
WP_URL = os.getenv("WP_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_SSL_VERIFY = os.getenv("WP_SSL_VERIFY", "true").lower() == "true"

# Use today's fresh RSS content from our content generator
RSS_URLS = [
    "https://techcrunch.com/feed/",
    "https://venturebeat.com/feed/",
    "https://artificialintelligence-news.com/feed/",
    "https://www.technologyreview.com/topic/artificial-intelligence/feed"
]

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
notion_client = NotionClient(auth=NOTION_API_KEY)

# Initialize WordPress client with SSL verification disabled to handle certificate issues
try:
    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Try to initialize WordPress client
    wp_client = WPClient(WP_URL, WP_USERNAME, WP_APP_PASSWORD)
    print("✅ WordPress client initialized successfully")
except Exception as e:
    print(f"❌ Error initializing WordPress client: {e}")
    print("⚠️ WordPress publishing will be disabled, but content will still be generated")
    wp_client = None

def fetch_rss_content():
    """Fetch content from RSS feeds with fallback options"""
    for url in RSS_URLS:
        try:
            print(f"Trying RSS feed: {url}")
            
            # Add user-agent to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            if feed.entries and len(feed.entries) > 0:
                print(f"✅ Successfully fetched {len(feed.entries)} entries from {url}")
                return feed.entries[:3]  # Limit to 3 entries for testing
                
        except Exception as e:
            print(f"❌ Failed to fetch from {url}: {e}")
            continue
    
    print("❌ All RSS feeds failed. Using fallback content.")
    return None

def generate_article(title, description):
    """Generate article using OpenAI"""
    try:
        article_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user", 
                "content": f"Generate a 300-word blog article based on this tech news: Title: {title}. Description: {description}. Include SEO keywords like 'trending 2025', headings, and bullet points. Make it original and engaging."
            }],
            max_tokens=500
        )
        return article_response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error generating article: {e}")
        return f"Article about: {title}\n\n{description}\n\nThis is a placeholder article generated due to an error in the AI service."

def generate_image(title, description):
    """Generate image using DALL-E"""
    try:
        # Shorten the prompt to avoid length issues
        short_description = description[:200] if len(description) > 200 else description
        prompt = f"{title[:50]} - AI technology illustration, vibrant digital art"
        
        image_response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        return image_response.data[0].url
    except Exception as e:
        print(f"❌ Error generating image: {e}")
        return "https://via.placeholder.com/1024x1024/007bff/ffffff?text=AI+Generated+Image"

def save_to_notion(title, article, image_url):
    """Save content to Notion"""
    try:
        # Format the database ID properly (add hyphens if missing)
        db_id = NOTION_DATABASE_ID
        if len(db_id) == 32 and '-' not in db_id:
            db_id = f"{db_id[:8]}-{db_id[8:12]}-{db_id[12:16]}-{db_id[16:20]}-{db_id[20:32]}"
        
        # Truncate content to fit Notion's limits
        truncated_article = article[:1900] + "..." if len(article) > 1900 else article
        
        notion_client.pages.create(
            parent={"database_id": db_id},
            properties={
                "Title": {"title": [{"text": {"content": title}}]},
                "Content": {"rich_text": [{"text": {"content": truncated_article}}]},
                "Image URL": {"url": image_url},
                "Status": {"select": {"name": "Draft"}}
            }
        )
        print(f"✅ Saved to Notion: {title}")
        return True
    except Exception as e:
        print(f"❌ Error saving to Notion: {e}")
        return False

def publish_to_wordpress(title, article, image_url):
    """Publish to WordPress"""
    if wp_client is None:
        print("⚠️ WordPress client not available, skipping WordPress publishing")
        return False
        
    try:
        post = {
            'title': title,
            'content': f"{article}\n\n<img src='{image_url}' alt='{title}' style='max-width: 100%; height: auto;'>",
            'status': 'draft'  # Changed to draft for safety during testing
        }
        wp_client.call(NewPost(post))
        print(f"✅ Published to WordPress: {title}")
        return True
    except Exception as e:
        print(f"❌ Error publishing to WordPress: {e}")
        return False

def main():
    """Main automation workflow"""
    print("🚀 Starting AI Content Automation...")
    
    # Load today's fresh RSS content from our content generator
    today = datetime.now().strftime("%Y-%m-%d")
    content_file = f"content_for_mytribal/mytribal_stories_{today}.json"
    
    try:
        with open(content_file, 'r', encoding='utf-8') as f:
            today_stories = json.load(f)
        print(f"✅ Loaded {len(today_stories)} fresh stories from today")
        
        # Convert to the format expected by the rest of the script
        entries = []
        for story in today_stories:
            entry = type('Entry', (), {
                'title': story['mytribal_adaptation']['suggested_title'],
                'contentSnippet': story['content']['summary'],
                'summary': story['content']['summary']
            })()
            entries.append(entry)
            
    except FileNotFoundError:
        print(f"❌ No content file found for today: {content_file}")
        print("Running RSS content generator first...")
        # Fetch RSS content as fallback
        entries = fetch_rss_content()
        if not entries:
            print("❌ No content to process. Exiting.")
            return
    except Exception as e:
        print(f"❌ Error loading today's content: {e}")
        print("Falling back to RSS feeds...")
        entries = fetch_rss_content()
        if not entries:
            print("❌ No content to process. Exiting.")
            return
    
    success_count = 0
    
    for i, entry in enumerate(entries, 1):
        print(f"\n📝 Processing entry {i}/{len(entries)}")
        print(f"Title: {entry.title}")
        
        title = entry.title
        description = getattr(entry, "contentSnippet", getattr(entry, "summary", "Tech news"))
        
        # Generate article
        print("🤖 Generating article...")
        article = generate_article(title, description)
        
        # Generate image
        print("🎨 Generating image...")
        image_url = generate_image(title, description)
        
        # Save to Notion
        print("📚 Saving to Notion...")
        notion_success = save_to_notion(title, article, image_url)
        
        # Publish to WordPress
        print("🌐 Publishing to WordPress...")
        wp_success = publish_to_wordpress(title, article, image_url)
        
        if notion_success and wp_success:
            success_count += 1
            print(f"✅ Entry {i} completed successfully!")
        else:
            print(f"⚠️ Entry {i} had some issues")
        
        print("-" * 50)
    
    print(f"\n🎉 Automation completed! {success_count}/{len(entries)} entries processed successfully.")
    print("Check Notion and WordPress for the generated content.")

if __name__ == "__main__":
    main()

