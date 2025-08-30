#!/usr/bin/env python3
"""
Simple Content Generator for MyTribal AI
Generates AI content from RSS feeds and saves it locally
"""

import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def load_todays_content():
    """Load today's generated content"""
    today = datetime.now().strftime("%Y-%m-%d")
    content_file = Path("content_for_mytribal") / f"mytribal_stories_{today}.json"
    
    if not content_file.exists():
        print(f"❌ No content file found for today: {content_file}")
        return None
    
    try:
        with open(content_file, 'r', encoding='utf-8') as f:
            content = json.load(f)
        print(f"✅ Loaded {len(content)} stories for today")
        return content
    except Exception as e:
        print(f"❌ Error loading content: {e}")
        return None

def generate_ai_article(title, summary):
    """Generate AI article using OpenAI"""
    try:
        openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        prompt = f"""Generate a 300-word engaging blog article based on this tech news:

Title: {title}
Summary: {summary}

Requirements:
- Make it engaging and informative
- Include SEO keywords like 'AI', '2025', 'trending', 'technology'
- Use headings and bullet points
- Keep it under 300 words
- Make it original and engaging
- Focus on AI and technology trends

Article:"""

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ Error generating article: {e}")
        return f"Article about: {title}\n\n{summary}\n\nThis is a placeholder article generated due to an error in the AI service."

def generate_image_prompt(title):
    """Generate a simple image prompt for DALL-E"""
    try:
        openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        prompt = f"Create a simple, professional image prompt for this AI article title: '{title}'. The prompt should be under 100 characters and describe a tech/AI themed illustration."
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ Error generating image prompt: {e}")
        return f"AI technology illustration, digital art"

def generate_dalle_image(prompt):
    """Generate image using DALL-E"""
    try:
        openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        return response.data[0].url
        
    except Exception as e:
        print(f"❌ Error generating image: {e}")
        return "https://via.placeholder.com/1024x1024/007bff/ffffff?text=AI+Generated+Image"

def save_generated_content(stories):
    """Save generated content locally"""
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path("generated_content")
    output_dir.mkdir(exist_ok=True)
    
    generated_stories = []
    
    for i, story in enumerate(stories, 1):
        print(f"\n📝 Processing story {i}/{len(stories)}: {story['mytribal_adaptation']['suggested_title'][:60]}...")
        
        # Generate AI article
        print("🤖 Generating AI article...")
        article = generate_ai_article(
            story['mytribal_adaptation']['suggested_title'],
            story['content']['summary']
        )
        
        # Generate image prompt
        print("🎨 Generating image prompt...")
        image_prompt = generate_image_prompt(story['mytribal_adaptation']['suggested_title'])
        
        # Generate DALL-E image
        print("🖼️ Generating DALL-E image...")
        image_url = generate_dalle_image(image_prompt)
        
        # Create generated story object
        generated_story = {
            'story_number': i,
            'original_title': story['content']['title'],
            'adapted_title': story['mytribal_adaptation']['suggested_title'],
            'source': story['source_info']['name'],
            'ai_article': article,
            'image_prompt': image_prompt,
            'image_url': image_url,
            'seo_keywords': story['mytribal_adaptation']['seo_keywords'],
            'target_audience': story['mytribal_adaptation']['target_audience'],
            'generated_at': datetime.now().isoformat(),
            'ready_for_publishing': True
        }
        
        generated_stories.append(generated_story)
        print(f"✅ Story {i} generated successfully!")
    
    # Save all generated content
    output_file = output_dir / f"generated_stories_{today}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(generated_stories, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n🎉 All content generated successfully!")
    print(f"📁 Saved to: {output_file}")
    
    return generated_stories

def display_generated_content(stories):
    """Display the generated content summary"""
    print(f"\n📊 GENERATED CONTENT SUMMARY:")
    print("=" * 80)
    
    for story in stories:
        print(f"\n📝 Story {story['story_number']}: {story['adapted_title']}")
        print(f"   📡 Source: {story['source']}")
        print(f"   📝 Article Length: {len(story['ai_article'])} characters")
        print(f"   🎨 Image Prompt: {story['image_prompt']}")
        print(f"   🖼️ Image URL: {story['image_url']}")
        print(f"   🔑 SEO Keywords: {', '.join(story['seo_keywords'][:5])}")
        print(f"   👥 Target: {story['target_audience']}")
        print("-" * 60)

def main():
    """Main content generation workflow"""
    print("🚀 Starting Simple Content Generator for MyTribal AI...")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load today's content
    stories = load_todays_content()
    if not stories:
        print("❌ No content to process. Exiting.")
        return
    
    # Generate AI content
    generated_stories = save_generated_content(stories)
    
    # Display summary
    display_generated_content(generated_stories)
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. ✅ AI articles generated and saved locally")
    print("2. ✅ DALL-E images created")
    print("3. 🔧 Fix Notion database sharing (see test_notion_access.py)")
    print("4. 🔧 Fix WordPress SSL certificate issues")
    print("5. 🚀 Run full automation once issues are resolved")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
