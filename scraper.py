import asyncio
import re
import time
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from fake_useragent import UserAgent

from config import Config
from database import DatabaseManager

class ScholarshipScraper:
    def __init__(self):
        self.db = DatabaseManager()
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': Config.DEFAULT_USER_AGENT})

    def check_robots_txt(self, url):
        """Check if scraping is allowed by robots.txt"""
        if not Config.RESPECT_ROBOTS_TXT:
            return True

        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()

            return rp.can_fetch(Config.DEFAULT_USER_AGENT, url)
        except Exception as e:
            print(f"Error checking robots.txt for {url}: {e}")
            return True  # Allow if we can't check

    def parse_deadline(self, deadline_text):
        """Parse various deadline formats into datetime objects"""
        if not deadline_text:
            return None

        deadline_text = deadline_text.lower().strip()

        # Common patterns
        patterns = [
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', '%m/%d/%Y'),
            (r'(\d{1,2})-(\d{1,2})-(\d{4})', '%m-%d-%Y'),
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
            (r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})', '%d %B %Y'),
            (r'(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{4})', '%d %b %Y'),
        ]

        for pattern, date_format in patterns:
            match = re.search(pattern, deadline_text)
            if match:
                try:
                    return datetime.strptime(match.group(0), date_format)
                except ValueError:
                    continue

        # Handle relative dates
        if 'rolling' in deadline_text or 'open' in deadline_text:
            return datetime.now() + timedelta(days=365)  # Far future for rolling deadlines

        return None

    def parse_funding_type(self, text):
        """Categorize funding types"""
        text = text.lower()
        if any(word in text for word in ['fully funded', 'full funding', '100%', 'complete']):
            return 'fully_funded'
        elif any(word in text for word in ['partial', '50%', 'half', 'tuition']):
            return 'partial'
        elif any(word in text for word in ['stipend', 'living allowance', 'monthly']):
            return 'stipend'
        return 'other'

    def parse_degree_level(self, text):
        """Extract degree level from text"""
        text = text.lower()
        if any(word in text for word in ['undergraduate', 'bachelor', 'bachelors', 'b.sc', 'b.a']):
            return 'undergraduate'
        elif any(word in text for word in ['masters', 'master', 'm.sc', 'm.a', 'postgraduate']):
            return 'masters'
        elif any(word in text for word in ['phd', 'doctoral', 'doctorate']):
            return 'phd'
        elif any(word in text for word in ['postdoc', 'post-doctoral']):
            return 'postdoc'
        return 'any'

    def parse_gpa(self, text):
        """Extract GPA requirement from text"""
        gpa_patterns = [
            r'gpa\s*[:\-]?\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*gpa',
            r'grade\s*point\s*average\s*[:\-]?\s*(\d+\.?\d*)'
        ]

        for pattern in gpa_patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    gpa = float(match.group(1))
                    return min(gpa, 4.0)  # Cap at 4.0
                except ValueError:
                    continue
        return None

    async def scrape_with_playwright(self, url):
        """Scrape dynamic content with Playwright"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=Config.PLAYWRIGHT_HEADLESS)
            context = await browser.new_context(
                user_agent=self.ua.random,
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()

            try:
                await page.goto(url, timeout=Config.PLAYWRIGHT_TIMEOUT)
                await page.wait_for_load_state('networkidle')

                # Extract scholarship data
                content = await page.content()
                return self.extract_scholarship_data(content, url)

            except PlaywrightTimeoutError:
                print(f"Timeout scraping {url}")
                return []
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                return []
            finally:
                await browser.close()

    def scrape_with_requests(self, url):
        """Scrape static content with requests"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return self.extract_scholarship_data(response.text, url)
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return []

    def extract_scholarship_data(self, html_content, source_url):
        """Extract scholarship information from HTML"""
        soup = BeautifulSoup(html_content, 'lxml')
        scholarships = []

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Find scholarship containers (adaptable patterns)
        scholarship_containers = []

        # Pattern 1: Common scholarship page structure
        containers = soup.find_all(['div', 'article', 'section'], class_=re.compile(r'scholarship|opportunity|grant|award'))
        if containers:
            scholarship_containers.extend(containers)

        # Pattern 2: List items
        if not scholarship_containers:
            list_items = soup.find_all('li', class_=re.compile(r'scholarship|opportunity|grant|award'))
            scholarship_containers.extend(list_items)

        # Pattern 3: Table rows
        if not scholarship_containers:
            table_rows = soup.find_all('tr')
            scholarship_containers.extend(table_rows)

        # Pattern 4: Generic containers with scholarship keywords
        if not scholarship_containers:
            all_divs = soup.find_all('div')
            for div in all_divs:
                text = div.get_text().lower()
                if any(keyword in text for keyword in Config.SCHOLARSHIP_KEYWORDS):
                    scholarship_containers.append(div)
                    break

        # Extract data from each container
        for container in scholarship_containers[:10]:  # Limit to first 10
            scholarship = self.parse_scholarship_container(container, source_url)
            if scholarship:
                scholarships.append(scholarship)

        return scholarships

    def parse_scholarship_container(self, container, source_url):
        """Parse individual scholarship container"""
        text = container.get_text()
        soup = BeautifulSoup(str(container), 'lxml')

        # Extract name
        name = None
        name_selectors = [
            'h1', 'h2', 'h3', 'h4',
            '[class*="title"]', '[class*="name"]', '[class*="heading"]'
        ]

        for selector in name_selectors:
            name_element = container.find(selector)
            if name_element:
                name = name_element.get_text().strip()
                if len(name) > 10:  # Reasonable minimum length
                    break

        if not name:
            # Fallback: first meaningful text
            lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 20]
            if lines:
                name = lines[0][:200]

        if not name or len(name) < 10:
            return None

        # Extract application link
        application_link = None
        link_selectors = [
            'a[href*="apply"]', 'a[href*="application"]', 'a[href*="register"]',
            'a[href*="scholarship"]', 'a[href*="opportunity"]'
        ]

        for selector in link_selectors:
            link_element = container.find(selector)
            if link_element:
                href = link_element.get('href')
                if href:
                    application_link = urljoin(source_url, href)
                    break

        # If no specific link found, use the source URL
        if not application_link:
            application_link = source_url

        # Parse other fields
        deadline = self.parse_deadline(text)
        funding_type = self.parse_funding_type(text)
        degree_level = self.parse_degree_level(text)
        gpa_requirement = self.parse_gpa(text)

        # Extract country (simple keyword matching)
        country = None
        countries = ['USA', 'UK', 'Canada', 'Australia', 'Germany', 'France', 'Netherlands', 'Switzerland', 'Sweden', 'Norway', 'Denmark', 'Finland']
        for c in countries:
            if c.lower() in text.lower():
                country = c
                break

        return {
            'name': name,
            'description': text[:1000],  # First 1000 characters
            'eligibility': text,
            'deadline': deadline,
            'funding_type': funding_type,
            'country': country,
            'university': None,  # Would need more sophisticated parsing
            'degree_level': degree_level,
            'gpa_requirement': gpa_requirement,
            'application_link': application_link,
            'source_url': source_url,
            'source_name': urlparse(source_url).netloc
        }

    async def scrape_url(self, url):
        """Scrape a single URL for scholarships"""
        if not self.check_robots_txt(url):
            print(f"Robots.txt disallows scraping {url}")
            return []

        # Try Playwright first for dynamic content
        try:
            scholarships = await self.scrape_with_playwright(url)
            if scholarships:
                return scholarships
        except Exception as e:
            print(f"Playwright failed for {url}: {e}")

        # Fallback to requests for static content
        return self.scrape_with_requests(url)

    async def scrape_multiple_urls(self, urls):
        """Scrape multiple URLs concurrently"""
        tasks = [self.scrape_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_scholarships = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Error scraping {urls[i]}: {result}")
            else:
                all_scholarships.extend(result)

        return all_scholarships

    def save_scholarships(self, scholarships):
        """Save scholarships to database"""
        saved_count = 0
        for scholarship in scholarships:
            try:
                scholarship_id = self.db.add_scholarship(scholarship)
                if scholarship_id:
                    saved_count += 1
            except Exception as e:
                print(f"Error saving scholarship {scholarship['name']}: {e}")

        return saved_count
