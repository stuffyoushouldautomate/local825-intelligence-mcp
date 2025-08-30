#!/usr/bin/env python3
"""
Deaf Technology Video Publisher for MyTribal AI
Creates content with AI-generated sign language videos for ASL, French Sign Language, and BSL
"""

import os
import json
import base64
import ssl
from datetime import datetime
import requests
from dotenv import load_dotenv
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

# WordPress configuration
WP_URL = os.getenv("WP_URL", "https://mytribal.ai").rstrip('/')
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Deaf Technology RSS feeds
DEAF_TECH_RSS_FEEDS = [
    "https://www.reddit.com/r/deaf/.rss",
    "https://www.reddit.com/r/accessibility/.rss",
    "https://www.reddit.com/r/assistivetechnology/.rss",
    "https://www.reddit.com/r/DeafEducation/.rss",
    "https://www.reddit.com/r/ASL/.rss"
]

# Sign Language options
SIGN_LANGUAGES = {
    "ASL": "American Sign Language",
    "FSL": "French Sign Language", 
    "BSL": "British Sign Language"
}

def create_auth_header():
    """Create Basic Auth header for WordPress REST API"""
    if not WP_USERNAME or not WP_APP_PASSWORD:
        return None
    
    credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded_credentials}"

def get_or_create_category(category_name):
    """Get existing category or create new one"""
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        
        auth_header = create_auth_header()
        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }
        
        # Search for existing category
        search_url = f"{WP_URL}/wp-json/wp/v2/categories?search={category_name}"
        response = requests.get(search_url, headers=headers, verify=False)
        
        if response.status_code == 200:
            categories = response.json()
            for cat in categories:
                if cat.get('name', '').lower() == category_name.lower():
                    print(f"✅ Using existing category: {category_name} (ID: {cat['id']})")
                    return cat['id']
        
        # Create new category
        create_url = f"{WP_URL}/wp-json/wp/v2/categories"
        category_data = {
            'name': category_name,
            'slug': category_name.lower().replace(' ', '-'),
            'description': f'Content related to {category_name}'
        }
        
        response = requests.post(create_url, headers=headers, data=json.dumps(category_data), verify=False)
        
        if response.status_code == 201:
            new_category = response.json()
            print(f"✅ Created new category: {category_name} (ID: {new_category['id']})")
            return new_category['id']
        else:
            print(f"⚠️ Failed to create category, using default (ID: 1)")
            return 1
            
    except Exception as e:
        print(f"⚠️ Error managing categories: {e}, using default (ID: 1)")
        return 1

def generate_deaf_tech_article(title, description):
    """Generate article focused on Deaf Technology and accessibility"""
    if not OPENAI_API_KEY:
        print("❌ OpenAI API key not found")
        return None
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""
        Create a compelling blog post about this Deaf Technology/accessibility topic:
        
        Title: {title}
        Description: {description}
        
        Requirements:
        - Focus on accessibility and Deaf Technology aspects
        - Include information about how this technology helps the Deaf community
        - Mention sign language considerations (ASL, FSL, BSL)
        - Write in an engaging, informative style
        - Keep it around 400-600 words
        - Include practical applications for Deaf users
        - Add a call-to-action encouraging accessibility awareness
        
        Format the response as clean HTML with <p> tags for paragraphs, <h3> for subheadings.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a tech writer specializing in Deaf Technology, accessibility, and assistive technology. Write engaging content that highlights how technology can improve accessibility for the Deaf community."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        article = response.choices[0].message.content.strip()
        print("✅ Deaf Technology article generated successfully")
        return article
        
    except Exception as e:
        print(f"❌ Error generating article: {e}")
        return None

def generate_sign_language_video_prompt(title, sign_language):
    """Generate a prompt for creating sign language video content"""
    if not OPENAI_API_KEY:
        print("❌ OpenAI API key not found")
        return None
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""
        Create a detailed prompt for generating a sign language video in {sign_language} ({SIGN_LANGUAGES[sign_language]}) for this topic:
        
        Title: {title}
        
        Requirements:
        - Create a prompt for an AI video generation tool
        - Focus on clear, accurate sign language representation
        - Include cultural sensitivity for {sign_language} users
        - Suggest appropriate background and lighting
        - Recommend professional sign language interpreter appearance
        - Keep the prompt under 200 words
        - Make it suitable for video generation tools like RunwayML, Pika Labs, or similar
        
        The prompt should result in a video that shows someone signing the key points of this technology topic in {sign_language}.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are an expert in {sign_language} and Deaf culture. Create prompts for AI video generation that will produce accurate, culturally appropriate sign language content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        video_prompt = response.choices[0].message.content.strip()
        print(f"✅ {sign_language} video prompt generated successfully")
        return video_prompt
        
    except Exception as e:
        print(f"❌ Error generating video prompt: {e}")
        return None

def generate_accessibility_image(title):
    """Generate image focused on accessibility and Deaf Technology"""
    if not OPENAI_API_KEY:
        print("❌ OpenAI API key not found")
        return None
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"{title[:50]} - accessibility technology, Deaf Technology, sign language, inclusive design, modern tech aesthetic, professional blog header"
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        image_url = response.data[0].url
        print("✅ Accessibility-focused image generated successfully")
        return image_url
        
    except Exception as e:
        print(f"❌ Error generating image: {e}")
        return None

def publish_deaf_tech_post(title, content, image_url, video_prompt=None, sign_language="ASL"):
    """Publish Deaf Technology content (video prompts removed for authentic ASL videos)"""
    print(f"📤 Publishing Deaf Technology post in {sign_language}...")
    
    auth_header = create_auth_header()
    if not auth_header:
        print("❌ WordPress credentials not available")
        return False
    
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # Get or create Deaf Technology category
        category_id = get_or_create_category("Deaf Technology")
        
        # Prepare post content with video prompt
        post_content = content
        
        # Add image if available
        if image_url:
            post_content = f'<img src="{image_url}" alt="{title}" style="max-width: 100%; height: auto; margin-bottom: 20px;" />\n\n{content}'
        
        # Video section removed - user will create authentic ASL videos
        # post_content += video_section
        
        post_data = {
            'title': title,
            'content': post_content,
            'status': 'publish',
            'categories': [category_id],
        }
        
        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }
        
        # Post to WordPress
        api_url = f"{WP_URL}/wp-json/wp/v2/posts"
        
        response = requests.post(
            api_url, 
            headers=headers, 
            data=json.dumps(post_data),
            verify=False,
            timeout=60
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 201:
            post_data = response.json()
            post_id = post_data.get('id')
            post_url = post_data.get('link')
            print(f"✅ Deaf Technology post published successfully!")
            print(f"   Post ID: {post_id}")
            print(f"   URL: {post_url}")
            print(f"   Category: Deaf Technology")
            print(f"   Sign Language: {sign_language}")
            return True
        else:
            print(f"❌ Failed to publish post")
            print(f"Response: {response.text[:300]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error publishing to WordPress: {e}")
        return False

def create_deaf_tech_sample_content():
    """Create sample Deaf Technology content for testing"""
    sample_stories = [
        {
            "title": "Revolutionary AI-Powered Sign Language Translation Glasses",
            "description": "New smart glasses use computer vision and AI to provide real-time sign language translation between ASL, FSL, and BSL, breaking down communication barriers.",
            "sign_language": "ASL"
        },
        {
            "title": "Accessible Video Conferencing: AI Captions Meet Sign Language Support",
            "description": "Latest video platforms now include AI-generated captions alongside sign language interpreter support, making virtual meetings accessible to all.",
            "sign_language": "FSL"
        },
        {
            "title": "Deaf-Friendly Smart Home Technology: Visual Alerts and Haptic Feedback",
            "description": "Smart home devices are becoming more accessible with visual notifications, haptic feedback, and sign language voice assistants.",
            "sign_language": "BSL"
        }
    ]
    return sample_stories

def main():
    """Main Deaf Technology publishing workflow"""
    print("🤟 Starting Deaf Technology Video Publisher for MyTribal AI...")
    print("=" * 70)
    print("🎯 Focus: Accessibility, Deaf Technology, and Sign Language Content")
    print("🌍 Supporting: ASL, French Sign Language (FSL), British Sign Language (BSL)")
    print("=" * 70)
    
    # Test WordPress connection
    auth_header = create_auth_header()
    if not auth_header:
        print("❌ Cannot proceed without WordPress credentials")
        return
    
    # Load or create sample content
    stories = create_deaf_tech_sample_content()
    
    print(f"\n📚 Processing {len(stories)} Deaf Technology stories...")
    
    success_count = 0
    for i, story in enumerate(stories, 1):
        print(f"\n--- Processing Story {i}/{len(stories)} ---")
        
        title = story['title']
        description = story['description']
        sign_language = story['sign_language']
        
        print(f"📝 Title: {title}")
        print(f"📄 Description: {description[:100]}...")
        print(f"🤟 Sign Language: {sign_language} ({SIGN_LANGUAGES[sign_language]})")
        
        # Generate Deaf Technology article
        print("🤖 Generating Deaf Technology article...")
        article = generate_deaf_tech_article(title, description)
        if not article:
            print("⚠️ Skipping story due to article generation failure")
            continue
        
        # Generate accessibility-focused image
        print("🎨 Generating accessibility-focused image...")
        image_url = generate_accessibility_image(title)
        
        # Video prompt generation removed - user will create authentic ASL videos
        # print(f"🎥 Generating {sign_language} video prompt...")
        # video_prompt = generate_sign_language_video_prompt(title, article, sign_language)
        
        # Publish to WordPress
        if publish_deaf_tech_post(title, article, image_url, None, sign_language):
            success_count += 1
            print(f"✅ Deaf Technology story {i} published successfully!")
        else:
            print(f"❌ Failed to publish story {i}")
        
        print("-" * 50)
    
    print(f"\n🎉 Deaf Technology Publishing Complete!")
    print(f"✅ Successfully published: {success_count}/{len(stories)} stories")
    
    if success_count > 0:
        print(f"🌐 Check your Deaf Technology category at {WP_URL}/category/deaf-technology/")
        print(f"🤟 Each post includes AI-generated sign language video prompts!")
        print(f"🌍 Supporting ASL, FSL, and BSL content creation")
    else:
        print("❌ No stories were published successfully")

if __name__ == "__main__":
    main()
