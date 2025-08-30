#!/usr/bin/env python3
"""
Publish Fresh RSS Content to mytribal.ai
Takes the daily AI content and publishes it to the website
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('publish_to_mytribal.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_todays_content():
    """Load today's generated content for publishing"""
    today = datetime.now().strftime("%Y-%m-%d")
    content_file = Path("content_for_mytribal") / f"mytribal_stories_{today}.json"
    
    if not content_file.exists():
        logger.error(f"❌ No content file found for today: {content_file}")
        return None
    
    try:
        with open(content_file, 'r', encoding='utf-8') as f:
            content = json.load(f)
        logger.info(f"✅ Loaded {len(content)} stories for publishing")
        return content
    except Exception as e:
        logger.error(f"❌ Error loading content: {e}")
        return None

def check_environment_setup():
    """Check if required environment variables are set"""
    required_vars = [
        'OPENAI_API_KEY',
        'NOTION_API_KEY', 
        'NOTION_DATABASE_ID',
        'WP_URL',
        'WP_USERNAME',
        'WP_APP_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these in your .env file")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True

def create_publishing_plan(stories):
    """Create a plan for publishing the stories"""
    logger.info("📋 Creating publishing plan...")
    
    plan = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'total_stories': len(stories),
        'publishing_order': [],
        'estimated_time': len(stories) * 3,  # 3 minutes per story
        'status': 'ready'
    }
    
    for i, story in enumerate(stories, 1):
        story_plan = {
            'story_number': i,
            'title': story['mytribal_adaptation']['suggested_title'],
            'source': story['source_info']['name'],
            'ai_relevance_score': story['ai_relevance_score'],
            'priority_score': story['priority_score'],
            'target_audience': story['mytribal_adaptation']['target_audience'],
            'seo_keywords': story['mytribal_adaptation']['seo_keywords'],
            'publishing_status': 'pending'
        }
        
        plan['publishing_order'].append(story_plan)
        
        logger.info(f"   📝 Story {i}: {story_plan['title'][:60]}...")
        logger.info(f"      Source: {story_plan['source']}")
        logger.info(f"      AI Score: {story_plan['ai_relevance_score']:.2f}")
        logger.info(f"      Target: {story_plan['target_audience']}")
    
    return plan

def display_publishing_summary(plan):
    """Display the publishing plan summary"""
    print("\n" + "=" * 80)
    print("🚀 PUBLISHING PLAN FOR MYTRIBAL.AI")
    print("=" * 80)
    print(f"📅 Date: {plan['date']}")
    print(f"📊 Total Stories: {plan['total_stories']}")
    print(f"⏰ Estimated Time: {plan['estimated_time']} minutes")
    print(f"📋 Status: {plan['status']}")
    
    print(f"\n📝 STORIES TO PUBLISH:")
    print("-" * 60)
    
    for story in plan['publishing_order']:
        print(f"\n{story['story_number']}. {story['title']}")
        print(f"   📡 Source: {story['source']}")
        print(f"   🎯 AI Relevance: {story['ai_relevance_score']:.2f}")
        print(f"   📊 Priority Score: {story['priority_score']:.2f}")
        print(f"   👥 Target Audience: {story['target_audience']}")
        print(f"   🔑 SEO Keywords: {', '.join(story['seo_keywords'][:5])}")
        print(f"   📤 Status: {story['publishing_status']}")
        print("-" * 40)

def show_next_steps():
    """Show the next steps to actually publish the content"""
    print(f"\n🎯 NEXT STEPS TO PUBLISH TO MYTRIBAL.AI:")
    print("=" * 80)
    
    steps = [
        "1. 📋 Set up your .env file with API keys (if not already done)",
        "2. 🤖 Run the main automation script: python3 main_improved.py",
        "3. 📚 The script will use today's RSS content to generate articles",
        "4. 🎨 DALL-E will create custom images for each story",
        "5. 📝 OpenAI will generate full articles based on the RSS content",
        "6. 🌐 Content will be published to your mytribal.ai website",
        "7. 📊 Articles will appear with today's date (August 19, 2025)"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print(f"\n⚡ QUICK START:")
    print("-" * 50)
    print("• Run: python3 main_improved.py")
    print("• This will use today's fresh RSS content")
    print("• Generate and publish 5 new AI stories")
    print("• All with today's date and fresh content")
    
    print(f"\n🔍 WHY YOU'RE SEEING OLD CONTENT:")
    print("-" * 50)
    print("• Your website currently shows August 2nd content")
    print("• Our script found fresh content from today (August 19th)")
    print("• We need to run the publishing automation to update your site")
    print("• The automation will replace old content with fresh stories")

def main():
    """Main publishing workflow"""
    logger.info("🚀 Starting Publishing Plan for mytribal.ai...")
    
    # Check environment setup
    if not check_environment_setup():
        logger.error("❌ Environment not properly configured. Please set up your .env file.")
        return
    
    # Load today's content
    stories = load_todays_content()
    if not stories:
        logger.error("❌ No content found for publishing today.")
        return
    
    # Create publishing plan
    plan = create_publishing_plan(stories)
    
    # Display summary
    display_publishing_summary(plan)
    
    # Show next steps
    show_next_steps()
    
    logger.info("✅ Publishing plan created successfully!")
    logger.info("🎯 Ready to publish fresh content to mytribal.ai")

if __name__ == "__main__":
    main()
