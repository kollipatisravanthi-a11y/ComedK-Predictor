import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
from googlesearch import search

class CollegeAgent:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.ignored_domains = [
            'shiksha.com', 'careers360.com', 'wikipedia.org', 'collegedunia.com', 
            'getmyuni.com', 'collegedekho.com', 'justdial.com', 'facebook.com', 
            'linkedin.com', 'instagram.com', 'youtube.com', 'twitter.com'
        ]

    def is_official_domain(self, url):
        domain = urlparse(url).netloc.lower()
        for ignored in self.ignored_domains:
            if ignored in domain:
                return False
        return True

    def find_official_website(self, college_name):
        # Clean college name: remove location details after hyphen
        clean_name = college_name.split('-')[0].strip()
        query = f"{clean_name} official website"
        print(f"Searching query: {query}")
        try:
            # Increase results to find a valid one
            for url in search(query, num_results=10):
                print(f"Found URL: {url}")
                if self.is_official_domain(url):
                    return url
        except Exception as e:
            print(f"Error searching for website: {e}")
        return None

    def search_deep_link(self, base_url, keywords):
        domain = urlparse(base_url).netloc
        query = f"site:{domain} {' '.join(keywords)}"
        try:
            for url in search(query, num_results=3):
                return url
        except Exception as e:
            print(f"Error searching deep link: {e}")
        return None

    def fetch_page(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None

    def find_link(self, soup, keywords, base_url):
        if not soup:
            return None
        
        # Try exact match first
        for a in soup.find_all('a', href=True):
            text = a.get_text().strip().lower()
            href = a['href']
            for keyword in keywords:
                if keyword == text:
                    return urljoin(base_url, href)
        
        # Then partial match
        for a in soup.find_all('a', href=True):
            text = a.get_text().strip().lower()
            href = a['href']
            for keyword in keywords:
                if keyword in text:
                    return urljoin(base_url, href)
        return None

    def extract_placements(self, soup, url):
        data = {
            "highest_package": "Information not available on official website",
            "average_package": "Information not available on official website",
            "top_recruiters": "Information not available on official website",
            "year": "Information not available on official website",
            "url": url
        }
        if not soup:
            return data

        text = soup.get_text()
        
        # Improved regex for packages
        # Look for patterns like "50 LPA", "50 Lakhs", "50.5 LPA"
        lpa_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:LPA|Lakhs?|Cr|Crores?)', text, re.IGNORECASE)
        
        if lpa_matches:
            # Convert to float to find max
            try:
                values = [float(x) for x in lpa_matches]
                if values:
                    max_val = max(values)
                    data["highest_package"] = f"{max_val} LPA"
                    
                    # Heuristic: Average is usually lower than max but not too low
                    # Filter out very small numbers (likely years or other stats)
                    valid_values = [v for v in values if 2 < v < max_val]
                    if valid_values:
                        # Take the average of remaining valid values or just a likely candidate
                        # This is a rough heuristic
                        avg_val = sum(valid_values) / len(valid_values)
                        data["average_package"] = f"{avg_val:.2f} LPA"
            except ValueError:
                pass

        # Fallback to specific keywords if general search failed
        if data["highest_package"] == "Information not available on official website":
            highest_match = re.search(r'Highest\s*(?:Package|Salary)?\s*[:\-]?\s*([\d\.]+\s*(?:LPA|Lakhs?|Cr|Crores?))', text, re.IGNORECASE)
            if highest_match:
                data["highest_package"] = highest_match.group(1)

        if data["average_package"] == "Information not available on official website":
            avg_match = re.search(r'Average\s*(?:Package|Salary)?\s*[:\-]?\s*([\d\.]+\s*(?:LPA|Lakhs?))', text, re.IGNORECASE)
            if avg_match:
                data["average_package"] = avg_match.group(1)

        # Year
        year_match = re.search(r'20\d{2}', text)
        if year_match:
            data["year"] = year_match.group(0)

        return data

    def extract_hostel(self, soup, url):
        data = {
            "availability": "Yes", # Assume yes if page exists
            "separate": "Information not available on official website",
            "facilities": "Information not available on official website",
            "url": url
        }
        if not soup:
            data["availability"] = "Information not available on official website"
            return data

        text = soup.get_text().lower()
        if "boys" in text and "girls" in text:
            data["separate"] = "Yes"
        else:
             data["separate"] = "No"
        
        facilities = []
        if "wifi" in text or "wi-fi" in text:
            facilities.append("Wi-Fi")
        if "mess" in text:
            facilities.append("Mess")
        if "gym" in text:
            facilities.append("Gym")
        if "laundry" in text:
            facilities.append("Laundry")
        if "security" in text:
            facilities.append("Security")
        
        if facilities:
            data["facilities"] = ", ".join(facilities)
            
        return data

    def get_college_data(self, college_url, college_name=None):
        if not college_url and college_name:
            print(f"Searching for official website for {college_name}...")
            college_url = self.find_official_website(college_name)
        
        if not college_url:
            return {"error": "Could not find official website"}

        print(f"Fetching data from: {college_url}")
        main_soup = self.fetch_page(college_url)
        data = {}

        # 1. Placements
        placement_url = self.find_link(main_soup, ['placement', 'career', 'recruit'], college_url)
        if not placement_url:
             placement_url = self.search_deep_link(college_url, ['placements'])
        
        if placement_url:
            placement_soup = self.fetch_page(placement_url)
            data['placements'] = self.extract_placements(placement_soup, placement_url)
        else:
            data['placements'] = {
                "highest_package": "Information not available on official website",
                "average_package": "Information not available on official website",
                "top_recruiters": "Information not available on official website",
                "year": "Information not available on official website",
                "url": "Information not available on official website"
            }

        # 2. Hostel
        hostel_url = self.find_link(main_soup, ['hostel', 'accommodation', 'residence'], college_url)
        if not hostel_url:
            hostel_url = self.search_deep_link(college_url, ['hostel', 'facilities'])

        if hostel_url:
            hostel_soup = self.fetch_page(hostel_url)
            data['hostel'] = self.extract_hostel(hostel_soup, hostel_url)
        else:
            data['hostel'] = {
                "availability": "Information not available on official website",
                "separate": "Information not available on official website",
                "facilities": "Information not available on official website",
                "url": "Information not available on official website"
            }

        # 3. Infrastructure
        infra_url = self.find_link(main_soup, ['infrastructure', 'campus', 'facility'], college_url)
        if not infra_url:
            infra_url = self.search_deep_link(college_url, ['infrastructure', 'campus'])

        data['infrastructure'] = {
            "campus_area": "Information not available on official website",
            "facilities": "Information not available on official website",
            "url": infra_url if infra_url else "Information not available on official website"
        }

        # 4. Academics
        acad_url = self.find_link(main_soup, ['academic', 'department', 'program'], college_url)
        if not acad_url:
            acad_url = self.search_deep_link(college_url, ['academics', 'departments'])

        data['academics'] = {
            "courses": "Information not available on official website",
            "accreditation": "Information not available on official website",
            "faculty": "Information not available on official website",
            "url": acad_url if acad_url else "Information not available on official website"
        }

        # 5. Admissions
        admin_url = self.find_link(main_soup, ['admission'], college_url)
        if not admin_url:
            admin_url = self.search_deep_link(college_url, ['admissions'])

        data['admissions'] = {
            "comedk_accepted": "Yes",
            "process": "Information not available on official website",
            "url": admin_url if admin_url else "Information not available on official website"
        }

        # 6. Contact
        contact_url = self.find_link(main_soup, ['contact', 'reach us'], college_url)
        if not contact_url:
            contact_url = self.search_deep_link(college_url, ['contact'])

        data['contact'] = {
            "address": "Information not available on official website",
            "phone": "Information not available on official website",
            "email": "Information not available on official website",
            "url": contact_url if contact_url else "Information not available on official website"
        }

        return data

college_agent = CollegeAgent()
