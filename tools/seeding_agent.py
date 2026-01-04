import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from googlesearch import search
import time
import re

class SeedingAgent:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Strict list for finding the OFFICIAL website
        self.ignored_domains_official = [
            'shiksha.com', 'careers360.com', 'wikipedia.org', 'collegedunia.com', 
            'getmyuni.com', 'collegedekho.com', 'justdial.com', 'facebook.com', 
            'linkedin.com', 'instagram.com', 'youtube.com', 'twitter.com',
            'quora.com', 'pinterest.com'
        ]
        # Looser list for fallback content (allow Wikipedia, aggregators if needed)
        self.ignored_domains_fallback = [
            'facebook.com', 'linkedin.com', 'instagram.com', 'youtube.com', 
            'twitter.com', 'quora.com', 'pinterest.com', 'justdial.com'
        ]

    def is_official_domain(self, url):
        domain = urlparse(url).netloc.lower()
        for ignored in self.ignored_domains_official:
            if ignored in domain:
                return False
        return True

    def is_valid_fallback(self, url):
        domain = urlparse(url).netloc.lower()
        for ignored in self.ignored_domains_fallback:
            if ignored in domain:
                return False
        return True

    def find_official_website(self, college_name, location):
        # Clean college name
        clean_name = college_name.split('-')[0].strip()
        query = f"{clean_name} {location} official website"
        print(f"Searching for: {query}")
        
        try:
            for url in search(query, num_results=10):
                if self.is_official_domain(url):
                    print(f"Found official URL: {url}")
                    return url
        except Exception as e:
            print(f"Error searching for website: {e}")
        return None

    def find_sub_page(self, base_url, keywords):
        if not base_url:
            return None
            
        domain = urlparse(base_url).netloc
        query = f"site:{domain} {' '.join(keywords)}"
        
        try:
            for url in search(query, num_results=1):
                return url
        except Exception as e:
            print(f"Error searching deep link for {keywords}: {e}")
        return None

    def find_fallback_page(self, college_name, keywords):
        query = f"{college_name} {' '.join(keywords)}"
        print(f"  Fallback search for: {query}")
        try:
            for url in search(query, num_results=3):
                if self.is_valid_fallback(url):
                    print(f"  Found fallback URL: {url}")
                    return url
        except Exception as e:
            print(f"Error searching fallback for {keywords}: {e}")
        return None

    def extract_courses(self, url):
        if not url:
            return []
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text().lower()
            
            # Simple heuristic to find engineering branches
            # In a real scenario, this would need more robust parsing or LLM
            common_branches = [
                "Computer Science", "Information Science", "Electronics", 
                "Mechanical", "Civil", "Electrical", "Artificial Intelligence",
                "Data Science", "Cyber Security", "Biotechnology", "Aerospace"
            ]
            
            found_courses = []
            for branch in common_branches:
                if branch.lower() in text:
                    found_courses.append(branch + " Engineering") # Append Engineering for consistency
            
            return list(set(found_courses))
            
        except Exception as e:
            print(f"Error extracting courses: {e}")
            return []

    def process_college(self, college_code, college_name, location, known_links=None, forced_official_url=None):
        print(f"Processing {college_code}: {college_name}...")
        
        official_website = forced_official_url
        
        if not official_website and known_links and 'placement' in known_links:
             # Try to infer official website from placement link if available
             parsed = urlparse(known_links['placement'])
             official_website = f"{parsed.scheme}://{parsed.netloc}"
        
        if not official_website:
            official_website = self.find_official_website(college_name, location)
        
        # Helper to find link with fallback
        def get_link(key, keywords):
            # 1. Use known link if available
            if known_links and key in known_links and known_links[key]:
                print(f"  Using known {key} link: {known_links[key]}")
                return known_links[key]

            # 2. Search sub-page
            link = None
            if official_website:
                link = self.find_sub_page(official_website, keywords)
            
            # 3. Fallback search
            if not link:
                print(f"  Official {key} link not found. Trying fallback...")
                link = self.find_fallback_page(college_name, keywords)
            
            return link

        links = {
            "placement": get_link("placement", ["placements"]),
            "hostel": get_link("hostel", ["hostel"]),
            "infrastructure": get_link("infrastructure", ["infrastructure", "campus"]),
            "academics": get_link("academics", ["academics", "departments"]),
            "admissions": get_link("admissions", ["admission"]),
            "contact": get_link("contact", ["contact", "reach us"])
        }

        # Try to find courses page to extract courses
        courses_url = links["academics"] if links["academics"] else official_website
        courses = self.extract_courses(courses_url)

        return {
            "college_code": college_code,
            "official_website": official_website,
            "links": links,
            "courses_offered": courses
        }

if __name__ == "__main__":
    agent = SeedingAgent()
    # Test with one college
    data = agent.process_college("E001", "Acharya Institute of Technology", "Bangalore")
    import json
    print(json.dumps(data, indent=2))
