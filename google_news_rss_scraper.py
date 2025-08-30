#!/usr/bin/env python3
"""
Google News RSS Feed Scraper for Labor Intelligence
Uses Google News RSS feeds with targeted keywords to extract relevant labor and union news
"""

import os
import requests
import feedparser
import re
import time
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, quote_plus
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class GoogleNewsRSSScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': os.getenv('USER_AGENT', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        }
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.articles = []
        self.filtered_articles = []
        
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
            print(f"🔍 Scraping RSS: {query}")
            
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
                        'scraped_at': datetime.now().isoformat()
                    }
                    articles.append(article)
                
                print(f"✅ Found {len(articles)} articles for: {query}")
                return articles
            else:
                print(f"❌ Failed to fetch RSS for {query}: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error scraping RSS for {query}: {e}")
            return []
    
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
    
    def scrape_all_sources(self):
        """Scrape all Google News RSS sources"""
        print("🚀 Starting Google News RSS scraping...")
        
        queries = self.build_search_queries()
        all_articles = []
        
        for query in queries:
            articles = self.scrape_google_news_rss(query)
            all_articles.extend(articles)
            time.sleep(1)  # Be respectful to Google's servers
        
        # Remove duplicates based on URL
        unique_articles = {}
        for article in all_articles:
            if article['url'] not in unique_articles:
                unique_articles[article['url']] = article
        
        self.articles = list(unique_articles.values())
        print(f"📰 Total unique articles found: {len(self.articles)}")
        
        # Filter for relevance
        self.filtered_articles = self.filter_articles_by_relevance(self.articles)
        print(f"✅ Relevant articles after filtering: {len(self.filtered_articles)}")
        
        return self.filtered_articles
    
    def generate_intelligence_report(self):
        """Generate comprehensive labor intelligence report"""
        if not self.filtered_articles:
            return "No relevant articles found to analyze."
        
        report = f"""
LABOR INTELLIGENCE REPORT - GOOGLE NEWS RSS ANALYSIS
====================================================
Date: {self.today}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Articles Analyzed: {len(self.articles)}
Relevant Articles: {len(self.filtered_articles)}

EXECUTIVE SUMMARY
-----------------
• {len(self.filtered_articles)} high-relevance labor articles identified
• Top categories: {', '.join(set([a['category'] for a in self.filtered_articles[:5]]))}
• Key sources: {', '.join(set([a['source'] for a in self.filtered_articles[:5]]))}

DETAILED ARTICLE ANALYSIS
=========================
"""
        
        # Group by category
        categories = {}
        for article in self.filtered_articles:
            cat = article['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(article)
        
        for category, articles in categories.items():
            report += f"\n{category.upper()}\n{'-' * len(category)}\n"
            for article in articles[:5]:  # Top 5 per category
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

RECOMMENDATIONS
===============
• Monitor {len(self.filtered_articles)} relevant articles for Local 825 impact
• Focus on {len([a for a in self.filtered_articles if a['relevance_score'] >= 4])} high-relevance stories
• Track {len(set([a['source'] for a in self.filtered_articles]))} news sources for ongoing monitoring

---
Generated by: Google News RSS Labor Intelligence System
Contact: jeremy@augments.art
© 2025 Labor Intelligence Division
"""
        
        return report
    
    def save_report(self, filename=None):
        """Save the intelligence report to file"""
        if not filename:
            filename = f"reports/google_news_labor_intelligence_{self.today}.txt"
        
        report = self.generate_intelligence_report()
        
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"💾 Report saved to: {filename}")
        return filename

def main():
    """Main execution function"""
    print("🌐 Google News RSS Labor Intelligence Scraper")
    print("=" * 50)
    
    scraper = GoogleNewsRSSScraper()
    
    # Scrape all sources
    articles = scraper.scrape_all_sources()
    
    if articles:
        # Generate and save report
        report_file = scraper.save_report()
        
        # Display summary
        print(f"\n🎉 Scraping completed successfully!")
        print(f"📊 Found {len(articles)} relevant articles")
        print(f"📋 Report saved to: {report_file}")
        
        # Show top articles
        print(f"\n🔝 Top 3 Most Relevant Articles:")
        for i, article in enumerate(articles[:3], 1):
            print(f"{i}. {article['title']} (Score: {article['relevance_score']})")
    else:
        print("❌ No relevant articles found. Check your keywords or try different search terms.")

if __name__ == "__main__":
    main()
