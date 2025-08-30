#!/usr/bin/env python3
"""
Local 825 Targeted Intelligence System
Focused on NJ and relevant NY territories with comprehensive research framework
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

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('local825_intelligence.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Local825TargetedIntelligenceSystem:
    def __init__(self):
        self.headers = {
            'User-Agent': os.getenv('USER_AGENT', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        }
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.articles = []
        self.filtered_articles = []
        self.research_data = {}
        
        # Initialize OpenAI if API key is available
        self.openai_client = None
        if os.getenv('OPENAI_API_KEY'):
            openai.api_key = os.getenv('OPENAI_API_KEY')
            self.openai_client = openai
        
        # Local 825 specific target keywords and jurisdictions
        self.target_keywords = {
            'local825_specific': [
                'Local 825', 'Operating Engineers Local 825', 'IUOE Local 825',
                'New Jersey Operating Engineers', 'NY Operating Engineers'
            ],
            'nj_construction': [
                'New Jersey construction', 'NJ construction projects', 'NJ infrastructure',
                'NJ building trades', 'NJ heavy construction', 'NJ road construction',
                'NJ bridge construction', 'NJ tunnel construction', 'NJ port construction'
            ],
            'ny_relevant_territories': [
                'New York construction', 'NYC construction', 'Long Island construction',
                'Westchester construction', 'Rockland construction', 'Orange construction',
                'Putnam construction', 'Dutchess construction', 'Suffolk construction'
            ],
            'union_organizing': [
                'union organizing', 'union drive', 'NLRB', 'collective bargaining',
                'union representation', 'union certification', 'union recognition'
            ],
            'labor_issues': [
                'strike', 'lockout', 'work stoppage', 'labor dispute', 'contract negotiation',
                'wage increase', 'benefits negotiation', 'working conditions', 'overtime pay'
            ],
            'construction_trades': [
                'construction union', 'building trades', 'heavy equipment', 'bulldozer',
                'excavator', 'construction worker', 'infrastructure', 'heavy construction'
            ],
            'government_projects': [
                'federal contracts', 'state contracts', 'municipal contracts', 'infrastructure bill',
                'construction projects', 'public works', 'government spending', 'prevailing wage'
            ]
        }
        
        # Local 825 jurisdiction focus areas
        self.jurisdiction_areas = {
            'new_jersey': [
                'Bergen County', 'Essex County', 'Hudson County', 'Passaic County',
                'Union County', 'Morris County', 'Somerset County', 'Middlesex County',
                'Monmouth County', 'Ocean County', 'Burlington County', 'Camden County',
                'Gloucester County', 'Salem County', 'Cape May County', 'Atlantic County',
                'Cumberland County', 'Hunterdon County', 'Warren County', 'Sussex County'
            ],
            'new_york_relevant': [
                'New York City', 'Bronx', 'Brooklyn', 'Manhattan', 'Queens', 'Staten Island',
                'Long Island', 'Nassau County', 'Suffolk County', 'Westchester County',
                'Rockland County', 'Orange County', 'Putnam County', 'Dutchess County'
            ]
        }
        
        # Google News RSS base URLs
        self.google_news_rss_base = "https://news.google.com/rss/search"
        
        # Local 825 specific RSS sources
        self.local825_rss_sources = {
            'nj_business': 'https://www.nj.com/business/feed/',
            'nj_politics': 'https://www.nj.com/politics/feed/',
            'nj_real_estate': 'https://www.nj.com/real-estate/feed/',
            'ny_business': 'https://www.crainsnewyork.com/feed',
            'construction_dive': 'https://www.constructiondive.com/rss/',
            'engineering_news': 'https://www.enr.com/rss',
            'labor_notes': 'https://labornotes.org/feed',
            'afl_cio': 'https://aflcio.org/feed'
        }
        
        # Government and public records sources
        self.government_sources = {
            'nj_courts': 'https://www.njcourts.gov/public/find-a-case',
            'nj_municipal': 'https://portal.njcourts.gov/webe41/MPAWeb/',
            'ny_courts': 'https://iapps.courts.state.ny.us/webcivil/ecourtsMain',
            'subsidy_tracker': 'https://subsidytracker.goodjobsfirst.org/',
            'public_records': 'https://publicrecords.searchsystems.net/',
            'osha': 'https://www.osha.gov/establishments',
            'nlrb': 'https://www.nlrb.gov/reports-guidance/nlrb-case-activity',
            'federal_procurement': 'https://www.fpds.gov/',
            'nj_dot': 'https://www.state.nj.us/transportation/business/contracts/',
            'ny_dot': 'https://www.dot.ny.gov/contracts'
        }
        
    def build_local825_search_queries(self):
        """Build targeted search queries for Local 825 jurisdiction"""
        queries = []
        
        # Local 825 specific searches
        queries.extend([
            "Local 825 Operating Engineers New Jersey",
            "Local 825 Operating Engineers New York",
            "IUOE Local 825 construction projects",
            "Operating Engineers Local 825 NJ",
            "Operating Engineers Local 825 NY"
        ])
        
        # NJ construction and infrastructure
        for county in self.jurisdiction_areas['new_jersey'][:10]:  # Focus on major counties
            queries.extend([
                f"{county} construction projects",
                f"{county} infrastructure projects",
                f"{county} construction union"
            ])
        
        # NY relevant territories
        for area in self.jurisdiction_areas['new_york_relevant'][:8]:  # Focus on major areas
            queries.extend([
                f"{area} construction projects",
                f"{area} infrastructure projects",
                f"{area} construction union"
            ])
        
        # Industry-specific searches
        queries.extend([
            "New Jersey heavy construction projects",
            "New York heavy construction projects",
            "NJ infrastructure bill projects",
            "NY infrastructure bill projects",
            "New Jersey prevailing wage construction",
            "New York prevailing wage construction",
            "NJ construction labor disputes",
            "NY construction labor disputes"
        ])
        
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
                        'type': 'google_news',
                        'jurisdiction': self.categorize_jurisdiction(entry.title + ' ' + entry.get('summary', ''))
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
    
    def categorize_jurisdiction(self, text):
        """Categorize article by Local 825 jurisdiction"""
        text_lower = text.lower()
        
        # Check for NJ focus
        if any(county.lower() in text_lower for county in self.jurisdiction_areas['new_jersey']):
            return 'New Jersey'
        elif 'new jersey' in text_lower or 'nj' in text_lower:
            return 'New Jersey'
        
        # Check for NY focus
        if any(area.lower() in text_lower for area in self.jurisdiction_areas['new_york_relevant']):
            return 'New York'
        elif 'new york' in text_lower or 'nyc' in text_lower:
            return 'New York'
        
        # Check for Local 825 specific
        if 'local 825' in text_lower or 'operating engineers' in text_lower:
            return 'Local 825 Specific'
        
        return 'General'
    
    def scrape_local825_rss_sources(self):
        """Scrape Local 825 specific RSS sources"""
        logger.info("🔍 Scraping Local 825 specific RSS sources...")
        all_articles = []
        
        for source_name, rss_url in self.local825_rss_sources.items():
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
                                                'type': 'local825_rss',
                                                'jurisdiction': self.categorize_jurisdiction(entry.title + ' ' + entry.get('summary', ''))
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
                                    'type': 'local825_rss',
                                    'jurisdiction': self.categorize_jurisdiction(entry.title + ' ' + entry.get('summary', ''))
                                }
                                articles.append(article)
                    
                    all_articles.extend(articles)
                    logger.info(f"✅ Found {len(articles)} articles from {source_name}")
                    time.sleep(1)  # Be respectful to servers
                    
            except Exception as e:
                logger.error(f"❌ Error scraping {source_name}: {e}")
                continue
        
        return all_articles
    
    def filter_articles_by_local825_relevance(self, articles):
        """Filter articles based on Local 825 relevance"""
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
            
            # Jurisdiction scoring
            if article['jurisdiction'] == 'Local 825 Specific':
                relevance_score += 5  # Highest priority
            elif article['jurisdiction'] == 'New Jersey':
                relevance_score += 4  # High priority
            elif article['jurisdiction'] == 'New York':
                relevance_score += 3  # Medium-high priority
            
            # Additional scoring factors
            if 'union' in text_to_analyze:
                relevance_score += 2
            if 'construction' in text_to_analyze:
                relevance_score += 2
            if 'Local 825' in text_to_analyze:
                relevance_score += 5  # High priority
            if 'strike' in text_to_analyze or 'negotiation' in text_to_analyze:
                relevance_score += 3
            if 'infrastructure' in text_to_analyze:
                relevance_score += 2
            if 'prevailing wage' in text_to_analyze:
                relevance_score += 3
            
            # Filter out low-relevance articles
            if relevance_score >= 3:  # Higher threshold for Local 825 focus
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
        elif 'prevailing wage' in text:
            return 'Prevailing Wage Issues'
        elif 'infrastructure bill' in text:
            return 'Infrastructure Bill Projects'
        else:
            return 'General Labor News'
    
    def scrape_all_local825_sources(self):
        """Scrape all sources for Local 825 focused coverage"""
        logger.info("🚀 Starting Local 825 targeted intelligence scraping...")
        
        all_articles = []
        
        # 1. Google News RSS scraping with Local 825 focus
        queries = self.build_local825_search_queries()
        for query in queries:
            articles = self.scrape_google_news_rss(query)
            all_articles.extend(articles)
            time.sleep(1)  # Be respectful to Google's servers
        
        # 2. Local 825 specific RSS sources
        local825_articles = self.scrape_local825_rss_sources()
        all_articles.extend(local825_articles)
        
        # Remove duplicates based on URL
        unique_articles = {}
        for article in all_articles:
            if article['url'] not in unique_articles:
                unique_articles[article['url']] = article
        
        self.articles = list(unique_articles.values())
        logger.info(f"📰 Total unique articles found: {len(self.articles)}")
        
        # Filter for Local 825 relevance
        self.filtered_articles = self.filter_articles_by_local825_relevance(self.articles)
        logger.info(f"✅ Local 825 relevant articles: {len(self.filtered_articles)}")
        
        return self.filtered_articles
    
    def generate_local825_intelligence_report(self):
        """Generate Local 825 focused intelligence report"""
        if not self.filtered_articles:
            return "No Local 825 relevant articles found to analyze."
        
        # Group by jurisdiction
        nj_articles = [a for a in self.filtered_articles if a['jurisdiction'] == 'New Jersey']
        ny_articles = [a for a in self.filtered_articles if a['jurisdiction'] == 'New York']
        local825_specific = [a for a in self.filtered_articles if a['jurisdiction'] == 'Local 825 Specific']
        
        report = f"""
LOCAL 825 OPERATING ENGINEERS INTELLIGENCE REPORT
================================================
Date: {self.today}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Articles Analyzed: {len(self.articles)}
Local 825 Relevant Articles: {len(self.filtered_articles)}

JURISDICTION BREAKDOWN
======================
• New Jersey: {len(nj_articles)} articles
• New York: {len(ny_articles)} articles  
• Local 825 Specific: {len(local825_specific)} articles

EXECUTIVE SUMMARY
-----------------
• {len(self.filtered_articles)} high-relevance articles for Local 825 jurisdiction
• Top categories: {', '.join(set([a['category'] for a in self.filtered_articles[:5]]))}
• Key sources: {', '.join(set([a['source'] for a in self.filtered_articles[:5]]))}

LOCAL 825 SPECIFIC ARTICLES
===========================
"""
        
        # Show Local 825 specific articles first
        if local825_specific:
            for article in local825_specific[:5]:
                report += f"""
🎯 {article['title']}
   Source: {article['source']}
   Relevance Score: {article['relevance_score']}
   Category: {article['category']}
   Keywords: {', '.join(article['matched_keywords'][:3])}
   URL: {article['url']}
   Published: {article['published']}
"""
        
        # New Jersey articles
        if nj_articles:
            report += f"\nNEW JERSEY FOCUS\n{'-' * 20}\n"
            for article in nj_articles[:5]:
                report += f"""
📰 {article['title']}
   Source: {article['source']}
   Relevance Score: {article['relevance_score']}
   Category: {article['category']}
   Keywords: {', '.join(article['matched_keywords'][:3])}
   URL: {article['url']}
   Published: {article['published']}
"""
        
        # New York articles
        if ny_articles:
            report += f"\nNEW YORK FOCUS\n{'-' * 15}\n"
            for article in ny_articles[:5]:
                report += f"""
📰 {article['title']}
   Source: {article['source']}
   Relevance Score: {article['relevance_score']}
   Category: {article['category']}
   Keywords: {', '.join(article['matched_keywords'][:3])}
   URL: {article['url']}
   Published: {article['published']}
"""
        
        # Group remaining articles by category
        categories = {}
        for article in self.filtered_articles:
            if article not in local825_specific + nj_articles + ny_articles:  # Skip already shown articles
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
   Jurisdiction: {article['jurisdiction']}
   Keywords: {', '.join(article['matched_keywords'][:3])}
   URL: {article['url']}
   Published: {article['published']}
"""
        
        report += f"""

STRATEGIC INSIGHTS FOR LOCAL 825
================================
• High-priority articles: {len([a for a in self.filtered_articles if a['relevance_score'] >= 7])}
• NJ focus articles: {len(nj_articles)}
• NY focus articles: {len(ny_articles)}
• Local 825 specific: {len(local825_specific)}

RECOMMENDATIONS FOR LOCAL 825 LEADERSHIP
========================================
• Monitor {len(self.filtered_articles)} relevant articles for Local 825 impact
• Focus on {len([a for a in self.filtered_articles if a['relevance_score'] >= 6])} high-relevance stories
• Prioritize {len(nj_articles)} NJ-focused developments
• Track {len(ny_articles)} NY territory developments
• Review {len(local825_specific)} Local 825 specific stories

NEXT STEPS
==========
• Investigate high-scoring construction projects for organizing opportunities
• Monitor labor disputes in Local 825 jurisdiction
• Track infrastructure bill project announcements
• Review prevailing wage compliance issues
• Analyze contract negotiation patterns

---
Generated by: Local 825 Targeted Intelligence System
Contact: jeremy@augments.art
© 2025 Local 825 Operating Engineers - Intelligence Division
"""
        
        return report
    
    def save_report(self, filename=None):
        """Save the Local 825 intelligence report to file"""
        if not filename:
            filename = f"reports/local825_intelligence_{self.today}.txt"
        
        report = self.generate_local825_intelligence_report()
        
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"💾 Local 825 report saved to: {filename}")
        return filename
    
    def save_json_data(self, filename=None):
        """Save structured data as JSON for further processing"""
        if not filename:
            filename = f"reports/local825_intelligence_{self.today}.json"
        
        data = {
            'metadata': {
                'date': self.today,
                'generated_at': datetime.now().isoformat(),
                'total_articles': len(self.articles),
                'relevant_articles': len(self.filtered_articles),
                'jurisdiction_breakdown': {
                    'new_jersey': len([a for a in self.filtered_articles if a['jurisdiction'] == 'New Jersey']),
                    'new_york': len([a for a in self.filtered_articles if a['jurisdiction'] == 'New York']),
                    'local825_specific': len([a for a in self.filtered_articles if a['jurisdiction'] == 'Local 825 Specific'])
                }
            },
            'articles': self.filtered_articles
        }
        
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"💾 JSON data saved to: {filename}")
        return filename

def main():
    """Main execution function"""
    print("🎯 Local 825 Targeted Intelligence System")
    print("=" * 50)
    print("Focus: New Jersey and relevant New York territories")
    print("=" * 50)
    
    system = Local825TargetedIntelligenceSystem()
    
    # Scrape all sources with Local 825 focus
    articles = system.scrape_all_local825_sources()
    
    if articles:
        # Generate and save reports
        report_file = system.save_report()
        json_file = system.save_json_data()
        
        # Display summary
        print(f"\n🎉 Local 825 targeted scraping completed successfully!")
        print(f"📊 Found {len(articles)} relevant articles")
        print(f"📋 Local 825 report saved to: {report_file}")
        print(f"💾 JSON data saved to: {json_file}")
        
        # Show jurisdiction breakdown
        nj_count = len([a for a in articles if a['jurisdiction'] == 'New Jersey'])
        ny_count = len([a for a in articles if a['jurisdiction'] == 'New York'])
        local825_count = len([a for a in articles if a['jurisdiction'] == 'Local 825 Specific'])
        
        print(f"\n🗺️ Jurisdiction Breakdown:")
        print(f"   New Jersey: {nj_count} articles")
        print(f"   New York: {ny_count} articles")
        print(f"   Local 825 Specific: {local825_count} articles")
        
        # Show top articles
        print(f"\n🔝 Top 3 Most Relevant Articles:")
        for i, article in enumerate(articles[:3], 1):
            print(f"{i}. {article['title']} (Score: {article['relevance_score']}, {article['jurisdiction']})")
    else:
        print("❌ No Local 825 relevant articles found. Check your keywords or try different search terms.")

if __name__ == "__main__":
    main()
