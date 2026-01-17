import json
import os

import pandas as pd
from flask import jsonify, render_template, request
from sqlalchemy import create_engine, inspect, text

from backend.app import app
from backend.branches_data import architecture_branches, engineering_branches
from backend.chatbot_ai import chatbot
from backend.college_agent import college_agent
from backend.college_details_data import get_college_explicit_data
from backend.colleges_data import architecture_colleges, colleges_list, dental_colleges, medical_colleges

# Removed unused imports
# from backend.prediction import get_college_courses
# from backend.prediction_2025 import predictor_2025
from backend.database import engine

# engine = create_engine(
#     "mssql+pyodbc://@localhost\\SQLEXPRESS/COMEDK_DB"
#     "?driver=ODBC+Driver+17+for+SQL+Server"
#     "&trusted_connection=yes"
# )

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


def get_college_courses_db(college_code):
    try:
        # Fetch unique branches for 2026 predictions (which represent 2025 active courses)
        with engine.connect() as conn:
            # Check columns first
            inspector = inspect(engine)
            columns = {col['name'] for col in inspector.get_columns('predictions_2026')}
            
            if 'branch_code' in columns:
                query = text("SELECT DISTINCT branch, branch_code FROM predictions_2026 WHERE college_code = :code AND branch NOT LIKE '%Arch%' ORDER BY branch")
                result = conn.execute(query, {"code": college_code})
                courses = [{"name": row[0], "code": row[1]} for row in result]
            else:
                query = text("SELECT DISTINCT branch FROM predictions_2026 WHERE college_code = :code AND branch NOT LIKE '%Arch%' ORDER BY branch")
                result = conn.execute(query, {"code": college_code})
                courses = [{"name": row[0], "code": None} for row in result]
        return courses
    except Exception as e:
        print(f"Error fetching courses for {college_code}: {e}")
        return []

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
        
    # Use DB function instead of deleted module
    courses = get_college_courses_db(college_code)

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
    error = None
    results = []

    if request.method == 'POST':
        try:
            rank = int(request.form.get('rank', '').strip())
        except (TypeError, ValueError):
            rank = None
            error = "Please enter a valid numeric rank."

        category = request.form.get('category')

        if rank is not None and category:
            inspector = inspect(engine)
            columns = {col['name'] for col in inspector.get_columns('predictions_2026')}

            # Fallback if legacy table lacks category column
            if 'category' in columns:
                # Check for branch_code column
                has_branch_code = 'branch_code' in columns
                select_clause = "college_code, college_name, branch, " + ("branch_code, " if has_branch_code else "") + "round, category, predicted_closing_rank"
                
                sql = text(
                    f"""
                    SELECT {select_clause}
                    FROM predictions_2026
                    WHERE predicted_closing_rank >= :rank
                      AND category = :category
                    ORDER BY predicted_closing_rank ASC
                    """
                )
                params = {"rank": rank, "category": category}
            else:
                # Check for branch_code column
                has_branch_code = 'branch_code' in columns
                select_clause = "college_code, college_name, branch, " + ("branch_code, " if has_branch_code else "") + "round, NULL AS category, predicted_closing_rank"
                
                sql = text(
                    f"""
                    SELECT {select_clause}
                    FROM predictions_2026
                    WHERE predicted_closing_rank >= :rank
                    ORDER BY predicted_closing_rank ASC
                    """
                )
                params = {"rank": rank}

            with engine.begin() as conn:
                df = pd.read_sql_query(sql, conn, params=params)
            
            # --- START FILTER LOGIC ---
            if not df.empty:
                # 1. Filter out Architecture or Medical if present (User requested only B.E/B.Tech for results display)
                # Identify filtered codes
                arch_codes = [b['code'] for b in architecture_branches]
                
                # Filter by branch_code if column exists, otherwise weak filter by name?
                # The DB has 'branch_code', so use it if available in DF.
                if 'branch_code' in df.columns:
                     # Remove architecture codes
                     df = df[~df['branch_code'].isin(arch_codes)]
                
                # Extract numeric round for sorting
                # Note: 'round' might be 'R1', 'R2', or just '1', '2'
                df['round_num'] = df['round'].astype(str).str.extract(r'(\d+)').fillna(0).astype(int)
                
                # Match official names BEFORE deduplication so we sort by the correct name
                all_colleges = colleges_list + architecture_colleges + medical_colleges + dental_colleges
                code_to_name = {c['code']: c['name'] for c in all_colleges}
                
                def get_official_name(row):
                    code = row.get('college_code')
                    return code_to_name.get(code, row.get('college_name'))
                
                df['college_name'] = df.apply(get_official_name, axis=1)

                # Sort by College, Branch, Round (Ascending)
                # Keep ONLY the EARLIEST round for each college+branch combination I qualify for
                df.sort_values(by=['college_name', 'branch', 'round_num'], ascending=[True, True, True], inplace=True)
                df.drop_duplicates(subset=['college_name', 'branch'], keep='first', inplace=True)
                
                # Final sort by Closing Rank
                df.sort_values(by=['predicted_closing_rank'], ascending=True, inplace=True)
                
                results = df.to_dict(orient='records')
            else:
                results = []
            # --- END FILTER LOGIC ---

            # Skip the old loop since we handled name mapping and deduplication above
            # (Old loop code was lines 206-224)
        elif not error:
            error = "Rank and category are required."

        return render_template('results.html', results=results, rank=rank, category=category, branch="All Courses", error=error)
    return render_template('predictor.html', engineering_branches=engineering_branches, architecture_branches=architecture_branches)

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/courses')
def courses():
    return render_template('courses.html', engineering_branches=engineering_branches, architecture_branches=architecture_branches)
