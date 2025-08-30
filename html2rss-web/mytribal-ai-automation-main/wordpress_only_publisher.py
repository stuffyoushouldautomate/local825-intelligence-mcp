#!/usr/bin/env python3
"""
WordPress Only Publisher for MyTribal AI
Posts content directly to WordPress, bypassing Notion
"""

import os
import json
from datetime import datetime
from wordpress_xmlrpc import Client as WPClient
from wordpress_xmlrpc.methods.posts import NewPost
import requests
from dotenv import load_dotenv
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

# WordPress configuration
WP_URL = os.getenv("WP_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def initialize_wordpress():
    """Initialize WordPress client with SSL verification disabled"""
    if not all([WP_URL, WP_USERNAME, WP_APP_PASSWORD]):
        print("❌ WordPress environment variables not found")
        return None
    
    try:
        # Disable SSL verification globally for this script
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # Ensure the URL has the proper XML-RPC endpoint
        wp_url = WP_URL.rstrip('/')
        if not wp_url.endswith('/xmlrpc.php'):
            wp_url += '/xmlrpc.php'
        
        print(f"🔗 Connecting to WordPress at: {wp_url}")
        wp_client = WPClient(wp_url, WP_USERNAME, WP_APP_PASSWORD)
        print("✅ WordPress client initialized successfully")
        return wp_client
        
    except Exception as e:
        print(f"❌ Error initializing WordPress client: {e}")
        return None

def generate_article_with_openai(title, description):
    """Generate article using OpenAI"""
    if not OPENAI_API_KEY:
        print("❌ OpenAI API key not found")
        return None
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""
        Create a compelling blog post about this AI/tech topic:
        
        Title: {title}
        Description: {description}
        
        Requirements:
        - Write in an engaging, informative style
        - Include 3-4 key points or insights
        - Add relevant examples or context
        - Keep it around 300-500 words
        - Make it suitable for a tech-savvy audience
        - Include a call-to-action at the end
        
        Format the response as clean HTML with <p> tags for paragraphs.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a tech writer specializing in AI and technology topics."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        article = response.choices[0].message.content.strip()
        print("✅ Article generated successfully")
        return article
        
    except Exception as e:
        print(f"❌ Error generating article: {e}")
        return None

def generate_image_with_dalle(title):
    """Generate image using DALL-E"""
    if not OPENAI_API_KEY:
        print("❌ OpenAI API key not found")
        return None
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Create a short, focused prompt
        prompt = f"{title[:50]} - AI technology illustration, vibrant digital art, modern tech aesthetic"
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        image_url = response.data[0].url
        print("✅ Image generated successfully")
        return image_url
        
    except Exception as e:
        print(f"❌ Error generating image: {e}")
        return None

def publish_to_wordpress(wp_client, title, article, image_url=None):
    """Publish content to WordPress"""
    if not wp_client:
        print("❌ WordPress client not available")
        return False
    
    try:
        # Prepare the post content
        post_content = article
        
        # Add image if available
        if image_url:
            post_content += f'\n\n<img src="{image_url}" alt="{title}" style="max-width: 100%; height: auto; margin: 20px 0;" />'
        
        # Create the post
        post = NewPost()
        post.title = title
        post.content = post_content
        post.post_status = 'publish'
        post.terms_names = {
            'category': ['AI', 'Technology', 'News']
        }
        
        # Publish the post
        post_id = wp_client.call(post)
        print(f"✅ Post published successfully! Post ID: {post_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error publishing to WordPress: {e}")
        return False

def load_todays_content():
    """Load today's generated content"""
    today = datetime.now().strftime("%Y-%m-%d")
    content_file = f"content_for_mytribal/mytribal_stories_{today}.json"
    
    try:
        with open(content_file, 'r', encoding='utf-8') as f:
            today_stories = json.load(f)
        print(f"✅ Loaded {len(today_stories)} stories from today")
        return today_stories
        
    except FileNotFoundError:
        print(f"❌ No content file found for today: {content_file}")
        return None
    except Exception as e:
        print(f"❌ Error loading content: {e}")
        return None

def create_sample_content():
    """Create sample content for testing if no content file exists"""
    sample_stories = [
        {
            "mytribal_adaptation": {
                "suggested_title": "AI Breakthrough: New Language Model Shows Human-Like Reasoning",
                "story_angle": "Recent developments in AI language models demonstrate unprecedented reasoning capabilities"
            },
            "content": {
                "summary": "A new AI language model has demonstrated human-like reasoning abilities, marking a significant milestone in artificial intelligence development."
            }
        },
        {
            "mytribal_adaptation": {
                "suggested_title": "Quantum Computing Meets AI: Revolutionary Applications Emerge",
                "story_angle": "The intersection of quantum computing and AI opens new possibilities for solving complex problems"
            },
            "content": {
                "summary": "Researchers are exploring how quantum computing can enhance AI capabilities, leading to breakthroughs in optimization and machine learning."
            }
        }
    ]
    return sample_stories

def main():
    """Main publishing workflow"""
    print("🚀 Starting WordPress-Only Publisher for MyTribal AI...")
    print("=" * 60)
    
    # Initialize WordPress
    wp_client = initialize_wordpress()
    if not wp_client:
        print("❌ Cannot proceed without WordPress connection")
        return
    
    # Load today's content
    stories = load_todays_content()
    if not stories:
        print("📝 No content file found, using sample content for testing...")
        stories = create_sample_content()
    
    print(f"\n📚 Processing {len(stories)} stories...")
    
    success_count = 0
    for i, story in enumerate(stories, 1):
        print(f"\n--- Processing Story {i}/{len(stories)} ---")
        
        title = story['mytribal_adaptation']['suggested_title']
        description = story['content']['summary']
        
        print(f"📝 Title: {title}")
        print(f"📄 Description: {description}")
        
        # Generate article
        print("🤖 Generating article...")
        article = generate_article_with_openai(title, description)
        if not article:
            print("⚠️ Skipping story due to article generation failure")
            continue
        
        # Generate image
        print("🎨 Generating image...")
        image_url = generate_image_with_dalle(title)
        
        # Publish to WordPress
        print("📤 Publishing to WordPress...")
        if publish_to_wordpress(wp_client, title, article, image_url):
            success_count += 1
            print(f"✅ Story {i} published successfully!")
        else:
            print(f"❌ Failed to publish story {i}")
        
        print("-" * 50)
    
    print(f"\n🎉 Publishing Complete!")
    print(f"✅ Successfully published: {success_count}/{len(stories)} stories")
    
    if success_count > 0:
        print(f"🌐 Check your website at {WP_URL} to see the new posts!")
    else:
        print("❌ No stories were published successfully")

if __name__ == "__main__":
    main()
