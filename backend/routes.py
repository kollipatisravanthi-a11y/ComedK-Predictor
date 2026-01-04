from backend.app import app
from flask import render_template, request, jsonify
from backend.prediction import predict_colleges, get_college_courses
from backend.chatbot_ai import chatbot
from backend.college_agent import college_agent
from backend.colleges_data import colleges_list, architecture_colleges, medical_colleges, dental_colleges
from backend.branches_data import engineering_branches, architecture_branches
from backend.college_details_data import get_college_explicit_data
import json
import os

# Load enriched data if available
ENRICHED_DATA_FILE = os.path.join(os.path.dirname(__file__), 'college_data_enriched.json')
ENRICHED_DATA = {}

def load_enriched_data():
    global ENRICHED_DATA
    if os.path.exists(ENRICHED_DATA_FILE):
        try:
            with open(ENRICHED_DATA_FILE, 'r', encoding='utf-8') as f:
                ENRICHED_DATA = json.load(f)
            print(f"Loaded enriched data for {len(ENRICHED_DATA)} colleges.")
        except Exception as e:
            print(f"Error loading enriched data: {e}")

# Initial load
load_enriched_data()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    response = chatbot.get_response(user_message)
    return jsonify({'response': response})

@app.route('/api/college-data/<college_code>')
def get_college_data_api(college_code):
    # Reload data if empty or if college not found (to pick up new prefetch data)
    if not ENRICHED_DATA or college_code not in ENRICHED_DATA:
        load_enriched_data()

    # Check enriched data first (Part 3: Prefetched content)
    if college_code in ENRICHED_DATA:
        data = ENRICHED_DATA[college_code]
        return jsonify({
            "source": "explicit",
            "links": data['links'],
            "courses": data['courses']
        })

    # First check for explicit data (Part 1 & 2 of requirement)
    explicit_data = get_college_explicit_data(college_code)
    if explicit_data:
        return jsonify({
            "source": "explicit",
            "links": explicit_data['links'],
            "courses": explicit_data['courses']
        })

    # Fallback: Return basic info from static list without live fetching
    college = next((c for c in colleges_list if c['code'] == college_code), None)
    if not college:
        college = next((c for c in architecture_colleges if c['code'] == college_code), None)
    if not college:
        college = next((c for c in medical_colleges if c['code'] == college_code), None)
    if not college:
        college = next((c for c in dental_colleges if c['code'] == college_code), None)
    
    if not college:
        return jsonify({"error": "College not found"}), 404

    # Return basic structure if no enriched data available
    # The seeding agent should be run to populate this data
    return jsonify({
        "source": "explicit",
        "links": {
            "placement": None,
            "hostel": None,
            "infrastructure": None,
            "academics": None,
            "admissions": None,
            "contact": None
        },
        "courses": [],
        "website": college.get('website')
    })

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/exam-details')
def exam_details():
    return render_template('exam_details.html')

@app.route('/colleges')
def colleges():
    return render_template('colleges.html', engineering_colleges=colleges_list, architecture_colleges=architecture_colleges, medical_colleges=medical_colleges, dental_colleges=dental_colleges)

@app.route('/college/<college_code>')
def college_details(college_code):
    # Find college details from the static list
    college = next((c for c in colleges_list if c['code'] == college_code), None)
    if not college:
        college = next((c for c in architecture_colleges if c['code'] == college_code), None)
    if not college:
        college = next((c for c in medical_colleges if c['code'] == college_code), None)
    if not college:
        college = next((c for c in dental_colleges if c['code'] == college_code), None)
        
    if not college:
        return "College not found", 404
        
    courses = get_college_courses(college_code)

    # Always reload enriched data to ensure latest updates are shown
    load_enriched_data()
    
    enriched_data = None
    if college_code in ENRICHED_DATA:
        enriched_data = ENRICHED_DATA[college_code]
    
    if not enriched_data:
         # Empty structure
         enriched_data = {
            "links": {
                "placement": None, "hostel": None, "infrastructure": None,
                "academics": None, "admissions": None, "contact": None
            },
            "courses": []
         }

    # Merge explicit data (prioritize explicit links)
    explicit = get_college_explicit_data(college_code)
    if explicit and 'links' in explicit:
        for key, url in explicit['links'].items():
            if url:
                if key not in enriched_data['links'] or enriched_data['links'][key] is None:
                     enriched_data['links'][key] = {'url': url, 'content': None}
                elif isinstance(enriched_data['links'][key], dict):
                     enriched_data['links'][key]['url'] = url

    return render_template('college_details.html', college=college, courses=courses, enriched_data=enriched_data)

@app.route('/predictor', methods=['GET', 'POST'])
def predictor():
    if request.method == 'POST':
        rank = request.form.get('rank')
        branch = request.form.getlist('branch')
        category = request.form.get('category')

        results = predict_colleges(rank, branch, category)

        return render_template('results.html', results=results, rank=rank, branch=branch)
    return render_template('predictor.html', engineering_branches=engineering_branches, architecture_branches=architecture_branches)

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/courses')
def courses():
    return render_template('courses.html', engineering_branches=engineering_branches, architecture_branches=architecture_branches)
