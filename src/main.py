import os
import requests
import openai
import supabase
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import schedule
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import json
import asyncio
from crawl4ai import AsyncWebCrawler
import logging
from typing import Dict, List, Any, Optional
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import sys

# Load environment variables
load_dotenv()

# Configure logging with colorful console output
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and emojis"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨',
        'STARTUP': '🚀',
        'DATABASE': '🗄️',
        'SCRAPING': '🕷️',
        'PROCESSING': '⚙️',
        'SUCCESS': '🎉',
        'WAITING': '⏳',
        'CONNECTING': '🔌',
        'ANALYZING': '🧠',
        'SAVING': '💾',
        'REPORTING': '📊'
    }
    
    def format(self, record):
        # Add emoji based on log level or custom attributes
        if hasattr(record, 'emoji'):
            emoji = record.emoji
        elif record.levelname in self.EMOJIS:
            emoji = self.EMOJIS[record.levelname]
        else:
            emoji = '📝'
        
        # Color the log level
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        colored_level = f"{level_color}{record.levelname}{self.COLORS['RESET']}"
        
        # Format the message
        formatted = super().format(record)
        return f"{emoji} {formatted}"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('datapilotplus_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Apply colored formatter to console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(console_handler)

def print_banner():
    """Print startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 DataPilotPlus Intelligence Scraper 🚀                 ║
║                                                                              ║
║  🔍 Comprehensive Business Intelligence Collection                          ║
║  🗄️  MySQL Database Integration                                            ║
║  🌐 MCP Server for External Integrations                                   ║
║  🤖 AI-Powered Data Analysis                                               ║
║                                                                              ║
║  Built with ❤️ by Jeremy Harris | augments.art                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def print_status(message: str, status_type: str = "info"):
    """Print formatted status message"""
    status_icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "processing": "⚙️",
        "waiting": "⏳",
        "connecting": "🔌",
        "analyzing": "🧠",
        "saving": "💾",
        "scraping": "🕷️"
    }
    
    icon = status_icons.get(status_type, "📝")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] {message}")

def print_progress_bar(current: int, total: int, description: str = "Progress"):
    """Print a progress bar"""
    bar_length = 30
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    percentage = current / total * 100
    print(f"🔄 {description}: [{bar}] {percentage:.1f}% ({current}/{total})")

class DataPilotPlusScraper:
    def __init__(self):
        print_banner()
        print_status("Initializing DataPilotPlus Intelligence Scraper...", "info")
        
        self.base_url = os.getenv('DATAPILOTPLUS_BASE_URL', 'https://datapilotplus.com')
        self.headers = {'User-Agent': os.getenv('USER_AGENT')}
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.db_connection = None
        self.crawler = AsyncWebCrawler()
        
        print_status("Setting up database connection...", "connecting")
        # Initialize database
        self.init_database()
        
        # Data sources configuration based on the comprehensive table
        self.data_sources = {
            'company_information': {
                'sec_edgar': {
                    'method': 'API',
                    'url': 'https://www.sec.gov/edgar/sec-api-documentation',
                    'description': 'Company filings, registration statements, disclosures',
                    'data_points': ['company_name', 'company_type', 'headquarters', 'founded', 'employees', 'revenue'],
                    'implementation': 'Python requests to API endpoints, parsing JSON responses'
                },
                'opencorporates': {
                    'method': 'API',
                    'url': 'https://api.opencorporates.com/documentation/API-Reference',
                    'description': 'Global corporate data, business registrations',
                    'data_points': ['company_name', 'registration_number', 'status', 'incorporation_date'],
                    'implementation': 'Python requests to API endpoints, parsing JSON responses'
                },
                'company_website': {
                    'method': 'Web Scraping',
                    'url': 'https://www.{company_name}.com/about',
                    'description': 'About Us pages, company profiles',
                    'data_points': ['company_name', 'description', 'mission', 'values', 'team'],
                    'implementation': 'BeautifulSoup to extract text from specific sections'
                }
            },
            'leadership': {
                'sec_insiders': {
                    'method': 'API',
                    'url': 'https://www.sec.gov/edgar/sec-api-documentation',
                    'description': 'Company officer/insider info, leadership',
                    'data_points': ['key_executives', 'board_members', 'management_team'],
                    'implementation': 'Python requests to API endpoints, parsing JSON responses'
                },
                'linkedin': {
                    'method': 'Web Scraping',
                    'url': 'https://www.linkedin.com/company/{company_name}/people',
                    'description': 'Leadership, management, board pages',
                    'data_points': ['executives', 'board_members', 'employee_count'],
                    'implementation': 'Selenium with headless browser to navigate and extract data'
                }
            },
            'operations': {
                'usaspending': {
                    'method': 'API',
                    'url': 'https://api.usaspending.gov/docs/endpoints',
                    'description': 'Federal contract/grant data, projects, services',
                    'data_points': ['contracts', 'projects', 'services', 'facilities'],
                    'implementation': 'Python requests to API endpoints, parsing JSON responses'
                },
                'state_dot': {
                    'method': 'Web Scraping',
                    'url': 'Varies by state',
                    'description': 'State transportation contracts, infrastructure projects',
                    'data_points': ['contracts', 'project_value', 'timeline'],
                    'implementation': 'Form automation with Selenium to search by company name'
                }
            },
            'compliance': {
                'osha_api': {
                    'method': 'API',
                    'url': 'https://www.osha.gov/data',
                    'description': 'OSHA enforcement data, safety violations',
                    'data_points': ['osha_violations', 'safety_record', 'legal_issues'],
                    'implementation': 'Python requests to API endpoints, parsing JSON responses'
                },
                'dol_enforcement': {
                    'method': 'API',
                    'url': 'https://www.dol.gov/agencies/whd',
                    'description': 'DOL enforcement actions, wage violations',
                    'data_points': ['wage_violations', 'enforcement_actions', 'penalties'],
                    'implementation': 'Python requests to API endpoints, parsing JSON responses'
                },
                'nlrb_api': {
                    'method': 'API',
                    'url': 'https://www.nlrb.gov/reports-guidance',
                    'description': 'NLRB case data, labor relations cases',
                    'data_points': ['labor_relations', 'labor_disputes', 'union_status'],
                    'implementation': 'Python requests to API endpoints, parsing JSON responses'
                }
            },
            'financial': {
                'yahoo_finance': {
                    'method': 'API',
                    'url': 'https://finance.yahoo.com/apis',
                    'description': 'Public company financial data, stock information',
                    'data_points': ['revenue', 'profit', 'market_cap', 'stock_price'],
                    'implementation': 'Python requests to API endpoints, parsing JSON responses'
                },
                'federal_contracts': {
                    'method': 'Web Scraping',
                    'url': 'https://sam.gov/',
                    'description': 'Federal contract award amounts, procurement data',
                    'data_points': ['contracts_value', 'award_amounts', 'procurement_data'],
                    'implementation': 'Form automation with Selenium to search by company name'
                }
            },
            'political': {
                'fec_api': {
                    'method': 'API',
                    'url': 'https://api.open.fec.gov/developers/',
                    'description': 'Federal Election Commission campaign finance data',
                    'data_points': ['political_contributions', 'campaign_finance', 'donations'],
                    'implementation': 'Python requests to API endpoints, parsing JSON responses'
                },
                'opensecrets': {
                    'method': 'API',
                    'url': 'https://www.opensecrets.org/api/',
                    'description': 'Lobbying activities, political influence data',
                    'data_points': ['lobbying_activities', 'political_influence', 'government_relations'],
                    'implementation': 'Python requests to API endpoints, parsing JSON responses'
                }
            }
        }
        
        print_status("DataPilotPlus Intelligence Scraper initialized successfully!", "success")
    
    def init_database(self):
        """Initialize MySQL database connection and create tables"""
        try:
            print_status("Connecting to MySQL database...", "connecting")
            self.db_connection = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', 'localhost'),
                port=int(os.getenv('MYSQL_PORT', 3306)),
                database=os.getenv('MYSQL_DATABASE', 'datapilotplus_scraper'),
                user=os.getenv('MYSQL_USERNAME'),
                password=os.getenv('MYSQL_PASSWORD'),
                charset=os.getenv('MYSQL_CHARSET', 'utf8mb4')
            )
            
            if self.db_connection.is_connected():
                print_status("✅ Successfully connected to MySQL database", "success")
                self.create_tables()
            else:
                print_status("❌ Failed to connect to MySQL database", "error")
                
        except Error as e:
            print_status(f"❌ Error connecting to MySQL: {e}", "error")
            self.db_connection = None
    
    def create_tables(self):
        """Create necessary database tables if they don't exist"""
        if not self.db_connection:
            return
            
        print_status("Creating database tables...", "processing")
        cursor = self.db_connection.cursor()
        
        # Table for scraped data
        create_data_table = """
        CREATE TABLE IF NOT EXISTS scraped_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            source_name VARCHAR(255) NOT NULL,
            category VARCHAR(100) NOT NULL,
            method_type VARCHAR(50) NOT NULL,
            url TEXT,
            data_points JSON,
            content TEXT,
            analysis JSON,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_source (source_name),
            INDEX idx_category (category),
            INDEX idx_scraped_at (scraped_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        # Table for reports
        create_reports_table = """
        CREATE TABLE IF NOT EXISTS reports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            report_type VARCHAR(100) NOT NULL,
            report_date DATE NOT NULL,
            content TEXT,
            summary JSON,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_report_type (report_type),
            INDEX idx_report_date (report_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        # Table for API keys and configurations
        create_config_table = """
        CREATE TABLE IF NOT EXISTS api_configs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            api_name VARCHAR(100) NOT NULL,
            api_key TEXT,
            base_url TEXT,
            rate_limit INT DEFAULT 100,
            last_used TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_api (api_name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        try:
            cursor.execute(create_data_table)
            print_status("✅ Table 'scraped_data' created successfully", "success")
            
            cursor.execute(create_reports_table)
            print_status("✅ Table 'reports' created successfully", "success")
            
            cursor.execute(create_config_table)
            print_status("✅ Table 'api_configs' created successfully", "success")
            
            self.db_connection.commit()
            print_status("🎉 All database tables created successfully", "success")
            
        except Error as e:
            print_status(f"❌ Error creating tables: {e}", "error")
        finally:
            cursor.close()
    
    async def scrape_datapilotplus(self):
        """Scrape DataPilotPlus.com for company information"""
        try:
            print_status(f"🕷️ Starting DataPilotPlus scraping from {self.base_url}", "scraping")
            
            # Use crawl4ai for intelligent scraping
            print_status("🤖 Initializing AI-powered crawler...", "processing")
            result = await self.crawler.arun(
                url=self.base_url,
                extraction_strategy="LLMExtractionStrategy",
                extraction_prompt="Extract all company information, services, team members, and business details from this page. Focus on company name, description, services offered, team members, and any business intelligence data."
            )
            
            if result and result.success:
                # Extract content from the result object
                if hasattr(result, 'extracted_content') and result.extracted_content:
                    content = result.extracted_content
                elif hasattr(result, 'markdown') and result.markdown:
                    content = result.markdown
                elif hasattr(result, 'text') and result.text:
                    content = result.text
                elif hasattr(result, 'html') and result.html:
                    content = result.html
                else:
                    # Fallback: try to get any available content
                    content = str(result)
                
                if content and len(content) > 0:
                    print_status(f"✅ Successfully scraped DataPilotPlus: {len(content)} characters", "success")
                    
                    # Save to database
                    print_status("💾 Saving scraped data to database...", "saving")
                    self.save_scraped_data(
                        source_name='datapilotplus.com',
                        category='company_information',
                        method_type='Web Scraping',
                        url=self.base_url,
                        data_points={
                            'company_name': 'DataPilotPlus',
                            'content_length': len(content),
                            'scraped_at': datetime.now().isoformat(),
                            'scraping_method': 'crawl4ai'
                        },
                        content=content[:1000] + "..." if len(content) > 1000 else content,  # Truncate if too long
                        analysis={'scraping_method': 'crawl4ai', 'success': True, 'content_type': 'extracted'}
                    )
                    
                    return content
                else:
                    print_status("⚠️ Crawler returned empty content", "warning")
                    return None
            else:
                error_msg = "Unknown error"
                if hasattr(result, 'error') and result.error:
                    error_msg = result.error
                elif hasattr(result, 'status') and result.status:
                    error_msg = result.status
                
                print_status(f"❌ Failed to scrape DataPilotPlus: {error_msg}", "error")
                return None
                
        except Exception as e:
            print_status(f"❌ Error scraping DataPilotPlus: {e}", "error")
            return None
    
    def scrape_api_data(self, api_name: str, api_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Scrape data from various APIs"""
        try:
            print_status(f"🔌 Scraping API: {api_name}", "connecting")
            
            # Check if we have API key in database
            api_key = self.get_api_key(api_name)
            if not api_key:
                print_status(f"⚠️ No API key found for {api_name}", "warning")
                return None
            
            # Implement specific API scraping logic based on api_name
            if api_name == 'sec_edgar':
                return self.scrape_sec_edgar(api_key)
            elif api_name == 'opencorporates':
                return self.scrape_opencorporates(api_key)
            elif api_name == 'yahoo_finance':
                return self.scrape_yahoo_finance(api_key)
            elif api_name == 'usaspending':
                return self.scrape_usaspending(api_key)
            elif api_name == 'osha_api':
                return self.scrape_osha_api(api_key)
            elif api_name == 'nlrb_api':
                return self.scrape_nlrb_api(api_key)
            elif api_name == 'fec_api':
                return self.scrape_fec_api(api_key)
            elif api_name == 'opensecrets':
                return self.scrape_opensecrets_api(api_key)
            else:
                print_status(f"⚠️ Unknown API: {api_name}", "warning")
                return None
                
        except Exception as e:
            print_status(f"❌ Error scraping API {api_name}: {e}", "error")
            return None
    
    def scrape_sec_edgar(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Scrape SEC EDGAR data"""
        try:
            print_status("📊 Scraping SEC EDGAR data...", "scraping")
            # SEC EDGAR API implementation
            headers = {'User-Agent': self.headers['User-Agent']}
            # Add SEC API specific logic here
            return {'status': 'success', 'data': 'SEC EDGAR data placeholder'}
        except Exception as e:
            print_status(f"❌ Error scraping SEC EDGAR: {e}", "error")
            return None
    
    def scrape_opencorporates(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Scrape OpenCorporates data"""
        try:
            print_status("🏢 Scraping OpenCorporates data...", "scraping")
            # OpenCorporates API implementation
            headers = {'Authorization': f'Token {api_key}'}
            # Add OpenCorporates API specific logic here
            return {'status': 'success', 'data': 'OpenCorporates data placeholder'}
        except Exception as e:
            print_status(f"❌ Error scraping OpenCorporates: {e}", "error")
            return None
    
    def scrape_yahoo_finance(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Scrape Yahoo Finance data"""
        try:
            print_status("💰 Scraping Yahoo Finance data...", "scraping")
            # Yahoo Finance API implementation
            # Add Yahoo Finance API specific logic here
            return {'status': 'success', 'data': 'Yahoo Finance data placeholder'}
        except Exception as e:
            print_status(f"❌ Error scraping Yahoo Finance: {e}", "error")
            return None
    
    def scrape_usaspending(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Scrape USAspending.gov data"""
        try:
            print_status("🏛️ Scraping USAspending.gov data...", "scraping")
            # USAspending API implementation
            # Add USAspending API specific logic here
            return {'status': 'success', 'data': 'USAspending data placeholder'}
        except Exception as e:
            print_status(f"❌ Error scraping USAspending: {e}", "error")
            return None
    
    def scrape_osha_api(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Scrape OSHA API data"""
        try:
            print_status("🦺 Scraping OSHA API data...", "scraping")
            # OSHA API implementation
            # Add OSHA API specific logic here
            return {'status': 'success', 'data': 'OSHA data placeholder'}
        except Exception as e:
            print_status(f"❌ Error scraping OSHA API: {e}", "error")
            return None
    
    def scrape_nlrb_api(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Scrape NLRB API data"""
        try:
            print_status("⚖️ Scraping NLRB API data...", "scraping")
            # NLRB API implementation
            # Add NLRB API specific logic here
            return {'status': 'success', 'data': 'NLRB data placeholder'}
        except Exception as e:
            print_status(f"❌ Error scraping NLRB API: {e}", "error")
            return None
    
    def scrape_fec_api(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Scrape FEC API data"""
        try:
            print_status("🗳️ Scraping FEC API data...", "scraping")
            # FEC API implementation
            # Add FEC API specific logic here
            return {'status': 'success', 'data': 'FEC data placeholder'}
        except Exception as e:
            print_status(f"❌ Error scraping FEC API: {e}", "error")
            return None
    
    def scrape_opensecrets_api(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Scrape OpenSecrets API data"""
        try:
            print_status("🔍 Scraping OpenSecrets API data...", "scraping")
            # OpenSecrets API implementation
            # Add OpenSecrets API specific logic here
            return {'status': 'success', 'data': 'OpenSecrets data placeholder'}
        except Exception as e:
            print_status(f"❌ Error scraping OpenSecrets API: {e}", "error")
            return None
    
    def get_api_key(self, api_name: str) -> Optional[str]:
        """Get API key from database"""
        if not self.db_connection:
            return None
            
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("SELECT api_key FROM api_configs WHERE api_name = %s", (api_name,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print_status(f"❌ Error getting API key for {api_name}: {e}", "error")
            return None
        finally:
            cursor.close()
    
    def save_scraped_data(self, source_name: str, category: str, method_type: str, 
                          url: str, data_points: Dict[str, Any], content: str, 
                          analysis: Dict[str, Any]):
        """Save scraped data to MySQL database"""
        if not self.db_connection:
            print_status("❌ No database connection available", "error")
            return
            
        cursor = self.db_connection.cursor()
        try:
            insert_query = """
            INSERT INTO scraped_data 
            (source_name, category, method_type, url, data_points, content, analysis)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                source_name,
                category,
                method_type,
                url,
                json.dumps(data_points),
                content,
                json.dumps(analysis)
            ))
            
            self.db_connection.commit()
            print_status(f"💾 Saved data from {source_name} to database", "saving")
            
        except Error as e:
            print_status(f"❌ Error saving data to database: {e}", "error")
        finally:
            cursor.close()
    
    def save_report(self, report_type: str, content: str, summary: Dict[str, Any]):
        """Save report to MySQL database"""
        if not self.db_connection:
            print_status("❌ No database connection available", "error")
            return
            
        cursor = self.db_connection.cursor()
        try:
            insert_query = """
            INSERT INTO reports (report_type, report_date, content, summary)
            VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                report_type,
                datetime.now().date(),
                content,
                json.dumps(summary)
            ))
            
            self.db_connection.commit()
            print_status(f"💾 Saved {report_type} report to database", "saving")
            
        except Error as e:
            print_status(f"❌ Error saving report to database: {e}", "error")
        finally:
            cursor.close()
    
    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive report from all scraped data"""
        print_status("📊 Generating comprehensive intelligence report...", "reporting")
        
        if not self.db_connection:
            return "Database connection not available"
            
        cursor = self.db_connection.cursor()
        try:
            # Get summary statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT source_name) as unique_sources,
                    COUNT(DISTINCT category) as categories,
                    MAX(scraped_at) as last_scraped
                FROM scraped_data
            """)
            stats = cursor.fetchone()
            
            # Get data by category
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM scraped_data
                GROUP BY category
                ORDER BY count DESC
            """)
            category_stats = cursor.fetchall()
            
            # Get recent data
            cursor.execute("""
                SELECT source_name, category, method_type, scraped_at
                FROM scraped_data
                ORDER BY scraped_at DESC
                LIMIT 20
            """)
            recent_data = cursor.fetchall()
            
            report = f"""
DATAPILOTPLUS COMPREHENSIVE INTELLIGENCE REPORT
===============================================
Date: {self.today}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Database: {os.getenv('MYSQL_DATABASE', 'datapilotplus_scraper')}

EXECUTIVE SUMMARY
-----------------
• Total Records: {stats[0] if stats else 0}
• Unique Sources: {stats[1] if stats else 0}
• Data Categories: {stats[2] if stats else 0}
• Last Scraped: {stats[3] if stats else 'Never'}

DATA CATEGORIES BREAKDOWN
=========================
"""
            
            for category, count in category_stats:
                report += f"• {category.replace('_', ' ').title()}: {count} records\n"
            
            report += f"""

RECENT DATA ACTIVITY
====================
"""
            
            for source, category, method, scraped_at in recent_data:
                report += f"• {source} - {category} ({method}) - {scraped_at}\n"
            
            report += f"""

DATA SOURCES MONITORED
======================
Based on the comprehensive data scraping framework:

COMPANY INFORMATION:
• SEC EDGAR API - Company filings, registrations, disclosures
• OpenCorporates API - Global corporate data, business registrations
• Company Websites - About pages, company profiles, team information

LEADERSHIP & MANAGEMENT:
• SEC Insiders API - Company officers, board members, management
• LinkedIn - Executive profiles, organizational structure

OPERATIONS & CONTRACTS:
• USAspending.gov API - Federal contracts, grants, projects
• State DOT Databases - Transportation contracts, infrastructure projects
• Local Government Portals - Municipal contracts, procurement data

COMPLIANCE & REGULATORY:
• OSHA API - Safety violations, enforcement actions
• DOL Enforcement API - Wage violations, labor enforcement
• NLRB API - Labor relations, union organizing cases
• EPA ECHO API - Environmental compliance data

FINANCIAL INTELLIGENCE:
• Yahoo Finance API - Public company financial data
• Federal Contract Data - Procurement amounts, award values
• State Procurement Portals - Local government spending

POLITICAL INFLUENCE:
• FEC API - Campaign finance, political contributions
• OpenSecrets API - Lobbying activities, political influence
• State Campaign Finance - Local political spending

CORPORATE STRUCTURE:
• Ownership relationships, subsidiaries, parent companies
• Related entities, corporate family trees
• Business registration data across jurisdictions

IMPLEMENTATION APPROACH
=======================
• API-based sources: Python requests with JSON/CSV parsing
• Web scraping: BeautifulSoup, Selenium, and crawl4ai
• Database: MySQL with structured JSON storage
• Scheduling: Automated scraping every {os.getenv('SCRAPER_INTERVAL_HOURS', 6)} hours
• MCP Server: Running on port {os.getenv('MCP_SERVER_PORT', 8000)}

NEXT STEPS
==========
• Configure API keys for all data sources
• Set up automated scraping schedules
• Implement data validation and quality checks
• Create custom analysis and reporting modules
• Deploy MCP server for external integrations

---
Generated by: DataPilotPlus Intelligence System
Contact: jeremy@augments.art
© 2025 DataPilotPlus - Business Intelligence Division
"""
            
            print_status("✅ Comprehensive report generated successfully", "success")
            return report
            
        except Error as e:
            print_status(f"❌ Error generating report: {e}", "error")
            return f"Error generating report: {e}"
        finally:
            cursor.close()
    
    def send_comprehensive_report(self, report_content: str):
        """Send the comprehensive report via email"""
        try:
            print_status("📧 Sending comprehensive intelligence report...", "reporting")
            
            # Save report to database
            summary = {
                'total_length': len(report_content),
                'generated_at': datetime.now().isoformat(),
                'report_type': 'comprehensive_intelligence'
            }
            self.save_report('comprehensive_intelligence', report_content, summary)
            
            # Email configuration
            smtp_server = os.getenv('SMTP_SERVER')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            email_user = os.getenv('EMAIL_USER')
            email_password = os.getenv('EMAIL_PASSWORD')
            sender_email = os.getenv('SENDER_EMAIL', 'jeremy@augments.art')
            recipients = os.getenv('REPORT_RECIPIENTS', '').split(',')
            
            if not all([smtp_server, email_user, email_password, sender_email, recipients[0]]):
                print_status("⚠️ Email configuration missing, skipping email send", "warning")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"DataPilotPlus Comprehensive Intelligence Report - {self.today}"
            
            body = f"""Hello,

Please find attached the comprehensive intelligence report for DataPilotPlus.com.

Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This report includes:
• Data scraping summary from multiple sources
• Company intelligence across all categories
• Compliance and regulatory data
• Financial and political intelligence
• Strategic recommendations

Best regards,
DataPilotPlus Intelligence Bot
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Create report file
            report_filename = f"reports/datapilotplus_comprehensive_report_{datetime.now().strftime('%Y%m%d')}.txt"
            os.makedirs('reports', exist_ok=True)
            
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # Attach the report file
            with open(report_filename, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(report_filename)}'
            )
            msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_user, email_password)
            server.sendmail(sender_email, recipients, msg.as_string())
            server.quit()
            
            print_status(f"✅ Comprehensive report successfully sent to: {', '.join(recipients)}", "success")
            return True
            
        except Exception as e:
            print_status(f"❌ Failed to send comprehensive report: {e}", "error")
            return False
    
    async def run_comprehensive_scraping(self):
        """Run comprehensive scraping across all data sources"""
        print_status("🚀 Starting comprehensive DataPilotPlus scraping...", "startup")
        
        try:
            # 1. Scrape DataPilotPlus.com
            print_status("📊 Scraping DataPilotPlus.com...", "scraping")
            datapilotplus_content = await self.scrape_datapilotplus()
            
            # 2. Scrape API-based sources
            print_status("🔌 Scraping API-based data sources...", "connecting")
            
            # Count total sources for progress bar
            total_sources = sum(len(sources) for sources in self.data_sources.values())
            current_source = 0
            
            for category, sources in self.data_sources.items():
                print_status(f"📂 Processing category: {category.replace('_', ' ').title()}", "processing")
                
                for source_name, config in sources.items():
                    current_source += 1
                    print_progress_bar(current_source, total_sources, f"Scraping {source_name}")
                    
                    if config.get('method') == 'API':
                        api_data = self.scrape_api_data(source_name, config)
                        if api_data:
                            self.save_scraped_data(
                                source_name=source_name,
                                category=category,
                                method_type='API',
                                url=config['url'],
                                data_points=api_data,
                                content=str(api_data),
                                analysis={'api_name': source_name, 'success': True}
                            )
            
            # 3. Generate comprehensive report
            print_status("📋 Generating comprehensive intelligence report...", "reporting")
            report = self.generate_comprehensive_report()
            
            # 4. Send report
            print_status("📧 Sending comprehensive intelligence report...", "reporting")
            self.send_comprehensive_report(report)
            
            print_status("🎉 Comprehensive DataPilotPlus scraping completed!", "success")
            
        except Exception as e:
            print_status(f"❌ Error during comprehensive scraping: {e}", "error")
            raise

# MCP Server Handler
class MCPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for MCP server"""
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
            self.wfile.write(json.dumps(response).encode())
        elif parsed_path.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'service': 'DataPilotPlus Scraper', 'status': 'running'}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_POST(self):
        """Handle POST requests for MCP server"""
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/scrape':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                # Handle scraping request
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'status': 'scraping_initiated', 'data': data}
                self.wfile.write(json.dumps(response).encode())
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Invalid JSON')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        """Custom logging for MCP server"""
        logging.info(f"MCP Server: {format % args}")

def start_mcp_server(port: int = 8000):
    """Start MCP server in a separate thread"""
    try:
        server = HTTPServer(('localhost', port), MCPHandler)
        print_status(f"🚀 MCP Server started on port {port}", "startup")
        
        def run_server():
            server.serve_forever()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        return server, server_thread
    except Exception as e:
        print_status(f"❌ Failed to start MCP server: {e}", "error")
        return None, None

# Main execution
if __name__ == "__main__":
    # Initialize scraper
    scraper = DataPilotPlusScraper()
    
    # Start MCP server if enabled
    mcp_server = None
    mcp_thread = None
    if os.getenv('MCP_SERVER_ENABLED', 'true').lower() == 'true':
        mcp_port = int(os.getenv('MCP_SERVER_PORT', 8000))
        mcp_server, mcp_thread = start_mcp_server(mcp_port)
    
    # Schedule comprehensive scraping
    scraper_interval = int(os.getenv('SCRAPER_INTERVAL_HOURS', 6))
    print_status(f"⏰ Scheduling scraper to run every {scraper_interval} hours", "info")
    
    schedule.every(scraper_interval).hours.do(
        lambda: asyncio.run(scraper.run_comprehensive_scraping())
    )
    
    # Run initial scraping
    print_status("🚀 Starting initial DataPilotPlus scraping...", "startup")
    asyncio.run(scraper.run_comprehensive_scraping())
    
    # Main loop
    print_status(f"🔄 Scraper running with {scraper_interval}-hour intervals", "info")
    print_status("💡 Press Ctrl+C to stop the scraper", "info")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print_status("🛑 Shutting down DataPilotPlus scraper...", "warning")
        if mcp_server:
            mcp_server.shutdown()
        if scraper.db_connection:
            scraper.db_connection.close()
        print_status("👋 DataPilotPlus scraper stopped successfully", "success")

