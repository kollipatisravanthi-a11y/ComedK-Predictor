import sys
import os
import json
import requests
from bs4 import BeautifulSoup
import time

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.college_details_data import college_links_data, college_courses_mapping, course_master

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'college_data_enriched.json')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_content(url):
    if not url:
        return None
    
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.extract()    

            # Get text
            text = soup.get_text()

            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit text length to avoid huge payloads (e.g., 2000 chars)
            # We want enough to be useful but not the whole page
            return text[:3000] + "..." if len(text) > 3000 else text
            
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    
    return None

def main():
    enriched_data = {}
    
    total_colleges = len(college_links_data)
    processed = 0

    for college_code, links in college_links_data.items():
        processed += 1
        print(f"Processing {college_code} ({processed}/{total_colleges})...")
        
        course_ids = college_courses_mapping.get(college_code, [])
        course_names = [course_master.get(cid, str(cid)) for cid in course_ids]

        enriched_data[college_code] = {
            'links': {},
            'courses': course_names
        }
        
        for category, url in links.items():
            content = fetch_content(url)
            enriched_data[college_code]['links'][category] = {
                'url': url,
                'content': content if content else "Content could not be fetched automatically. Please visit the link."
            }
            # Be nice to servers
            time.sleep(0.5)
        
        # Save incrementally
        print(f"Saving progress for {college_code}...")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(enriched_data, f, indent=4)
            
    print("Done.")

if __name__ == "__main__":
    main()
