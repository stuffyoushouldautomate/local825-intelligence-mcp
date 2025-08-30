#!/usr/bin/env python3
"""
Enhanced mytribal.ai RSS Automation Script
Adds additional context sources for richer AI story generation
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
        logging.FileHandler('mytribal_rss_enhanced.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Primary RSS feeds from mytribal.ai
MYTRIBAL_RSS_FEEDS = [
    "https://mytribal.ai/feed/",
    "https://mytribal.ai/feed/rss/",
    "https://mytribal.ai/feed/atom/",
    "https://mytribal.ai/feed/rss2/"
]

# Additional AI/tech news sources for context enrichment
ADDITIONAL_CONTEXT_SOURCES = {
    'tech_crunch': {
        'url': 'https://techcrunch.com/feed/',
        'category': 'tech_news',
        'weight': 0.8
    },
    'venture_beat': {
        'url': 'https://venturebeat.com/feed/',
        'category': 'tech_news',
        'weight': 0.7
    },
    'ai_news': {
        'url': 'https://artificialintelligence-news.com/feed/',
        'category': 'ai_specific',
        'weight': 0.9
    },
    'mit_tech_review': {
        'url': 'https://www.technologyreview.com/topic/artificial-intelligence/feed',
        'category': 'ai_research',
        'weight': 0.8
    },
    'reddit_ai': {
        'url': 'https://www.reddit.com/r/artificial/hot.rss?limit=5',
        'category': 'community_discussion',
        'weight': 0.6
    },
    'hacker_news': {
        'url': 'https://news.ycombinator.com/rss',
        'category': 'tech_community',
        'weight': 0.7
    }
}

# Trending AI topics and keywords for content enhancement
TRENDING_AI_TOPICS = {
    'machine_learning': ['ML', 'machine learning', 'deep learning', 'neural networks'],
    'generative_ai': ['GPT', 'DALL-E', 'generative AI', 'text-to-image', 'LLM'],
    'ai_ethics': ['AI ethics', 'responsible AI', 'AI safety', 'bias in AI'],
    'ai_applications': ['AI in healthcare', 'AI in finance', 'AI in education', 'AI automation'],
    'quantum_ai': ['quantum computing', 'quantum AI', 'quantum machine learning'],
    'ai_research': ['AI research', 'AI breakthrough', 'AI innovation', 'AI development']
}

# Configuration for enhanced processing
CONFIG = {
    'data_dir': 'rss_data_enhanced',
    'max_entries_per_run': 15,
    'today_only': True,
    'max_days_old': 1,
    'backup_count': 5,
    'request_delay': 1,
    'context_enrichment': True,
    'trending_analysis': True,
    'content_clustering': True
}

def ensure_data_directory():
    """Ensure the enhanced data directory exists"""
    Path(CONFIG['data_dir']).mkdir(exist_ok=True)
    return CONFIG['data_dir']

def fetch_additional_context():
    """Fetch additional context from external sources"""
    logger.info("🔍 Fetching additional context from external sources...")
    
    context_data = {}
    
    for source_name, source_info in ADDITIONAL_CONTEXT_SOURCES.items():
        try:
            logger.info(f"📡 Fetching context from: {source_name}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(source_info['url'], headers=headers, timeout=15)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            if feed.entries:
                context_entries = []
                for entry in feed.entries[:5]:  # Limit to 5 entries per source
                    context_entry = {
                        'title': entry.title,
                        'link': entry.get('link', ''),
                        'summary': entry.get('summary', entry.get('contentSnippet', '')),
                        'published': entry.get('published', entry.get('updated', '')),
                        'source': source_name,
                        'category': source_info['category'],
                        'weight': source_info['weight']
                    }
                    context_entries.append(context_entry)
                
                context_data[source_name] = {
                    'entries': context_entries,
                    'category': source_info['category'],
                    'weight': source_info['weight']
                }
                
                logger.info(f"✅ Found {len(context_entries)} context entries from {source_name}")
                
            else:
                logger.warning(f"❌ No context entries found in {source_name}")
                
        except Exception as e:
            logger.error(f"❌ Error fetching context from {source_name}: {e}")
            continue
        
        time.sleep(CONFIG['request_delay'])
    
    return context_data

def analyze_trending_topics(entries, context_data):
    """Analyze trending topics across all content"""
    logger.info("📊 Analyzing trending topics and themes...")
    
    # Combine all content for analysis
    all_content = []
    
    # Add mytribal entries
    for entry in entries:
        all_content.append({
            'text': f"{entry['title']} {entry['summary']}",
            'source': 'mytribal',
            'weight': 1.0
        })
    
    # Add context entries
    for source_name, source_data in context_data.items():
        for entry in source_data['entries']:
            all_content.append({
                'text': f"{entry['title']} {entry['summary']}",
                'source': source_name,
                'weight': source_data['weight']
            })
    
    # Analyze trending topics
    topic_scores = {}
    
    for content in all_content:
        text_lower = content['text'].lower()
        weight = content['weight']
        
        for topic, keywords in TRENDING_AI_TOPICS.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1
            
            if score > 0:
                topic_scores[topic] = topic_scores.get(topic, 0) + (score * weight)
    
    # Sort topics by score
    trending_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
    
    logger.info("📈 Trending topics identified:")
    for topic, score in trending_topics[:5]:
        logger.info(f"   {topic}: {score:.2f}")
    
    return trending_topics

def cluster_related_content(entries, context_data):
    """Cluster related content for story generation"""
    logger.info("🔗 Clustering related content...")
    
    # Create content clusters based on similarity
    clusters = []
    
    # Simple clustering based on keyword overlap
    for entry in entries:
        entry_keywords = extract_keywords(f"{entry['title']} {entry['summary']}")
        
        # Find related context
        related_context = []
        for source_name, source_data in context_data.items():
            for context_entry in source_data['entries']:
                context_keywords = extract_keywords(f"{context_entry['title']} {context_entry['summary']}")
                
                # Calculate similarity
                similarity = calculate_similarity(entry_keywords, context_keywords)
                
                if similarity > 0.3:  # Threshold for related content
                    related_context.append({
                        'entry': context_entry,
                        'similarity': similarity,
                        'source': source_name
                    })
        
        if related_context:
            # Sort by similarity
            related_context.sort(key=lambda x: x['similarity'], reverse=True)
            
            cluster = {
                'main_entry': entry,
                'related_context': related_context[:3],  # Top 3 related pieces
                'cluster_score': sum(ctx['similarity'] for ctx in related_context[:3]),
                'topics': extract_topics(f"{entry['title']} {entry['summary']}")
            }
            
            clusters.append(cluster)
    
    logger.info(f"✅ Created {len(clusters)} content clusters")
    return clusters

def extract_keywords(text):
    """Extract keywords from text"""
    # Simple keyword extraction (can be enhanced with NLP libraries)
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter out common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
    
    keywords = [word for word in words if word not in stop_words and len(word) > 3]
    
    # Count frequency
    keyword_freq = {}
    for keyword in keywords:
        keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
    
    return keyword_freq

def calculate_similarity(keywords1, keywords2):
    """Calculate similarity between two sets of keywords"""
    if not keywords1 or not keywords2:
        return 0.0
    
    # Simple Jaccard similarity
    set1 = set(keywords1.keys())
    set2 = set(keywords2.keys())
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0

def extract_topics(text):
    """Extract main topics from text"""
    text_lower = text.lower()
    found_topics = []
    
    for topic, keywords in TRENDING_AI_TOPICS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_topics.append(topic)
                break
    
    return list(set(found_topics))

def create_enhanced_story_outline(cluster):
    """Create an enhanced story outline with additional context"""
    main_entry = cluster['main_entry']
    related_context = cluster['related_context']
    
    outline = {
        'main_story': {
            'title': main_entry['title'],
            'summary': main_entry['summary'],
            'link': main_entry['link'],
            'topics': cluster['topics']
        },
        'supporting_context': [],
        'story_angles': [],
        'key_insights': [],
        'trending_connections': []
    }
    
    # Add supporting context
    for ctx in related_context:
        outline['supporting_context'].append({
            'title': ctx['entry']['title'],
            'summary': ctx['entry']['summary'],
            'source': ctx['source'],
            'relevance': ctx['similarity']
        })
    
    # Generate story angles
    if 'ai_ethics' in cluster['topics']:
        outline['story_angles'].append("Ethical implications and responsible AI development")
    
    if 'ai_applications' in cluster['topics']:
        outline['story_angles'].append("Real-world applications and industry impact")
    
    if 'ai_research' in cluster['topics']:
        outline['story_angles'].append("Research breakthroughs and future implications")
    
    # Extract key insights
    all_text = f"{main_entry['title']} {main_entry['summary']}"
    for ctx in related_context:
        all_text += f" {ctx['entry']['title']} {ctx['entry']['summary']}"
    
    # Simple insight extraction (can be enhanced with AI)
    insights = extract_insights(all_text)
    outline['key_insights'] = insights
    
    return outline

def extract_insights(text):
    """Extract key insights from text"""
    insights = []
    
    # Look for insight indicators
    insight_patterns = [
        r'breakthrough',
        r'innovation',
        r'discovery',
        r'advancement',
        r'implication',
        r'impact',
        r'future',
        r'potential'
    ]
    
    for pattern in insight_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            insights.append(f"Key {pattern}: {len(matches)} mentions")
    
    return insights[:3]  # Limit to top 3 insights

def fetch_todays_rss():
    """Fetch RSS content from mytribal.ai, focusing on today's posts"""
    logger.info("🔍 Fetching today's RSS feeds from mytribal.ai...")
    
    all_entries = []
    today = datetime.now().date()
    
    for feed_url in MYTRIBAL_RSS_FEEDS:
        try:
            logger.info(f"📡 Fetching: {feed_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(feed_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            if feed.entries:
                logger.info(f"✅ Found {len(feed.entries)} entries from {feed_url}")
                
                for entry in feed.entries:
                    entry_data = {
                        'title': entry.title,
                        'link': entry.get('link', ''),
                        'published': entry.get('published', entry.get('updated', '')),
                        'summary': entry.get('summary', entry.get('contentSnippet', '')),
                        'feed_url': feed_url,
                        'feed_title': feed.feed.get('title', 'mytribal.ai'),
                        'timestamp': datetime.now().isoformat(),
                        'processed': False,
                        'processing_date': None,
                        'is_today': False
                    }
                    
                    # Parse publication date and check if it's today
                    try:
                        if entry_data['published']:
                            if 'T' in entry_data['published']:
                                pub_date = datetime.fromisoformat(entry_data['published'].replace('Z', '+00:00'))
                            else:
                                pub_date = datetime.strptime(entry_data['published'], '%a, %d %b %Y %H:%M:%S %z')
                            
                            entry_data['parsed_date'] = pub_date.isoformat()
                            entry_data['days_old'] = (datetime.now(pub_date.tzinfo) - pub_date).days
                            
                            pub_date_local = pub_date.astimezone()
                            entry_data['is_today'] = (pub_date_local.date() == today)
                            
                            if entry_data['is_today']:
                                hour = pub_date_local.hour
                                if 6 <= hour < 12:
                                    entry_data['time_category'] = 'morning'
                                elif 12 <= hour < 18:
                                    entry_data['time_category'] = 'afternoon'
                                elif 18 <= hour < 22:
                                    entry_data['time_category'] = 'evening'
                                else:
                                    entry_data['time_category'] = 'night'
                            else:
                                entry_data['time_category'] = 'previous_days'
                            
                        else:
                            entry_data['parsed_date'] = None
                            entry_data['days_old'] = None
                            entry_data['is_today'] = False
                            entry_data['time_category'] = 'unknown'
                            
                    except Exception as e:
                        logger.warning(f"Could not parse date for entry: {entry.title[:50]}... Error: {e}")
                        entry_data['parsed_date'] = None
                        entry_data['days_old'] = None
                        entry_data['is_today'] = False
                        entry_data['time_category'] = 'unknown'
                    
                    all_entries.append(entry_data)
                
            else:
                logger.warning(f"❌ No entries found in {feed_url}")
                
        except Exception as e:
            logger.error(f"❌ Error fetching {feed_url}: {e}")
            continue
        
        time.sleep(CONFIG['request_delay'])
    
    return all_entries

def main():
    """Main enhanced RSS automation workflow"""
    logger.info("🚀 Starting Enhanced mytribal.ai RSS Automation...")
    start_time = datetime.now()
    
    try:
        # Ensure data directory exists
        data_dir = ensure_data_directory()
        
        # Fetch mytribal RSS content
        mytribal_entries = fetch_todays_rss()
        
        if not mytribal_entries:
            logger.warning("❌ No mytribal RSS content found. Exiting.")
            return
        
        # Filter for today's content
        todays_entries = [e for e in mytribal_entries if e.get('is_today', False)]
        
        if not todays_entries:
            logger.info("📅 No new content from today found")
            return
        
        logger.info(f"📥 Found {len(todays_entries)} entries from today")
        
        # Fetch additional context
        context_data = fetch_additional_context()
        
        # Analyze trending topics
        trending_topics = analyze_trending_topics(todays_entries, context_data)
        
        # Cluster related content
        content_clusters = cluster_related_content(todays_entries, context_data)
        
        # Create enhanced story outlines
        enhanced_stories = []
        for cluster in content_clusters:
            story_outline = create_enhanced_story_outline(cluster)
            enhanced_stories.append(story_outline)
        
        # Save enhanced data
        enhanced_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'mytribal_entries': todays_entries,
            'context_sources': context_data,
            'trending_topics': trending_topics,
            'content_clusters': content_clusters,
            'enhanced_stories': enhanced_stories
        }
        
        # Save to file
        today = datetime.now().strftime("%Y-%m-%d")
        enhanced_file = Path(data_dir) / f"enhanced_rss_{today}.json"
        
        with open(enhanced_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"💾 Enhanced data saved to: {enhanced_file}")
        
        # Display summary
        logger.info("\n📊 Enhanced Processing Summary:")
        logger.info(f"   Date: {today}")
        logger.info(f"   MyTribal entries: {len(todays_entries)}")
        logger.info(f"   Context sources: {len(context_data)}")
        logger.info(f"   Content clusters: {len(content_clusters)}")
        logger.info(f"   Enhanced stories: {len(enhanced_stories)}")
        logger.info(f"   Trending topics: {len(trending_topics)}")
        
        logger.info(f"\n🎉 Enhanced RSS Automation completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Fatal error in enhanced RSS automation: {e}")
        raise
    
    finally:
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"⏰ Total runtime: {duration}")

if __name__ == "__main__":
    main()
