#!/usr/bin/env python3
"""
Enhanced Labor Intelligence System
Integrates Google News RSS scraping with AI automation for comprehensive labor intelligence
"""

import os
import requests
import feedparser
import re
import time
import json
import logging
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, quote_plus
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import openai
import schedule
import threading

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_labor_intelligence.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedLaborIntelligenceSystem:
    def __init__(self):
        self.headers = {
            'User-Agent': os.getenv('USER_AGENT', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        }
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.articles = []
        self.filtered_articles = []
        self.ai_enhanced_content = []
        
        # Initialize OpenAI if API key is available
        self.openai_client = None
        if os.getenv('OPENAI_API_KEY'):
            openai.api_key = os.getenv('OPENAI_API_KEY')
            self.openai_client = openai
        
        # Target keywords for labor and union intelligence
        self.target_keywords = {
            'union_organizing': [
                'union organizing', 'union drive', 'union election', 'NLRB', 'collective bargaining',
                'union representation', 'union certification', 'union recognition'
            ],
            'labor_issues': [
                'strike', 'lockout', 'work stoppage', 'labor dispute', 'contract negotiation',
                'wage increase', 'benefits negotiation', 'working conditions', 'overtime pay'
            ],
            'construction_trades': [
                'Local 825', 'Operating Engineers', 'construction union', 'building trades',
                'heavy equipment', 'bulldozer', 'excavator', 'construction worker', 'infrastructure'
            ],
            'job_market': [
                'construction jobs', 'infrastructure jobs', 'union jobs', 'hiring', 'employment',
                'job growth', 'construction projects', 'infrastructure projects'
            ],
            'government_projects': [
                'federal contracts', 'state contracts', 'municipal contracts', 'infrastructure bill',
                'construction projects', 'public works', 'government spending'
            ]
        }
        
        # Google News RSS base URLs
        self.google_news_rss_base = "https://news.google.com/rss/search"
        
        # Additional RSS sources for comprehensive coverage
        self.additional_rss_sources = {
            'labor_notes': 'https://labornotes.org/feed',
            'afl_cio': 'https://aflcio.org/feed',
            'teamsters': 'https://teamster.org/feed',
            'uaw': 'https://uaw.org/feed',
            'construction_news': 'https://www.constructiondive.com/rss/',
            'infrastructure_news': 'https://www.infrastructure-intelligence.com/rss'
        }
        
    def build_search_queries(self):
        """Build optimized Google News RSS search queries"""
        queries = []
        
        # Primary union and labor searches
        queries.extend([
            "union organizing labor news",
            "Local 825 Operating Engineers",
            "construction union news",
            "labor strikes negotiations",
            "infrastructure construction jobs",
            "NLRB union elections",
            "collective bargaining agreements"
        ])
        
        # Regional searches (adjust based on Local 825 jurisdiction)
        regional_terms = [
            "New Jersey construction union",
            "New York construction union", 
            "Pennsylvania construction union",
            "Northeast construction projects"
        ]
        queries.extend(regional_terms)
        
        return queries
    
    def get_google_news_rss_url(self, query, timeframe="24h"):
        """Generate Google News RSS URL for a search query"""
        encoded_query = quote_plus(query)
        return f"{self.google_news_rss_base}?q={encoded_query}&hl=en-US&gl=US&ceid=US:en&tbm=nws&tbs=qdr:{timeframe}"
    
    def scrape_google_news_rss(self, query, timeframe="24h"):
        """Scrape Google News RSS feed for a specific query"""
        try:
            rss_url = self.get_google_news_rss_url(query, timeframe)
            logger.info(f"🔍 Scraping RSS: {query}")
            
            response = requests.get(rss_url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                articles = []
                
                for entry in feed.entries:
                    article = {
                        'title': entry.title,
                        'url': entry.link,
                        'published': entry.get('published', ''),
                        'source': entry.get('source', {}).get('title', ''),
                        'summary': entry.get('summary', ''),
                        'query': query,
                        'scraped_at': datetime.now().isoformat(),
                        'type': 'google_news'
                    }
                    articles.append(article)
                
                logger.info(f"✅ Found {len(articles)} articles for: {query}")
                return articles
            else:
                logger.error(f"❌ Failed to fetch RSS for {query}: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error scraping RSS for {query}: {e}")
            return []
    
    def scrape_additional_rss_sources(self):
        """Scrape additional RSS sources for comprehensive coverage"""
        logger.info("🔍 Scraping additional RSS sources...")
        all_articles = []
        
        for source_name, rss_url in self.additional_rss_sources.items():
            try:
                logger.info(f"📡 Scraping {source_name}: {rss_url}")
                response = requests.get(rss_url, headers=self.headers, timeout=30)
                
                if response.status_code == 200:
                    feed = feedparser.parse(response.content)
                    articles = []
                    
                    for entry in feed.entries:
                        # Check if article is recent (within last 7 days)
                        pub_date = entry.get('published', '')
                        if pub_date:
                            try:
                                # Parse various date formats
                                for fmt in ['%a, %d %b %Y %H:%M:%S %Z', '%Y-%m-%dT%H:%M:%S%z']:
                                    try:
                                        parsed_date = datetime.strptime(pub_date, fmt)
                                        if parsed_date > datetime.now() - timedelta(days=7):
                                            article = {
                                                'title': entry.title,
                                                'url': entry.link,
                                                'published': pub_date,
                                                'source': source_name.title(),
                                                'summary': entry.get('summary', ''),
                                                'query': f'RSS_{source_name}',
                                                'scraped_at': datetime.now().isoformat(),
                                                'type': 'additional_rss'
                                            }
                                            articles.append(article)
                                        break
                                    except ValueError:
                                        continue
                            except:
                                # If date parsing fails, include article anyway
                                article = {
                                    'title': entry.title,
                                    'url': entry.link,
                                    'published': pub_date,
                                    'source': source_name.title(),
                                    'summary': entry.get('summary', ''),
                                    'query': f'RSS_{source_name}',
                                    'scraped_at': datetime.now().isoformat(),
                                    'type': 'additional_rss'
                                }
                                articles.append(article)
                    
                    all_articles.extend(articles)
                    logger.info(f"✅ Found {len(articles)} articles from {source_name}")
                    time.sleep(1)  # Be respectful to servers
                    
            except Exception as e:
                logger.error(f"❌ Error scraping {source_name}: {e}")
                continue
        
        return all_articles
    
    def filter_articles_by_relevance(self, articles):
        """Filter articles based on relevance to our target keywords"""
        relevant_articles = []
        
        for article in articles:
            relevance_score = 0
            matched_keywords = []
            
            # Combine title and summary for analysis
            text_to_analyze = f"{article['title']} {article['summary']}".lower()
            
            # Score based on keyword matches
            for category, keywords in self.target_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in text_to_analyze:
                        relevance_score += 1
                        matched_keywords.append(keyword)
            
            # Additional scoring factors
            if 'union' in text_to_analyze:
                relevance_score += 2
            if 'construction' in text_to_analyze:
                relevance_score += 2
            if 'Local 825' in text_to_analyze:
                relevance_score += 5  # High priority
            if 'strike' in text_to_analyze or 'negotiation' in text_to_analyze:
                relevance_score += 3
            
            # Filter out low-relevance articles
            if relevance_score >= 2:  # Minimum relevance threshold
                article['relevance_score'] = relevance_score
                article['matched_keywords'] = matched_keywords
                article['category'] = self.categorize_article(article)
                relevant_articles.append(article)
        
        # Sort by relevance score
        relevant_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_articles
    
    def categorize_article(self, article):
        """Categorize article based on content and keywords"""
        text = f"{article['title']} {article['summary']}".lower()
        
        if any(term in text for term in ['strike', 'lockout', 'work stoppage']):
            return 'Labor Disputes'
        elif any(term in text for term in ['negotiation', 'contract', 'bargaining']):
            return 'Contract Negotiations'
        elif any(term in text for term in ['organizing', 'election', 'NLRB']):
            return 'Union Organizing'
        elif any(term in text for term in ['construction', 'infrastructure', 'project']):
            return 'Construction Projects'
        elif any(term in text for term in ['job', 'hiring', 'employment']):
            return 'Job Market'
        elif 'Local 825' in text:
            return 'Local 825 Specific'
        else:
            return 'General Labor News'
    
    def enhance_content_with_ai(self, articles):
        """Enhance content using AI analysis if OpenAI is available"""
        if not self.openai_client or not articles:
            return []
        
        logger.info("🤖 Enhancing content with AI analysis...")
        enhanced_content = []
        
        # Take top 10 most relevant articles for AI enhancement
        top_articles = articles[:10]
        
        for article in top_articles:
            try:
                # Create AI prompt for analysis
                prompt = f"""
                Analyze this labor union news article and provide:
                1. Key implications for Local 825 Operating Engineers
                2. Strategic opportunities or threats
                3. Recommended actions for union leadership
                4. Impact on construction industry
                
                Article: {article['title']}
                Summary: {article['summary']}
                Category: {article['category']}
                Relevance Score: {article['relevance_score']}
                
                Provide a concise, actionable analysis in 2-3 paragraphs.
                """
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a labor intelligence analyst specializing in construction unions and Local 825 Operating Engineers."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                
                ai_analysis = response.choices[0].message.content
                
                enhanced_article = article.copy()
                enhanced_article['ai_analysis'] = ai_analysis
                enhanced_article['enhanced_at'] = datetime.now().isoformat()
                
                enhanced_content.append(enhanced_article)
                logger.info(f"✅ AI enhanced: {article['title'][:50]}...")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ AI enhancement failed for {article['title']}: {e}")
                continue
        
        return enhanced_content
    
    def scrape_all_sources(self):
        """Scrape all sources for comprehensive coverage"""
        logger.info("🚀 Starting comprehensive labor intelligence scraping...")
        
        all_articles = []
        
        # 1. Google News RSS scraping
        queries = self.build_search_queries()
        for query in queries:
            articles = self.scrape_google_news_rss(query)
            all_articles.extend(articles)
            time.sleep(1)  # Be respectful to Google's servers
        
        # 2. Additional RSS sources
        additional_articles = self.scrape_additional_rss_sources()
        all_articles.extend(additional_articles)
        
        # Remove duplicates based on URL
        unique_articles = {}
        for article in all_articles:
            if article['url'] not in unique_articles:
                unique_articles[article['url']] = article
        
        self.articles = list(unique_articles.values())
        logger.info(f"📰 Total unique articles found: {len(self.articles)}")
        
        # Filter for relevance
        self.filtered_articles = self.filter_articles_by_relevance(self.articles)
        logger.info(f"✅ Relevant articles after filtering: {len(self.filtered_articles)}")
        
        # AI enhancement
        self.ai_enhanced_content = self.enhance_content_with_ai(self.filtered_articles)
        logger.info(f"🤖 AI enhanced articles: {len(self.ai_enhanced_content)}")
        
        return self.filtered_articles
    
    def generate_enhanced_intelligence_report(self):
        """Generate comprehensive labor intelligence report with AI insights"""
        if not self.filtered_articles:
            return "No relevant articles found to analyze."
        
        report = f"""
ENHANCED LABOR INTELLIGENCE REPORT - COMPREHENSIVE ANALYSIS
==========================================================
Date: {self.today}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Articles Analyzed: {len(self.articles)}
Relevant Articles: {len(self.filtered_articles)}
AI Enhanced Articles: {len(self.ai_enhanced_content)}

EXECUTIVE SUMMARY
-----------------
• {len(self.filtered_articles)} high-relevance labor articles identified
• {len(self.ai_enhanced_content)} articles enhanced with AI analysis
• Top categories: {', '.join(set([a['category'] for a in self.filtered_articles[:5]]))}
• Key sources: {', '.join(set([a['source'] for a in self.filtered_articles[:5]]))}

AI-ENHANCED ANALYSIS
====================
"""
        
        # Show AI-enhanced articles first
        if self.ai_enhanced_content:
            for article in self.ai_enhanced_content[:5]:
                report += f"""
🤖 {article['title']}
   Source: {article['source']}
   Relevance Score: {article['relevance_score']}
   Category: {article['category']}
   Keywords: {', '.join(article['matched_keywords'][:3])}
   
   AI Analysis:
   {article['ai_analysis']}
   
   URL: {article['url']}
   Published: {article['published']}
"""
        
        # Group remaining articles by category
        categories = {}
        for article in self.filtered_articles:
            if article not in self.ai_enhanced_content:  # Skip already shown articles
                cat = article['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(article)
        
        for category, articles in categories.items():
            if articles:  # Only show categories with articles
                report += f"\n{category.upper()}\n{'-' * len(category)}\n"
                for article in articles[:3]:  # Top 3 per category
                    report += f"""
📰 {article['title']}
   Source: {article['source']}
   Relevance Score: {article['relevance_score']}
   Keywords: {', '.join(article['matched_keywords'][:3])}
   URL: {article['url']}
   Published: {article['published']}
"""
        
        report += f"""

STRATEGIC INSIGHTS
==================
• High-priority articles: {len([a for a in self.filtered_articles if a['relevance_score'] >= 5])}
• Union organizing focus: {len([a for a in self.filtered_articles if 'organizing' in a['category'].lower()])}
• Construction projects: {len([a for a in self.filtered_articles if 'construction' in a['category'].lower()])}
• AI-enhanced insights: {len(self.ai_enhanced_content)} strategic analyses

RECOMMENDATIONS
===============
• Monitor {len(self.filtered_articles)} relevant articles for Local 825 impact
• Focus on {len([a for a in self.filtered_articles if a['relevance_score'] >= 4])} high-relevance stories
• Review {len(self.ai_enhanced_content)} AI-enhanced strategic analyses
• Track {len(set([a['source'] for a in self.filtered_articles]))} news sources for ongoing monitoring

---
Generated by: Enhanced Labor Intelligence System with AI Analysis
Contact: jeremy@augments.art
© 2025 Labor Intelligence Division
"""
        
        return report
    
    def save_report(self, filename=None):
        """Save the enhanced intelligence report to file"""
        if not filename:
            filename = f"reports/enhanced_labor_intelligence_{self.today}.txt"
        
        report = self.generate_enhanced_intelligence_report()
        
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"💾 Enhanced report saved to: {filename}")
        return filename
    
    def save_json_data(self, filename=None):
        """Save structured data as JSON for further processing"""
        if not filename:
            filename = f"reports/enhanced_labor_intelligence_{self.today}.json"
        
        data = {
            'metadata': {
                'date': self.today,
                'generated_at': datetime.now().isoformat(),
                'total_articles': len(self.articles),
                'relevant_articles': len(self.filtered_articles),
                'ai_enhanced': len(self.ai_enhanced_content)
            },
            'articles': self.filtered_articles,
            'ai_enhanced_content': self.ai_enhanced_content
        }
        
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"💾 JSON data saved to: {filename}")
        return filename

def main():
    """Main execution function"""
    print("🚀 Enhanced Labor Intelligence System")
    print("=" * 50)
    
    system = EnhancedLaborIntelligenceSystem()
    
    # Scrape all sources
    articles = system.scrape_all_sources()
    
    if articles:
        # Generate and save reports
        report_file = system.save_report()
        json_file = system.save_json_data()
        
        # Display summary
        print(f"\n🎉 Enhanced scraping completed successfully!")
        print(f"📊 Found {len(articles)} relevant articles")
        print(f"🤖 AI enhanced {len(system.ai_enhanced_content)} articles")
        print(f"📋 Enhanced report saved to: {report_file}")
        print(f"💾 JSON data saved to: {json_file}")
        
        # Show top articles
        print(f"\n🔝 Top 3 Most Relevant Articles:")
        for i, article in enumerate(articles[:3], 1):
            print(f"{i}. {article['title']} (Score: {article['relevance_score']})")
        
        if system.ai_enhanced_content:
            print(f"\n🤖 AI-Enhanced Articles:")
            for i, article in enumerate(system.ai_enhanced_content[:3], 1):
                print(f"{i}. {article['title']} - AI Analysis Available")
    else:
        print("❌ No relevant articles found. Check your keywords or try different search terms.")

if __name__ == "__main__":
    main()
