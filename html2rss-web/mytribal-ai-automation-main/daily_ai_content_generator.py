#!/usr/bin/env python3
"""
Daily AI Content Generator
Pulls data FROM external RSS feeds and prepares it for publishing TO mytribal.ai website
"""

import feedparser
import requests
from datetime import datetime, timedelta
import json
import time
import os
import logging
from pathlib import Path
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_ai_content_generator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# External RSS feeds to pull content FROM
EXTERNAL_RSS_SOURCES = {
    'tech_crunch': {
        'url': 'https://techcrunch.com/feed/',
        'category': 'tech_news',
        'weight': 0.9,
        'max_entries': 10
    },
    'venture_beat': {
        'url': 'https://venturebeat.com/feed/',
        'category': 'tech_news',
        'weight': 0.8,
        'max_entries': 10
    },
    'ai_news': {
        'url': 'https://artificialintelligence-news.com/feed/',
        'category': 'ai_specific',
        'weight': 0.95,
        'max_entries': 15
    },
    'mit_tech_review': {
        'url': 'https://www.technologyreview.com/topic/artificial-intelligence/feed',
        'category': 'ai_research',
        'weight': 0.9,
        'max_entries': 10
    },
    'reddit_ai': {
        'url': 'https://www.reddit.com/r/artificial/hot.rss?limit=10',
        'category': 'community_discussion',
        'weight': 0.7,
        'max_entries': 10
    },
    'hacker_news': {
        'url': 'https://news.ycombinator.com/rss',
        'category': 'tech_community',
        'weight': 0.8,
        'max_entries': 15
    },
    'wired_ai': {
        'url': 'https://www.wired.com/feed/rss',
        'category': 'tech_news',
        'weight': 0.85,
        'max_entries': 10
    },
    'ars_technica': {
        'url': 'https://feeds.arstechnica.com/arstechnica/index',
        'category': 'tech_news',
        'weight': 0.8,
        'max_entries': 10
    }
}

# AI-related keywords to filter content
AI_KEYWORDS = [
    'artificial intelligence', 'AI', 'machine learning', 'ML', 'deep learning',
    'neural network', 'GPT', 'DALL-E', 'ChatGPT', 'OpenAI', 'Google AI',
    'Microsoft AI', 'Meta AI', 'Apple AI', 'quantum computing', 'robotics',
    'automation', 'data science', 'algorithm', 'computer vision', 'NLP',
    'natural language processing', 'autonomous', 'smart', 'intelligent',
    'predictive', 'analytics', 'big data', 'cloud computing', 'edge computing'
]

# Configuration
CONFIG = {
    'data_dir': 'content_for_mytribal',
    'max_stories_per_day': 5,
    'min_ai_relevance_score': 0.6,
    'request_delay': 1,
    'backup_count': 5
}

def ensure_data_directory():
    """Ensure the content directory exists"""
    Path(CONFIG['data_dir']).mkdir(exist_ok=True)
    return CONFIG['data_dir']

def fetch_external_rss_content():
    """Fetch content FROM external RSS feeds"""
    logger.info("🔍 Fetching content FROM external RSS feeds...")
    
    all_external_content = []
    
    for source_name, source_info in EXTERNAL_RSS_SOURCES.items():
        try:
            logger.info(f"📡 Fetching FROM: {source_name}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(source_info['url'], headers=headers, timeout=15)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            if feed.entries:
                logger.info(f"✅ Found {len(feed.entries)} entries FROM {source_name}")
                
                # Process entries up to max limit
                for entry in feed.entries[:source_info['max_entries']]:
                    # Calculate AI relevance score
                    ai_relevance = calculate_ai_relevance(entry.title, entry.get('summary', ''))
                    
                    if ai_relevance >= CONFIG['min_ai_relevance_score']:
                        content_entry = {
                            'title': entry.title,
                            'link': entry.get('link', ''),
                            'summary': entry.get('summary', entry.get('contentSnippet', '')),
                            'published': entry.get('published', entry.get('updated', '')),
                            'source_name': source_name,
                            'source_url': source_info['url'],
                            'category': source_info['category'],
                            'weight': source_info['weight'],
                            'ai_relevance_score': ai_relevance,
                            'timestamp': datetime.now().isoformat(),
                            'ready_for_mytribal': True
                        }
                        
                        # Parse publication date
                        try:
                            if content_entry['published']:
                                if 'T' in content_entry['published']:
                                    pub_date = datetime.fromisoformat(content_entry['published'].replace('Z', '+00:00'))
                                else:
                                    # Handle RSS date format
                                    pub_date = datetime.strptime(content_entry['published'], '%a, %d %b %Y %H:%M:%S %z')
                                
                                content_entry['parsed_date'] = pub_date.isoformat()
                                content_entry['days_old'] = (datetime.now(pub_date.tzinfo) - pub_date).days
                            else:
                                content_entry['parsed_date'] = None
                                content_entry['days_old'] = 999  # Default to old content
                                
                        except Exception as e:
                            logger.warning(f"Could not parse date for entry: {entry.title[:50]}... Error: {e}")
                            content_entry['parsed_date'] = None
                            content_entry['days_old'] = 999  # Default to old content
                        
                        all_external_content.append(content_entry)
                        
                        logger.info(f"   📝 AI Content: {entry.title[:60]}... (Score: {ai_relevance:.2f})")
                    else:
                        logger.debug(f"   ⚠️ Low AI relevance: {entry.title[:60]}... (Score: {ai_relevance:.2f})")
                
            else:
                logger.warning(f"❌ No entries found FROM {source_name}")
                
        except Exception as e:
            logger.error(f"❌ Error fetching FROM {source_name}: {e}")
            continue
        
        time.sleep(CONFIG['request_delay'])
    
    logger.info(f"📥 Total AI-relevant content fetched: {len(all_external_content)}")
    return all_external_content

def calculate_ai_relevance(title, summary):
    """Calculate how relevant content is to AI topics"""
    text = f"{title} {summary}".lower()
    
    # Count AI keyword matches
    ai_matches = 0
    for keyword in AI_KEYWORDS:
        if keyword.lower() in text:
            ai_matches += 1
    
    # Calculate relevance score (0.0 to 1.0)
    if ai_matches == 0:
        return 0.0
    elif ai_matches >= 5:
        return 1.0
    else:
        return min(ai_matches / 5.0, 1.0)

def filter_and_rank_content(content_entries):
    """Filter and rank content for mytribal.ai publishing"""
    logger.info("🔍 Filtering and ranking content for mytribal.ai...")
    
    # Filter by relevance and recency
    filtered_content = []
    for entry in content_entries:
        # Must meet minimum AI relevance
        if entry['ai_relevance_score'] >= CONFIG['min_ai_relevance_score']:
            # Prefer recent content (within last 7 days)
            if entry.get('days_old', 999) <= 7:
                entry['priority_score'] = entry['ai_relevance_score'] * entry['weight'] * 1.5
            else:
                entry['priority_score'] = entry['ai_relevance_score'] * entry['weight']
            
            filtered_content.append(entry)
    
    # Sort by priority score (highest first)
    filtered_content.sort(key=lambda x: x['priority_score'], reverse=True)
    
    # Limit to max stories per day
    top_content = filtered_content[:CONFIG['max_stories_per_day']]
    
    logger.info(f"✅ Selected {len(top_content)} top stories for mytribal.ai")
    return top_content

def create_mytribal_story_outlines(selected_content):
    """Create story outlines ready for mytribal.ai publishing"""
    logger.info("📝 Creating story outlines for mytribal.ai...")
    
    story_outlines = []
    
    for i, content in enumerate(selected_content, 1):
        outline = {
            'story_number': i,
            'priority_score': content['priority_score'],
            'ai_relevance_score': content['ai_relevance_score'],
            'source_info': {
                'name': content['source_name'],
                'url': content['source_url'],
                'category': content['category']
            },
            'content': {
                'title': content['title'],
                'summary': content['summary'],
                'original_link': content['link'],
                'published_date': content['published']
            },
            'mytribal_adaptation': {
                'suggested_title': adapt_title_for_mytribal(content['title']),
                'story_angle': generate_story_angle(content),
                'key_points': extract_key_points(content['summary']),
                'seo_keywords': extract_seo_keywords(content),
                'target_audience': determine_target_audience(content)
            },
            'publishing_ready': True,
            'timestamp': datetime.now().isoformat()
        }
        
        story_outlines.append(outline)
        
        logger.info(f"   📚 Story {i}: {outline['mytribal_adaptation']['suggested_title'][:60]}...")
    
    return story_outlines

def adapt_title_for_mytribal(original_title):
    """Adapt external titles for mytribal.ai style"""
    # Remove source-specific prefixes
    title = original_title
    prefixes_to_remove = ['TechCrunch:', 'VentureBeat:', 'MIT:', 'Reddit:', 'Hacker News:']
    
    for prefix in prefixes_to_remove:
        if title.startswith(prefix):
            title = title[len(prefix):].strip()
    
    # Add mytribal.ai style if needed
    if not any(word in title.lower() for word in ['ai', 'artificial intelligence', 'machine learning']):
        title = f"AI Update: {title}"
    
    return title

def generate_story_angle(content):
    """Generate a story angle for mytribal.ai"""
    category = content['category']
    ai_score = content['ai_relevance_score']
    
    if category == 'ai_research':
        return "Research breakthrough with real-world implications"
    elif category == 'ai_specific':
        return "Direct AI development and its impact on technology"
    elif category == 'tech_news':
        return "AI technology making waves in the industry"
    elif category == 'community_discussion':
        return "Community insights on AI development and trends"
    else:
        return "AI innovation and its broader technological impact"

def extract_key_points(summary):
    """Extract key points from content summary"""
    # Simple key point extraction
    sentences = summary.split('.')
    key_points = []
    
    for sentence in sentences[:3]:  # First 3 sentences
        sentence = sentence.strip()
        if len(sentence) > 20:  # Only meaningful sentences
            key_points.append(sentence)
    
    return key_points

def extract_seo_keywords(content):
    """Extract SEO keywords for mytribal.ai"""
    text = f"{content['title']} {content['summary']}".lower()
    
    # Find AI-related keywords
    found_keywords = []
    for keyword in AI_KEYWORDS:
        if keyword.lower() in text:
            found_keywords.append(keyword)
    
    # Add trending terms
    trending_terms = ['2025', 'trending', 'latest', 'breakthrough', 'innovation']
    for term in trending_terms:
        if term.lower() in text:
            found_keywords.append(term)
    
    return list(set(found_keywords))[:10]  # Limit to 10 keywords

def determine_target_audience(content):
    """Determine target audience for the content"""
    category = content['category']
    ai_score = content['ai_relevance_score']
    
    if ai_score >= 0.9:
        return "AI professionals and researchers"
    elif ai_score >= 0.8:
        return "Tech enthusiasts and developers"
    elif ai_score >= 0.7:
        return "General tech audience"
    else:
        return "Curious readers interested in technology"

def save_content_for_mytribal(data_dir, story_outlines, raw_content):
    """Save content ready for mytribal.ai publishing"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Save story outlines
    outlines_file = Path(data_dir) / f"mytribal_stories_{today}.json"
    with open(outlines_file, 'w', encoding='utf-8') as f:
        json.dump(story_outlines, f, indent=2, ensure_ascii=False, default=str)
    
    # Save raw content for reference
    raw_file = Path(data_dir) / f"raw_content_{today}.json"
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(raw_content, f, indent=2, ensure_ascii=False, default=str)
    
    logger.info(f"💾 Content saved for mytribal.ai publishing:")
    logger.info(f"   Story outlines: {outlines_file}")
    logger.info(f"   Raw content: {raw_file}")
    
    return outlines_file, raw_file

def main():
    """Main content generation workflow"""
    logger.info("🚀 Starting Daily AI Content Generator for mytribal.ai...")
    start_time = datetime.now()
    
    try:
        # Ensure data directory exists
        data_dir = ensure_data_directory()
        
        # Fetch content FROM external RSS feeds
        external_content = fetch_external_rss_content()
        
        if not external_content:
            logger.warning("❌ No external content found. Exiting.")
            return
        
        # Filter and rank content for mytribal.ai
        selected_content = filter_and_rank_content(external_content)
        
        if not selected_content:
            logger.warning("❌ No suitable content selected for mytribal.ai. Exiting.")
            return
        
        # Create story outlines for mytribal.ai
        story_outlines = create_mytribal_story_outlines(selected_content)
        
        # Save content ready for mytribal.ai publishing
        outlines_file, raw_file = save_content_for_mytribal(data_dir, story_outlines, external_content)
        
        # Display summary
        logger.info("\n📊 Content Generation Summary:")
        logger.info(f"   Date: {datetime.now().strftime('%Y-%m-%d')}")
        logger.info(f"   External sources checked: {len(EXTERNAL_RSS_SOURCES)}")
        logger.info(f"   Total content fetched: {len(external_content)}")
        logger.info(f"   Content selected for mytribal.ai: {len(selected_content)}")
        logger.info(f"   Story outlines created: {len(story_outlines)}")
        
        logger.info(f"\n🎯 Content ready for mytribal.ai publishing!")
        logger.info(f"   Check: {outlines_file}")
        logger.info(f"   Each story includes: title, summary, key points, SEO keywords, and publishing guidance")
        
    except Exception as e:
        logger.error(f"❌ Fatal error in content generation: {e}")
        raise
    
    finally:
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"⏰ Total runtime: {duration}")

if __name__ == "__main__":
    main()
