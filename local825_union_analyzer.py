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

class Local825UnionAnalyzer:
    def __init__(self):
        self.base_url = "https://datapilotplus.com"
        self.headers = {'User-Agent': os.getenv('USER_AGENT')}
        self.today = datetime.now().strftime('%B %d, %Y')
        self.local825_articles = []
        self.job_listings = []
        self.sources_found = set()
        
    def scrape_local825_category(self):
        """Scrape specifically the Local 825 category"""
        print("🏗️ Scraping Local 825 News articles...")
        
        # Try different patterns
        category_urls = [
            f"{self.base_url}/category/category-local-825/",
            f"{self.base_url}/category/category-local-825",
            f"{self.base_url}/category-local-825/",
        ]
        
        for url in category_urls:
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    print(f"✅ Found Local 825 category at: {url}")
                    return BeautifulSoup(response.content, 'html.parser'), url
            except Exception as e:
                print(f"❌ Failed to access {url}: {e}")
                continue
        
        # If category not found, scrape homepage
        print("🔍 Category page not found, filtering from homepage...")
        response = requests.get(self.base_url, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup, self.base_url
    
    def extract_local825_articles(self, soup, source_url):
        """Extract Local 825 specific articles"""
        articles = []
        
        # Look for articles tagged with Local 825
        article_elements = soup.find_all('article', class_=lambda x: 'category-local-825' in ' '.join(x).lower())
        
        for article in article_elements:
            title_elem = article.find(['h1', 'h2', 'h3', 'h4'], recursive=True)
            if title_elem:
                link_elem = title_elem.find('a', href=True)
                if link_elem:
                    title = link_elem.get_text(strip=True)
                    url = link_elem.get('href')
                    
                    if url.startswith('/'):
                        url = urljoin(self.base_url, url)
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'category': 'Local 825 News',
                        'element': article
                    })
        
        print(f"📰 Found {len(articles)} Local 825 news articles")
        return articles
    
    def extract_job_listings(self, soup):
        """Extract job listings for union analysis"""
        jobs = []
        
        job_indicators = ['job', 'position', 'hiring', 'employment', 'worker', 'operator', 'engineer']
        
        all_articles = soup.find_all('article', class_=lambda x: x and 'post' in ' '.join(x).lower())
        
        for article in all_articles:
            article_text = article.get_text().lower()
            title_elem = article.find(['h1', 'h2', 'h3', 'h4'], recursive=True)
            
            if title_elem:
                title = title_elem.get_text(strip=True)
                title_lower = title.lower()
                
                if any(indicator in title_lower for indicator in job_indicators):
                    link_elem = title_elem.find('a', href=True)
                    if link_elem:
                        url = link_elem.get('href')
                        if url.startswith('/'):
                            url = urljoin(self.base_url, url)
                        
                        jobs.append({
                            'title': title,
                            'url': url,
                            'category': 'Job Listing',
                            'element': article
                        })
        
        print(f"💼 Found {len(jobs)} job listings for analysis")
        return jobs
    
    def analyze_article_content(self, article_info):
        """Extract detailed content and source from individual article"""
        try:
            print(f"📖 Analyzing: {article_info['title'][:60]}...")
            time.sleep(1)  # Be respectful
            
            response = requests.get(article_info['url'], headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
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
            
            source_url = self.extract_source_url(soup, content)
            union_analysis = self.analyze_union_implications(content, article_info['category'])
            
            details = {
                'title': article_info['title'],
                'url': article_info['url'],
                'category': article_info['category'],
                'content': content[:2000] + "..." if len(content) > 2000 else content,
                'full_content': content,
                'source_url': source_url,
                'word_count': len(content.split()),
                'union_analysis': union_analysis,
                'date_analyzed': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if source_url:
                self.sources_found.add(source_url)
            
            return details
            
        except Exception as e:
            print(f"❌ Error analyzing {article_info['url']}: {e}")
            return None
    
    def extract_source_url(self, soup, content):
        """Extract the original source URL from the curated post"""
        source_patterns = [
            r'source:\s*(https?://[^\s]+)',
            r'via\s+(https?://[^\s]+)',
            r'originally published at\s*(https?://[^\s]+)',
            r'read more:\s*(https?://[^\s]+)',
            r'full article:\s*(https?://[^\s]+)'
        ]
        
        for pattern in source_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        external_links = soup.find_all('a', href=True)
        for link in external_links:
            href = link.get('href')
            text = link.get_text(strip=True).lower()
            
            if (href.startswith('http') and 
                'datapilotplus.com' not in href and 
                'jobviewtrack.com' not in href and
                any(indicator in text for indicator in ['source', 'original', 'full article', 'read more', 'via'])):
                return href
        
        for link in external_links:
            href = link.get('href')
            if (href.startswith('http') and 
                'datapilotplus.com' not in href and 
                'jobviewtrack.com' not in href and
                any(domain in href for domain in ['.com', '.org', '.net', '.gov']) and
                len(link.get_text(strip=True)) > 10):
                return href
        
        return None
    
    def analyze_union_implications(self, content, category):
        """Analyze content from a Local 825 labor organizer perspective"""
        analysis = {
            'union_relevance': 'Low',
            'labor_issues': [],
            'organizing_opportunities': [],
            'wage_benefits_mentions': [],
            'safety_concerns': [],
            'employer_relations': [],
            'strategic_importance': 'Low',
            'action_items': []
        }
        
        content_lower = content.lower()
        
        high_relevance_terms = ['union', 'local 825', 'collective bargaining', 'strike', 'labor dispute', 'organizing']
        medium_relevance_terms = ['wages', 'benefits', 'safety', 'working conditions', 'employment', 'contract']
        
        high_score = sum(1 for term in high_relevance_terms if term in content_lower)
        medium_score = sum(1 for term in medium_relevance_terms if term in content_lower)
        
        if high_score >= 2:
            analysis['union_relevance'] = 'High'
        elif high_score >= 1 or medium_score >= 3:
            analysis['union_relevance'] = 'Medium'
        
        labor_terms = {
            'wage_issues': ['wage', 'pay', 'salary', 'compensation', 'overtime'],
            'safety_issues': ['safety', 'accident', 'injury', 'hazard', 'osha'],
            'benefits': ['health insurance', 'pension', 'retirement', 'benefits', 'vacation'],
            'working_conditions': ['working conditions', 'hours', 'shift', 'workplace'],
            'job_security': ['layoff', 'downsizing', 'job security', 'employment'],
            'training': ['training', 'apprentice', 'education', 'certification']
        }
        
        for category_name, terms in labor_terms.items():
            found_terms = [term for term in terms if term in content_lower]
            if found_terms:
                analysis['labor_issues'].append({
                    'category': category_name,
                    'terms_found': found_terms
                })
        
        if category == 'Job Listing':
            analysis.update(self.analyze_job_from_union_perspective(content))
        
        strategic_indicators = ['new construction', 'infrastructure', 'public works', 'government contract']
        if any(indicator in content_lower for indicator in strategic_indicators):
            analysis['strategic_importance'] = 'High'
        elif any(indicator in content_lower for indicator in ['private sector', 'commercial']):
            analysis['strategic_importance'] = 'Medium'
        
        if analysis['union_relevance'] == 'High':
            analysis['action_items'].append('Priority review for union leadership')
        if 'safety' in str(analysis['labor_issues']):
            analysis['action_items'].append('Safety committee review recommended')
        if category == 'Job Listing' and analysis['strategic_importance'] == 'High':
            analysis['action_items'].append('Consider organizing outreach to workers')
        
        return analysis
    
    def analyze_job_from_union_perspective(self, content):
        """Specific analysis for job listings from union organizer viewpoint"""
        job_analysis = {
            'job_type': 'Unknown',
            'union_potential': 'Low',
            'wage_analysis': 'Not specified',
            'employer_type': 'Unknown',
            'organizing_difficulty': 'Unknown',
            'union_recommendations': []
        }
        
        content_lower = content.lower()
        
        job_types = {
            'operator': ['operator', 'equipment operator', 'crane operator'],
            'engineer': ['engineer', 'civil engineer', 'design engineer'],
            'construction': ['construction', 'builder', 'contractor'],
            'manufacturing': ['production', 'manufacturing', 'factory'],
            'maintenance': ['maintenance', 'mechanic', 'technician']
        }
        
        for job_type, terms in job_types.items():
            if any(term in content_lower for term in terms):
                job_analysis['job_type'] = job_type
                break
        
        high_potential_indicators = ['large employer', 'government', 'public sector', 'infrastructure']
        medium_potential_indicators = ['construction', 'manufacturing', 'industrial']
        
        if any(indicator in content_lower for indicator in high_potential_indicators):
            job_analysis['union_potential'] = 'High'
        elif any(indicator in content_lower for indicator in medium_potential_indicators):
            job_analysis['union_potential'] = 'Medium'
        
        wage_patterns = [r'\$(\d+)[.,]?\d*\s*(?:per hour|/hour|hr)', r'\$(\d+)[,.]?\d*k?\s*(?:annually|per year|/year)']
        for pattern in wage_patterns:
            match = re.search(pattern, content_lower)
            if match:
                job_analysis['wage_analysis'] = f"${match.group(1)} mentioned"
                break
        
        if job_analysis['union_potential'] == 'High':
            job_analysis['union_recommendations'].append('High priority for organizing campaign')
        if 'government' in content_lower or 'public' in content_lower:
            job_analysis['union_recommendations'].append('Leverage public sector organizing advantages')
        if job_analysis['job_type'] in ['operator', 'construction']:
            job_analysis['union_recommendations'].append('Good fit for Local 825 membership')
        
        return job_analysis
    
    def generate_union_report(self, local825_articles, job_listings):
        """Generate comprehensive Local 825 union organizer report"""
        
        report = f"""LOCAL 825 DAILY LABOR INTELLIGENCE REPORT
==========================================
Date: {self.today}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Prepared for: Local 825 Union Leadership

EXECUTIVE SUMMARY
-----------------
• {len(local825_articles)} Local 825 news articles analyzed
• {len(job_listings)} job opportunities reviewed from union perspective  
• {len(self.sources_found)} unique sources monitored
• Strategic labor market intelligence for organizing and member services

"""

        if local825_articles:
            report += f"""
LOCAL 825 NEWS ANALYSIS
=======================

Total Articles: {len(local825_articles)}

High Priority Articles:
"""
            high_priority = [a for a in local825_articles if a and a.get('union_analysis', {}).get('union_relevance') == 'High']
            
            for article in high_priority:
                report += f"""
📰 {article['title']}
   Source: {article.get('source_url', 'Direct reporting')}
   Union Relevance: {article['union_analysis']['union_relevance']}
   Strategic Importance: {article['union_analysis']['strategic_importance']}
   Action Items: {', '.join(article['union_analysis']['action_items']) if article['union_analysis']['action_items'] else 'None'}
   
   Labor Issues Identified:
"""
                for issue in article['union_analysis']['labor_issues']:
                    report += f"   • {issue['category'].replace('_', ' ').title()}: {', '.join(issue['terms_found'])}\n"
                
                report += f"   \n   Content Summary: {article['content'][:300]}...\n"
                report += f"   Full Article: {article['url']}\n"
                report += "   " + "-" * 70 + "\n"

        if job_listings:
            report += f"""

JOB MARKET INTELLIGENCE FOR LOCAL 825
======================================

Total Jobs Analyzed: {len(job_listings)}

HIGH ORGANIZING POTENTIAL JOBS:
"""
            high_potential_jobs = [j for j in job_listings if j and j.get('union_analysis', {}).get('union_potential') == 'High']
            
            for job in high_potential_jobs:
                if 'job_type' in job['union_analysis']:
                    job_details = job['union_analysis']
                    report += f"""
💼 {job['title']}
   Job Type: {job_details.get('job_type', 'Unknown')}
   Union Potential: {job_details.get('union_potential', 'Unknown')}
   Organizing Difficulty: {job_details.get('organizing_difficulty', 'Unknown')}
   Wage Info: {job_details.get('wage_analysis', 'Not specified')}
   
   Union Recommendations:
"""
                    for rec in job_details.get('union_recommendations', []):
                        report += f"   • {rec}\n"
                    
                    report += f"   \n   Source: {job.get('source_url', 'Direct posting')}\n"
                    report += f"   Job Posting: {job['url']}\n"
                    report += "   " + "-" * 70 + "\n"

            all_job_types = {}
            union_potential_summary = {'High': 0, 'Medium': 0, 'Low': 0}
            
            for job in job_listings:
                if job and 'union_analysis' in job:
                    job_type = job['union_analysis'].get('job_type', 'Unknown')
                    all_job_types[job_type] = all_job_types.get(job_type, 0) + 1
                    
                    potential = job['union_analysis'].get('union_potential', 'Low')
                    union_potential_summary[potential] = union_potential_summary.get(potential, 0) + 1

            report += f"""

JOB MARKET TRENDS ANALYSIS:
"""
            report += f"Job Types Distribution:\n"
            for job_type, count in sorted(all_job_types.items(), key=lambda x: x[1], reverse=True):
                report += f"  • {job_type.title()}: {count} positions\n"
            
            report += f"\nUnion Organizing Potential:\n"
            for potential, count in union_potential_summary.items():
                report += f"  • {potential} Potential: {count} positions\n"

        report += f"""

STRATEGIC RECOMMENDATIONS FOR LOCAL 825
========================================

IMMEDIATE ACTIONS:
• Review {len([a for a in local825_articles if a and a.get('union_analysis', {}).get('union_relevance') == 'High'])} high-priority news articles for potential member impact
• Target {len([j for j in job_listings if j and j.get('union_analysis', {}).get('union_potential') == 'High'])} high-potential job opportunities for organizing outreach
• Monitor sources: {', '.join(list(self.sources_found)[:5])}

ORGANIZING OPPORTUNITIES:
"""
        
        construction_jobs = len([j for j in job_listings if j and 'construction' in j.get('union_analysis', {}).get('job_type', '').lower()])
        operator_jobs = len([j for j in job_listings if j and 'operator' in j.get('union_analysis', {}).get('job_type', '').lower()])
        
        if construction_jobs > 0:
            report += f"• {construction_jobs} construction-related positions - prime for Local 825 membership\n"
        if operator_jobs > 0:
            report += f"• {operator_jobs} equipment operator positions - core Local 825 trade\n"

        report += f"""

MEMBER SERVICES ALERTS:
• Monitor wage trends in tracked positions for contract negotiations
• Safety issues identified: Review articles for potential safety concerns affecting members
• Training opportunities: Look for apprenticeship and certification programs

SOURCES MONITORED:
"""
        for source in sorted(self.sources_found):
            parsed_url = urlparse(source)
            report += f"• {parsed_url.netloc}\n"

        report += f"""

METHODOLOGY:
• Data source: datapilotplus.com curated labor intelligence
• Focus areas: Local 825 news category and relevant job postings
• Analysis framework: Union organizing potential, member impact, strategic value
• Update frequency: Daily monitoring and analysis

This intelligence report supports Local 825's organizing efforts, member services,
and strategic planning with actionable labor market insights.

---
Prepared by: Henjii Labor Intelligence System
For: Local 825 Operating Engineers Union
Contact: jeremy@augments.art
© 2025 Bulldozer Insights - Labor Intelligence Division
"""
        
        return report
    
    def send_union_report(self, report_content):
        """Send the union-focused report via email"""
        try:
            report_path = f"reports/local825_union_report_{datetime.now().strftime('%Y%m%d')}.txt"
            os.makedirs('reports', exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            smtp_server = os.getenv('SMTP_SERVER')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            email_user = os.getenv('EMAIL_USER')
            email_password = os.getenv('EMAIL_PASSWORD')
            sender_email = os.getenv('SENDER_EMAIL', 'jeremy@augments.art')
            recipients = os.getenv('REPORT_RECIPIENTS', '').split(',')
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"Local 825 Daily Labor Intelligence Report - {self.today}"
            
            body = f"""Local 825 Leadership,

Please find attached today's labor intelligence report with union-focused analysis.

TODAY'S INTELLIGENCE HIGHLIGHTS:
• {len(self.local825_articles)} Local 825 news articles reviewed
• {len(self.job_listings)} job opportunities analyzed for organizing potential
• {len(self.sources_found)} sources monitored for labor developments

This report provides strategic intelligence for:
- Organizing campaign opportunities
- Member service alerts  
- Industry trend analysis
- Employer relations insights

The analysis is prepared specifically for Local 825's organizing and strategic needs.

In Solidarity,
Henjii Labor Intelligence Division

Report Date: {self.today}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            with open(report_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(report_path)}'
            )
            msg.attach(part)
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_user, email_password)
            server.sendmail(sender_email, recipients, msg.as_string())
            server.quit()
            
            print(f"📧 Local 825 union report sent to: {', '.join(recipients)}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send union report: {e}")
            return False
    
    def run_local825_analysis(self):
        """Run the complete Local 825 union analysis"""
        print(f"🏗️ LOCAL 825 LABOR INTELLIGENCE ANALYSIS")
        print(f"Date: {self.today}")
        print("=" * 60)
        
        try:
            soup, source_url = self.scrape_local825_category()
            self.local825_articles = self.extract_local825_articles(soup, source_url)
            self.job_listings = self.extract_job_listings(soup)
            
            print("🔍 Analyzing Local 825 news articles...")
            analyzed_articles = []
            for article in self.local825_articles:
                details = self.analyze_article_content(article)
                if details:
                    analyzed_articles.append(details)
            
            print("💼 Analyzing job listings for union opportunities...")
            analyzed_jobs = []
            for job in self.job_listings[:15]:
                details = self.analyze_article_content(job)
                if details:
                    analyzed_jobs.append(details)
            
            print(f"✅ Analysis complete:")
            print(f"   📰 {len(analyzed_articles)} Local 825 articles analyzed")
            print(f"   💼 {len(analyzed_jobs)} job opportunities reviewed")
            print(f"   🔗 {len(self.sources_found)} sources identified")
            
            print("📋 Generating Local 825 intelligence report...")
            report = self.generate_union_report(analyzed_articles, analyzed_jobs)
            print("📧 Sending union intelligence report...")
            self.send_union_report(report)
            
            print("🎉 Local 825 labor intelligence analysis completed!")
            
        except Exception as e:
            print(f"❌ Error during Local 825 analysis: {e}")
            raise

if __name__ == "__main__":
    analyzer = Local825UnionAnalyzer()
    analyzer.run_local825_analysis()
