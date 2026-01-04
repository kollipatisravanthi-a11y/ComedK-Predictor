import sys
import os
import json
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.colleges_data import colleges_list, architecture_colleges
# from backend.college_details_data import get_college_explicit_data
from tools.seeding_agent import SeedingAgent

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'college_data_enriched.json')

def load_data():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def main():
    agent = SeedingAgent()
    data = load_data()
    
    # Combine lists
    all_colleges = colleges_list + architecture_colleges
    
    print(f"Found {len(all_colleges)} colleges to process.")
    
    # Process a few for demonstration (or all if desired, but it takes time)
    # For now, let's process the first 3 that are missing or incomplete
    count = 0
    max_process = 50
    
    for college in all_colleges:
        code = college['code']
        name = college['name']
        location = college['location']
        
        # Use official website from data if available, otherwise let agent find it
        forced_official_url = college.get('website')

        # Check if we already have data (and it's not just empty placeholders)
        if code in data and data[code].get('links', {}).get('placement'):
            print(f"Skipping {code} - already has data.")
            continue
            
        if count >= max_process:
            break
            
        print(f"Seeding data for {code}...")
        # Pass known_links=None to force dynamic discovery as requested
        result = agent.process_college(code, name, location, known_links=None, forced_official_url=forced_official_url)
        
        if result:
            # Map to existing structure
            # Preserve existing data if we are just updating links
            if code not in data:
                data[code] = {}
            
            data[code]["links"] = result['links']
            data[code]["courses"] = result['courses_offered']
            data[code]["website"] = result['official_website']
            
            save_data(data) # Save incrementally
            count += 1
            time.sleep(1) # Be polite to search engines
            
    print("Seeding complete.")

if __name__ == "__main__":
    main()
