
import sys
import os

# Add project root to path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.college_agent import college_agent
import time

new_colleges = [
    {"code": "E021", "name": "Bapuji Institute of Engineering & Technology- Shamanur Road, Davangere"},
    {"code": "E023", "name": "Basavakalyan Engineering College-NH9 Basavakalyan, Bidar"},
    {"code": "E024", "name": "Basaveshwar Engineering College-Vidyanagar, Bagalkot"},
    {"code": "E026", "name": "BLDEA's V.P. Dr. P.G. Halakatti College of Engineering & Technology,Ashram Road, Vijayapura"},
    {"code": "E027", "name": "BMS College of Engineering-Basavanagudi, Bengaluru"},
    {"code": "E028", "name": "BMS Institute of Technology & Management-Yelahanka, Bengaluru"},
    {"code": "E030", "name": "Brindavan College of Engineering-Yelahanka, Bengaluru"},
    {"code": "E032", "name": "C.M.R. Institute of Technology-Brookefield, Bengaluru"},
    {"code": "E033", "name": "Cambridge Institute of Technology, K R Puram, Bengaluru"},
    {"code": "E035", "name": "Channabasaveshwara Institute of Technology-Gubbi, Tumakuru"},
    {"code": "E036", "name": "Chanakya University-Devanahalli,Bengaluru Rural"},
    {"code": "E037", "name": "City Engineering College-Doddakalasandra, Bengaluru"},
    {"code": "E038", "name": "Coorg Institute of Technology-Ponnampet, South Kodagu"},
    {"code": "E039", "name": "Dayananda Sagar Academy of Technology & Management-Kanakapura Road, Bengaluru"},
    {"code": "E040", "name": "Dayananda Sagar College of Engineering-Kumaraswamy Layout, Bengaluru"}
]

# Course mapping for heuristic detection
course_keywords = {
    1: ['computer science', 'cse', 'computer'],
    2: ['information science', 'ise', 'information technology', 'it'],
    3: ['artificial intelligence', 'aiml', 'ai & ml', 'machine learning'],
    4: ['electronics', 'ece', 'communication'],
    5: ['electrical', 'eee'],
    6: ['mechanical', 'mech'],
    7: ['civil']
}

print("college_links_data_update = {")

for college in new_colleges:
    code = college['code']
    name = college['name']
    
    # Fetch data using the agent
    # We pass None for url so it searches by name
    try:
        data = college_agent.get_college_data(None, name)
    except Exception as e:
        data = {"error": str(e)}

    if "error" in data:
        print(f"    # Error fetching {code}: {data['error']}")
        continue

    print(f"    '{code}': {{")
    print(f"        'placement': '{data['placements']['url']}',")
    print(f"        'hostel': '{data['hostel']['url']}',")
    print(f"        'infrastructure': '{data['infrastructure']['url']}',")
    print(f"        'academics': '{data['academics']['url']}',")
    print(f"        'admissions': '{data['admissions']['url']}',")
    print(f"        'contact': '{data['contact']['url']}'")
    print(f"    }},")
    
    # Be nice to Google
    time.sleep(2)

print("}")
print("")
print("college_courses_mapping_update = {")

# For now, we'll assign a default set of courses (CS, ECE, Mech, Civil) + others if likely
# In a real scenario, we'd scrape the academics page text to find these keywords
for college in new_colleges:
    # Defaulting to most common branches for now as scraping courses reliably is hard without specific page logic
    # 1: CSE, 4: ECE, 6: Mech, 7: Civil are standard
    print(f"    '{college['code']}': [1, 2, 4, 5, 6, 7], # Assumed standard offering")

print("}")
