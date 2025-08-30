import os
import requests
import time
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Load environment variables
load_dotenv()

class EnhancedDailyReporter:
    def __init__(self):
        self.base_url = "https://datapilotplus.com"
        self.headers = {'User-Agent': os.getenv('USER_AGENT')}
        self.today = datetime.now().strftime('%B %d, %Y')
        self.articles_analyzed = 0
        self.sources_found = set()
        
    def scrape_homepage(self):
        """Scrape the homepage to find all articles"""
        print("📰 Scraping datapilotplus.com homepage...")
        response = requests.get(self.base_url, headers=self.headers)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    
    def extract_article_links(self, soup):
        """Extract all article links from the homepage"""
        article_links = []
        
        # Find articles by looking for post/article elements
        articles = soup.find_all('article', class_=lambda x: x and 'post' in ' '.join(x).lower())
        
        for article in articles:
            # Look for title links
            title_link = article.find('h3')
            if title_link:
                link_element = title_link.find('a', href=True)
                if link_element:
                    url = link_element.get('href')
                    title = link_element.get_text(strip=True)
                    
                    # Make sure it's a full URL
                    if url.startswith('/'):
                        url = urljoin(self.base_url, url)
                    
                    article_links.append({
                        'url': url,
                        'title': title,
                        'element': article
                    })
        
        # Also look for direct links to datapilotplus.com articles
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href')
            if 'datapilotplus.com' in href and href not in [a['url'] for a in article_links]:
                title = link.get_text(strip=True)
                if title and len(title) > 10:  # Filter out short/empty titles
                    article_links.append({
                        'url': href,
                        'title': title,
                        'element': link
                    })
        
        print(f"🔗 Found {len(article_links)} article links")
        return article_links
    
    def extract_article_details(self, article_info):
        """Extract detailed information from a single article"""
        try:
            print(f"📖 Analyzing: {article_info['title'][:60]}...")
            
            # Add delay to be respectful
            time.sleep(1)
            
            response = requests.get(article_info['url'], headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract article content
            content_selectors = [
                'article .entry-content',
                '.post-content',
                '.article-content', 
                'article',
                '.content'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(separator=' ', strip=True)
                    break
            
            # Extract sources and citations
            sources = self.extract_sources(soup)
            
            # Extract key details
            details = {
                'title': article_info['title'],
                'url': article_info['url'],
                'content': content[:1000] + "..." if len(content) > 1000 else content,
                'full_content': content,
                'sources': sources,
                'word_count': len(content.split()),
                'date_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Extract key entities and topics
            details['key_topics'] = self.extract_key_topics(content)
            details['companies'] = self.extract_companies(content)
            details['locations'] = self.extract_locations(content)
            
            self.articles_analyzed += 1
            self.sources_found.update(sources)
            
            return details
            
        except Exception as e:
            print(f"❌ Error analyzing {article_info['url']}: {e}")
            return None
    
    def extract_sources(self, soup):
        """Extract source citations from article"""
        sources = []
        
        # Look for external links as sources
        external_links = soup.find_all('a', href=True)
        for link in external_links:
            href = link.get('href')
            text = link.get_text(strip=True)
            
            # Filter for actual sources (exclude internal links, ads, etc.)
            if (href.startswith('http') and 
                'datapilotplus.com' not in href and 
                'jobviewtrack.com' not in href and
                text and len(text) > 3):
                
                domain = urlparse(href).netloc
                sources.append({
                    'url': href,
                    'text': text[:100],
                    'domain': domain
                })
        
        return sources
    
    def extract_key_topics(self, content):
        """Extract key topics from content using keyword analysis"""
        # Common labor/construction/job keywords
        keywords = {
            'job_types': ['engineer', 'operator', 'technician', 'manager', 'worker', 'supervisor'],
            'industries': ['construction', 'manufacturing', 'tech', 'energy', 'aerospace', 'infrastructure'],
            'locations': ['new jersey', 'new york', 'pennsylvania', 'boise', 'fort monmouth'],
            'companies': ['howmet', 'netflix', 'portal', 'helix', 'palumbo'],
            'labor_terms': ['union', 'labor', 'jobs', 'hiring', 'employment', 'wages', 'benefits']
        }
        
        found_topics = {}
        content_lower = content.lower()
        
        for category, terms in keywords.items():
            found_topics[category] = [term for term in terms if term in content_lower]
        
        return found_topics
    
    def extract_companies(self, content):
        """Extract company names from content"""
        # Simple company extraction - look for capitalized words followed by common suffixes
        company_pattern = r'\b[A-Z][a-zA-Z]+ (?:Inc|Corp|Corporation|LLC|Ltd|Company|Group|Industries|Aerospace|Innovations)\b'
        companies = re.findall(company_pattern, content)
        return list(set(companies))
    
    def extract_locations(self, content):
        """Extract location names from content"""
        # Common location patterns
        location_patterns = [
            r'\b[A-Z][a-zA-Z]+, [A-Z]{2}\b',  # City, State
            r'\b(?:New Jersey|New York|Pennsylvania|California|Texas|Florida|Boise|Dover)\b'  # State names
        ]
        
        locations = []
        for pattern in location_patterns:
            locations.extend(re.findall(pattern, content))
        
        return list(set(locations))
    
    def analyze_trends(self, articles_data):
        """Analyze trends across all articles"""
        trends = {
            'total_articles': len(articles_data),
            'total_word_count': sum(a['word_count'] for a in articles_data if a),
            'top_companies': {},
            'top_locations': {},
            'industry_focus': {},
            'job_categories': {},
            'source_domains': {},
            'key_insights': []
        }
        
        # Aggregate data
        all_companies = []
        all_locations = []
        all_topics = {'industries': [], 'job_types': [], 'labor_terms': []}
        
        for article in articles_data:
            if article:
                all_companies.extend(article.get('companies', []))
                all_locations.extend(article.get('locations', []))
                
                for topic_type in all_topics:
                    all_topics[topic_type].extend(article.get('key_topics', {}).get(topic_type, []))
        
        # Count frequencies
        trends['top_companies'] = self.count_frequencies(all_companies)
        trends['top_locations'] = self.count_frequencies(all_locations)
        trends['industry_focus'] = self.count_frequencies(all_topics['industries'])
        trends['job_categories'] = self.count_frequencies(all_topics['job_types'])
        
        # Source analysis
        all_sources = []
        for article in articles_data:
            if article:
                all_sources.extend([s['domain'] for s in article.get('sources', [])])
        trends['source_domains'] = self.count_frequencies(all_sources)
        
        # Generate insights
        trends['key_insights'] = self.generate_insights(trends)
        
        return trends
    
    def count_frequencies(self, items):
        """Count frequency of items and return sorted dict"""
        freq = {}
        for item in items:
            freq[item] = freq.get(item, 0) + 1
        return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))
    
    def generate_insights(self, trends):
        """Generate key insights from trend data"""
        insights = []
        
        if trends['top_companies']:
            top_company = list(trends['top_companies'].keys())[0]
            insights.append(f"Most mentioned company: {top_company} ({trends['top_companies'][top_company]} mentions)")
        
        if trends['top_locations']:
            top_location = list(trends['top_locations'].keys())[0]
            insights.append(f"Primary location focus: {top_location} ({trends['top_locations'][top_location]} mentions)")
        
        if trends['industry_focus']:
            top_industry = list(trends['industry_focus'].keys())[0]
            insights.append(f"Leading industry: {top_industry} ({trends['industry_focus'][top_industry]} articles)")
        
        if trends['job_categories']:
            top_job = list(trends['job_categories'].keys())[0]
            insights.append(f"Most common job type: {top_job} ({trends['job_categories'][top_job]} mentions)")
        
        insights.append(f"Total articles analyzed: {trends['total_articles']}")
        insights.append(f"Average article length: {trends['total_word_count'] // max(trends['total_articles'], 1)} words")
        
        return insights
    
    def generate_comprehensive_report(self, articles_data, trends):
        """Generate a comprehensive daily report"""
        report = f"""datapilotplus.com DAILY LABOR MARKET ANALYSIS
========================================
Date: {self.today}
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY
-----------------
• {trends['total_articles']} articles analyzed from today's coverage
• {len(self.sources_found)} unique sources cited
• {trends['total_word_count']:,} total words of content analyzed
• Primary focus: {list(trends['industry_focus'].keys())[0] if trends['industry_focus'] else 'Mixed industries'}

KEY MARKET INSIGHTS
-------------------
"""
        
        for insight in trends['key_insights']:
            report += f"• {insight}\n"
        
        report += f"""

INDUSTRY ANALYSIS
-----------------
"""
        if trends['industry_focus']:
            report += "Top Industries by Article Count:\n"
            for industry, count in list(trends['industry_focus'].items())[:5]:
                report += f"  • {industry.title()}: {count} articles\n"
        
        report += f"""

GEOGRAPHIC FOCUS
----------------
"""
        if trends['top_locations']:
            report += "Most Mentioned Locations:\n"
            for location, count in list(trends['top_locations'].items())[:5]:
                report += f"  • {location}: {count} mentions\n"
        
        report += f"""

COMPANY SPOTLIGHT
-----------------
"""
        if trends['top_companies']:
            report += "Companies in Focus:\n"
            for company, count in list(trends['top_companies'].items())[:5]:
                report += f"  • {company}: {count} mentions\n"
        
        report += f"""

JOB MARKET TRENDS
-----------------
"""
        if trends['job_categories']:
            report += "Most In-Demand Roles:\n"
            for job, count in list(trends['job_categories'].items())[:5]:
                report += f"  • {job.title()}: {count} mentions\n"
        
        report += f"""

DETAILED ARTICLE ANALYSIS
--------------------------
"""
        
        for i, article in enumerate([a for a in articles_data if a], 1):
            report += f"""
Article {i}: {article['title']}
{'=' * (10 + len(str(i)) + len(article['title']))}
URL: {article['url']}
Word Count: {article['word_count']} words
Key Topics: {', '.join(article.get('key_topics', {}).get('industries', [])[:3])}

Content Summary:
{article['content']}

Sources Cited:
"""
            if article['sources']:
                for source in article['sources'][:3]:
                    report += f"  • {source['domain']}: {source['text']}\n    URL: {source['url']}\n"
            else:
                report += "  • No external sources cited\n"
            
            report += "\n" + "-" * 80 + "\n"
        
        report += f"""

SOURCE CREDIBILITY ANALYSIS
----------------------------
"""
        if trends['source_domains']:
            report += "Most Cited Source Domains:\n"
            for domain, count in list(trends['source_domains'].items())[:10]:
                report += f"  • {domain}: {count} citations\n"
        
        report += f"""

METHODOLOGY
-----------
• Data collected from: {self.base_url}
• Analysis period: {self.today}
• Articles processed: {len(articles_data)}
• Sources identified: {len(self.sources_found)}
• Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This report provides comprehensive analysis of today's labor market coverage
on datapilotplus.com, including industry trends, geographic focus, company mentions,
and source attribution for strategic decision-making.

---
Generated by Henjii Scraper Bot
© 2025 Bulldozer Insights
"""
        
        return report
    
    def send_email_report(self, report_content):
        """Send the comprehensive report via email"""
        try:
            # Save report to file first
            report_path = f"reports/comprehensive_daily_report_{datetime.now().strftime('%Y%m%d')}.txt"
            os.makedirs('reports', exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # Email configuration
            smtp_server = os.getenv('SMTP_SERVER')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            email_user = os.getenv('EMAIL_USER')
            email_password = os.getenv('EMAIL_PASSWORD')
            sender_email = os.getenv('SENDER_EMAIL', 'jeremy@augments.art')
            recipients = os.getenv('REPORT_RECIPIENTS', '').split(',')
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"Comprehensive Daily Labor Market Analysis - {self.today}"
            
            # Email body
            body = f"""Hello,

Please find attached today's comprehensive labor market analysis from datapilotplus.com.

KEY HIGHLIGHTS:
• {self.articles_analyzed} articles analyzed
• {len(self.sources_found)} unique sources cited
• Comprehensive industry, geographic, and company analysis included

This detailed report provides strategic insights into today's labor market trends,
job opportunities, and industry developments.

Best regards,
Henjii Analytics Bot

Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach the report file
            with open(report_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(report_path)}'
            )
            msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_user, email_password)
            server.sendmail(sender_email, recipients, msg.as_string())
            server.quit()
            
            print(f"📧 Comprehensive report successfully sent to: {', '.join(recipients)}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def run_comprehensive_analysis(self):
        """Run the complete comprehensive analysis"""
        print(f"🚀 Starting comprehensive daily analysis for {self.today}")
        print("=" * 60)
        
        try:
            # Step 1: Scrape homepage
            homepage_soup = self.scrape_homepage()
            
            # Step 2: Extract article links
            article_links = self.extract_article_links(homepage_soup)
            
            if not article_links:
                print("❌ No articles found!")
                return
            
            # Step 3: Analyze each article in detail
            print(f"🔍 Beginning detailed analysis of {len(article_links)} articles...")
            articles_data = []
            
            for i, article_info in enumerate(article_links[:10], 1):  # Limit to 10 for performance
                print(f"Progress: {i}/{min(len(article_links), 10)}")
                article_details = self.extract_article_details(article_info)
                if article_details:
                    articles_data.append(article_details)
            
            print(f"✅ Successfully analyzed {len(articles_data)} articles")
            
            # Step 4: Perform trend analysis
            print("📊 Analyzing trends and patterns...")
            trends = self.analyze_trends(articles_data)
            
            # Step 5: Generate comprehensive report
            print("📝 Generating comprehensive report...")
            report = self.generate_comprehensive_report(articles_data, trends)
            
            # Step 6: Send email
            print("📧 Sending email report...")
            self.send_email_report(report)
            
            print("🎉 Comprehensive daily analysis completed successfully!")
            print(f"📊 Final stats: {self.articles_analyzed} articles, {len(self.sources_found)} sources")
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            raise

if __name__ == "__main__":
    reporter = EnhancedDailyReporter()
    reporter.run_comprehensive_analysis()
