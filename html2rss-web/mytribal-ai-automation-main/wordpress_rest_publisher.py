#!/usr/bin/env python3
"""
WordPress REST API Publisher for MyTribal AI
Posts content using WordPress REST API instead of XML-RPC
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

# RSS feed mapping to WordPress categories
RSS_CATEGORY_MAPPING = {
    "https://techcrunch.com/feed/": "AI Technology",
    "https://venturebeat.com/feed/": "AI Technology", 
    "https://artificialintelligence-news.com/feed/": "AI Technology",
    "https://www.technologyreview.com/topic/artificial-intelligence/feed": "AI Technology",
    # Deaf Technology and Accessibility sources
    "https://deaftechnews.com/feed/": "Deaf Technology",
    "https://assistivetechnology.org/feed/": "Assistive Technology",
    "https://accessibility.com/feed/": "Accessibility",
    "https://www.reddit.com/r/deaf/.rss": "Deaf Technology",
    "https://www.reddit.com/r/accessibility/.rss": "Accessibility"
}

def create_auth_header():
    """Create Basic Auth header for WordPress REST API"""
    if not WP_USERNAME or not WP_APP_PASSWORD:
        return None
    
    # Create base64 encoded credentials
    credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded_credentials}"

def get_or_create_category(category_name):
    """Get existing category or create new one"""
    try:
        # Disable SSL verification
        ssl._create_default_https_context = ssl._create_unverified_context
        
        auth_header = create_auth_header()
        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }
        
        # First, try to find existing category
        search_url = f"{WP_URL}/wp-json/wp/v2/categories?search={category_name}"
        response = requests.get(search_url, headers=headers, verify=False)
        
        if response.status_code == 200:
            categories = response.json()
            for cat in categories:
                if cat.get('name', '').lower() == category_name.lower():
                    print(f"✅ Using existing category: {category_name} (ID: {cat['id']})")
                    return cat['id']
        
        # Create new category if not found
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

def test_wordpress_connection():
    """Test WordPress REST API connection"""
    print("🔍 Testing WordPress REST API Connection...")
    
    auth_header = create_auth_header()
    if not auth_header:
        print("❌ WordPress credentials not found")
        return False
    
    try:
        # Disable SSL verification for this request
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # Test endpoint - get current user info
        test_url = f"{WP_URL}/wp-json/wp/v2/users/me"
        
        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }
        
        print(f"🌐 Testing: {test_url}")
        
        response = requests.get(test_url, headers=headers, verify=False, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Connected successfully as: {user_data.get('name', 'Unknown')}")
            print(f"👤 User ID: {user_data.get('id')}")
            print(f"🔐 Capabilities: {', '.join(user_data.get('capabilities', {}).keys())[:100]}...")
            return True
        elif response.status_code == 401:
            print("❌ Authentication failed - check credentials")
            return False
        elif response.status_code == 403:
            print("❌ Access forbidden - check user permissions")
            return False
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

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
        - Keep it around 400-600 words
        - Make it suitable for a tech-savvy audience
        - Include a brief conclusion with a call-to-action
        
        Format the response as clean HTML with proper <p> tags for paragraphs, <h3> for subheadings if needed.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a tech writer specializing in AI and technology topics. Write engaging, informative content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
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
        prompt = f"{title[:50]} - AI technology illustration, vibrant digital art, modern tech aesthetic, professional blog header"
        
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

def publish_to_wordpress_rest(title, content, image_url=None, category_name="AI Technology"):
    """Publish content using WordPress REST API"""
    print("📤 Publishing to WordPress via REST API...")
    
    auth_header = create_auth_header()
    if not auth_header:
        print("❌ WordPress credentials not available")
        return False
    
    try:
        # Disable SSL verification
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # Get or create category
        category_id = get_or_create_category(category_name)
        
        # Prepare post data
        post_content = content
        
        # Add image if available
        if image_url:
            post_content = f'<img src="{image_url}" alt="{title}" style="max-width: 100%; height: auto; margin-bottom: 20px;" />\n\n{content}'
        
        post_data = {
            'title': title,
            'content': post_content,
            'status': 'publish',
            'categories': [category_id],
            # Skip tags for now to avoid the integer issue
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
        
        if response.status_code == 201:  # Created
            post_data = response.json()
            post_id = post_data.get('id')
            post_url = post_data.get('link')
            print(f"✅ Post published successfully!")
            print(f"   Post ID: {post_id}")
            print(f"   URL: {post_url}")
            return True
        else:
            print(f"❌ Failed to publish post")
            print(f"Response: {response.text[:300]}...")
            return False
            
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
    """Create sample content for testing"""
    sample_stories = [
        {
            "mytribal_adaptation": {
                "suggested_title": "Breaking: AI Achieves New Milestone in Natural Language Understanding",
                "story_angle": "Latest AI breakthrough demonstrates human-level comprehension in complex reasoning tasks"
            },
            "content": {
                "summary": "Researchers have developed an AI system that demonstrates unprecedented natural language understanding, marking a significant step toward artificial general intelligence."
            }
        }
    ]
    return sample_stories

def main():
    """Main publishing workflow"""
    print("🚀 Starting WordPress REST API Publisher for MyTribal AI...")
    print("=" * 70)
    
    # Test WordPress connection
    if not test_wordpress_connection():
        print("❌ Cannot proceed without WordPress connection")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check your .env file has correct WordPress credentials")
        print("2. Ensure WordPress REST API is enabled (it usually is by default)")
        print("3. Verify your application password is correct")
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
        print(f"📄 Description: {description[:100]}...")
        
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
        if publish_to_wordpress_rest(title, article, image_url, "AI Technology"):
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
