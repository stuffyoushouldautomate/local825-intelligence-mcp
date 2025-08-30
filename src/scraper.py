import requests
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from datetime import datetime, timedelta
import json
import re

class HenjiiScraper:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.get('user_agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.delay = config.get('request_delay', 1)
        self.max_retries = config.get('max_retries', 3)
    
    def get_page_with_selenium(self, url):
        """Use Selenium for JavaScript-heavy pages"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
            driver.get(url)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Scroll to load dynamic content
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            page_source = driver.page_source
            driver.quit()
            return BeautifulSoup(page_source, 'html.parser')
            
        except Exception as e:
            print(f"Selenium scraping failed for {url}: {e}")
            return None
    
    def get_page_requests(self, url):
        """Standard requests-based scraping"""
        for attempt in range(self.max_retries):
            try:
                time.sleep(self.delay + random.uniform(0, 1))
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == self.max_retries - 1:
                    return None
                time.sleep(2 ** attempt)
    
    def extract_posts(self, soup):
        """Extract posts from the main page"""
        posts = []
        
        # Multiple selectors to try (adapt based on actual site structure)
        selectors = [
            'article', '.post', '.article', '.content-item', 
            '.blog-post', '.entry', '[class*="post"]', '[class*="article"]'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} posts using selector: {selector}")
                break
        
        for element in elements:
            post_data = self.extract_post_data(element)
            if post_data:
                posts.append(post_data)
        
        return posts
    
    def extract_post_data(self, element):
        """Extract data from a single post element"""
        try:
            # Try to extract title
            title = self.extract_text([
                'h1', 'h2', 'h3', '.title', '.post-title', 
                '.entry-title', '[class*="title"]'
            ], element)
            
            # Try to extract content/summary
            content = self.extract_text([
                '.content', '.post-content', '.entry-content', 
                '.summary', '.excerpt', 'p'
            ], element)
            
            # Try to extract date
            date = self.extract_text([
                '.date', '.post-date', '.published', 'time', 
                '[class*="date"]', '[datetime]'
            ], element)
            
            # Try to extract author
            author = self.extract_text([
                '.author', '.post-author', '.by-author', 
                '[class*="author"]'
            ], element)
            
            # Try to extract tags/categories
            tags = self.extract_tags(element)
            
            # Try to extract URL
            url = self.extract_url(element)
            
            return {
                'title': title,
                'content': content,
                'date': date,
                'author': author,
                'tags': tags,
                'url': url,
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error extracting post data: {e}")
            return None
    
    def extract_text(self, selectors, element):
        """Extract text using multiple selectors"""
        for selector in selectors:
            found = element.select_one(selector)
            if found:
                text = found.get_text(strip=True)
                if text:
                    return text
        return ""
    
    def extract_tags(self, element):
        """Extract tags or categories"""
        tags = []
        tag_selectors = [
            '.tag', '.tags a', '.category', '.categories a',
            '[class*="tag"]', '[class*="category"]'
        ]
        
        for selector in tag_selectors:
            elements = element.select(selector)
            for tag_elem in elements:
                tag_text = tag_elem.get_text(strip=True)
                if tag_text and tag_text not in tags:
                    tags.append(tag_text)
        
        return tags
    
    def extract_url(self, element):
        """Extract post URL"""
        # Try to find a link within the post
        link_selectors = ['a[href]', '.title a', '.post-title a', 'h1 a', 'h2 a', 'h3 a']
        
        for selector in link_selectors:
            link = element.select_one(selector)
            if link and link.get('href'):
                href = link.get('href')
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    return f"https://datapilotplus.com{href}"
                elif href.startswith('http'):
                    return href
        return ""
    
    def extract_jobs(self, soup):
        """Extract job postings specifically"""
        jobs = []
        
        # Look for job-specific selectors
        job_selectors = [
            '.job', '.job-listing', '.career', '.position',
            '[class*="job"]', '[class*="career"]', '[class*="position"]'
        ]
        
        for selector in job_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} jobs using selector: {selector}")
                for element in elements:
                    job_data = self.extract_job_data(element)
                    if job_data:
                        jobs.append(job_data)
                break
        
        return jobs
    
    def extract_job_data(self, element):
        """Extract job-specific data"""
        try:
            title = self.extract_text([
                'h1', 'h2', 'h3', '.title', '.job-title', 
                '.position-title', '[class*="title"]'
            ], element)
            
            company = self.extract_text([
                '.company', '.employer', '.organization',
                '[class*="company"]', '[class*="employer"]'
            ], element)
            
            location = self.extract_text([
                '.location', '.place', '.city', '.address',
                '[class*="location"]', '[class*="place"]'
            ], element)
            
            salary = self.extract_text([
                '.salary', '.pay', '.compensation', '.wage',
                '[class*="salary"]', '[class*="pay"]'
            ], element)
            
            description = self.extract_text([
                '.description', '.job-description', '.details',
                '[class*="description"]'
            ], element)
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'salary': salary,
                'description': description,
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error extracting job data: {e}")
            return None
    
    def scrape_full_site(self):
        """Main scraping method"""
        print("Starting full site scrape...")
        
        # Try requests first, fallback to Selenium
        soup = self.get_page_requests("https://datapilotplus.com")
        if not soup:
            print("Requests failed, trying Selenium...")
            soup = self.get_page_with_selenium("https://datapilotplus.com")
        
        if not soup:
            print("Failed to retrieve the main page")
            return None
        
        # Extract different types of content
        posts = self.extract_posts(soup)
        jobs = self.extract_jobs(soup)
        
        # Look for pagination and scrape additional pages
        additional_pages = self.find_pagination_links(soup)
        
        for page_url in additional_pages[:5]:  # Limit to 5 additional pages
            print(f"Scraping additional page: {page_url}")
            page_soup = self.get_page_requests(page_url)
            if page_soup:
                posts.extend(self.extract_posts(page_soup))
                jobs.extend(self.extract_jobs(page_soup))
        
        return {
            'posts': posts,
            'jobs': jobs,
            'scraped_at': datetime.now().isoformat(),
            'total_posts': len(posts),
            'total_jobs': len(jobs)
        }
    
    def find_pagination_links(self, soup):
        """Find pagination links"""
        pagination_links = []
        
        # Common pagination selectors
        pagination_selectors = [
            '.pagination a', '.page-numbers a', '.next', 
            '[class*="pagination"] a', '[class*="page"] a'
        ]
        
        for selector in pagination_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href and href not in pagination_links:
                    if href.startswith('/'):
                        pagination_links.append(f"https://datapilotplus.com{href}")
                    elif href.startswith('http'):
                        pagination_links.append(href)
        
        return pagination_links[:5]  # Limit to prevent excessive scraping
