import json
import random
import os
import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from backend.colleges_data import colleges_list
# from backend.utils import load_comedk_data
# from backend.prediction import predict_colleges
from sqlalchemy import create_engine, text

# DB Configuration
SERVER = 'LAPTOP-H91N3543\\SQLEXPRESS'
DATABASE = 'COMEDK_DB'
engine = create_engine(f'mssql+pyodbc://@{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes')

def predict_colleges(rank, branch=None, category='GM'):
    """
    Predict colleges based on rank using the predictions_2026 table.
    """
    try:
        with engine.connect() as conn:
            # Construct query
            # predicted_closing_rank is what we have. Filter by R3 for 'final' cutoff estimation.
            query_str = "SELECT college_name, branch, predicted_closing_rank FROM predictions_2026 WHERE predicted_closing_rank >= :rank AND round = 'R3'"
            params = {"rank": rank}
            
            if category:
                query_str += " AND category = :category"
                params["category"] = category
                
            if branch:
                query_str += " AND branch = :branch"
                params["branch"] = branch
                
            query_str += " ORDER BY predicted_closing_rank ASC"
            
            # Limit results
            query_str += " OFFSET 0 ROWS FETCH NEXT 15 ROWS ONLY"
            
            result = conn.execute(text(query_str), params)
            predictions = []
            for row in result:
                predictions.append({
                    "college": row[0],
                    "branch": row[1],
                    "cutoff": row[2],
                    "location": "Karnataka", # Placeholder as location is not in predictions table
                    "probability": "High" # Placeholder
                })
            return predictions
    except Exception as e:
        print(f"Prediction Error: {e}")
        return []

class ChatBot:
    def __init__(self):
        self.intents = []
        self.model = None
        self.colleges_df = None
        self.model_name = "GPT-5.1-Codex-Max"
        print(f"Enabled {self.model_name} for all clients")
        self.load_data_and_train()

    def load_data_and_train(self):
        # Load intents
        base_dir = os.path.dirname(os.path.abspath(__file__))
        intents_path = os.path.join(base_dir, 'intents.json')
        
        try:
            with open(intents_path, 'r') as f:
                data = json.load(f)
                
            self.intents = data['intents']
            
            patterns = []
            tags = []
            
            for intent in self.intents:
                for pattern in intent['patterns']:
                    patterns.append(pattern)
                    tags.append(intent['tag'])
            
            # --- Augment training data with College names and Ranks ---
            # This ensures the model recognizes specific college names and rank queries
            # even if they are not explicitly in intents.json
            
            for college in colleges_list:
                # Extract main name (e.g. 'Acharya Institute of Technology' from 'Acharya Institute of Technology- Soladevanahalli...')
                full_name = college.get('name', '')
                main_name = full_name.split('-')[0].strip()
                
                # Add patterns for 'colleges' intent or specific query
                # We associate them with 'colleges' or 'cutoff' based on context if we had it,
                # but here we'll map them to a new 'college_specific' intent or just 'colleges'
                # For now, let's map to 'colleges' to ensure it's recognized as a college query
                
                if main_name:
                    patterns.append(main_name)
                    tags.append('colleges')
                    patterns.append(f"Tell me about {main_name}")
                    tags.append('colleges')
                    patterns.append(f"cutoff for {main_name}")
                    tags.append('cutoff')
                    patterns.append(f"courses in {main_name}")
                    tags.append('colleges')
                
                # Add code
                code = college.get('code', '')
                if code:
                    patterns.append(code)
                    tags.append('colleges')

            # Add Rank patterns covering a wide range to ensure numerical literacy in the vectorizer
            # (Though regex catches explicit numbers, this helps 'my rank is...' type queries)
            for r in [1, 100, 1000, 5000, 10000, 20000, 50000, 100000]:
                patterns.append(f"Rank {r}")
                tags.append('rank')
                patterns.append(f"My rank is {r}")
                tags.append('rank')
                patterns.append(f"predict for {r}")
                tags.append('rank')

            # -----------------------------------------------------------

            # Create and train pipeline
            self.model = make_pipeline(TfidfVectorizer(), LogisticRegression())
            self.model.fit(patterns, tags)
            print("Chatbot model trained successfully.")
            
            # Load college data
            enriched_path = os.path.join(base_dir, '../data/processed/linear_model_results_enriched.csv')
            if os.path.exists(enriched_path):
                 self.colleges_df = pd.read_csv(enriched_path)
                 print(f"Chatbot loaded enriched linear model results from {enriched_path}")
            else:
                 print("Chatbot: Enriched data not found. Please run result generation.")
                 self.colleges_df = pd.DataFrame() # Empty to avoid using forbidden data

            # Load Enriched Web Data (Placements, Hostels etc.)
            enriched_json_path = os.path.join(base_dir, 'college_data_enriched.json')
            self.enriched_web_data = {}
            if os.path.exists(enriched_json_path):
                try:
                    with open(enriched_json_path, 'r', encoding='utf-8') as f:
                        self.enriched_web_data = json.load(f)
                    print(f"Chatbot loaded enriched web data for {len(self.enriched_web_data)} colleges.")
                except Exception as e:
                    print(f"Error loading enriched web data: {e}")

        except Exception as e:
            print(f"Error initializing chatbot: {e}")
            self.model = None

    def get_college_info(self, message):
        message = message.lower()
        found_college = None
        
        # Check against the comprehensive list from colleges_data.py
        for college in colleges_list:
            # Simple fuzzy matching: check if college name parts are in message
            # Or check if a significant part of the college name is in the message
            college_name_lower = college['name'].lower()
            
            # Extract main name (e.g., "BMS College of Engineering" from "BMS College of Engineering-Basavanagudi...")
            main_name = college_name_lower.split('-')[0].strip()
            
            if main_name in message:
                found_college = college
                break
            
            # Also check for common abbreviations if possible, or just partial match
            # For now, let's stick to the main name check
            
        if found_college:
            response = f"**{found_college['name']}**\n"
            response += f"Location: {found_college['location']}\n"
            
            # Check for specific info types in user message
            info_type = None
            if any(w in message for w in ["placement", "package", "salary", "recruiters"]):
                info_type = "placement"
            elif any(w in message for w in ["hostel", "accommodation", "dorm"]):
                info_type = "hostel"
            elif any(w in message for w in ["infrastructure", "campus", "facilities"]):
                info_type = "infrastructure"
            elif any(w in message for w in ["academic", "curriculum", "faculty"]):
                info_type = "academics"
            elif any(w in message for w in ["admission", "eligibility", "process"]):
                info_type = "admissions"
                
            # If enriched data exists and users asks for specific info
            code = found_college['code']
            if info_type and self.enriched_web_data and code in self.enriched_web_data:
                details = self.enriched_web_data[code].get('links', {}).get(info_type)
                if details:
                    if details.get('url'):
                        response += f"\nHere is the official {info_type} information: {details['url']}\n"
                    if details.get('content') and len(details['content']) > 20:
                        # Extract a snippet
                        snippet = details['content'][:300].replace('\n', ' ') + "..."
                        response += f"Snippet: {snippet}\n"
                    else:
                        response += f"\n(Further details available on the official website)\n"
                else:
                    response += f"\nSpecific {info_type} details are not currently indexed. Please visit: {found_college.get('website', 'official website')}\n"
            
            # Look up courses in the CSV if no specific info requested or just general
            elif not info_type and not self.colleges_df.empty:
                # Normalize columns for access
                df = self.colleges_df.copy()
                df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
                
                # Check column existence
                code_col = 'college_code' if 'college_code' in df.columns else None
                course_col = 'course' if 'course' in df.columns else None
                
                if code_col and course_col:
                    college_courses = df[df[code_col] == found_college['code']]
                    
                    if not college_courses.empty:
                        response += "\nAvailable Courses:\n"
                        courses = college_courses[course_col].unique()
                        for course in courses:
                            response += f"- {course}\n"
            
            # Helper text
            if not info_type:
                 response += "\nYou can also ask about **placements**, **hostels**, or **fees** for this college."
                
            return response
            
        return None

    def get_response(self, message):
        if not self.model:
            return "I am currently under maintenance. Please try again later."
            
        if not message:
            return "Please say something."
            
        try:
            # Check for rank prediction request
            # Look for "rank" followed by number, or just a number if it looks like a rank
            rank_match = re.search(r'rank\s*[:is]?\s*(\d+)', message.lower())
            if not rank_match:
                # Try to find just a number if the message is short (e.g. "5000")
                if message.strip().isdigit():
                    rank_match = re.search(r'(\d+)', message)
            
            if rank_match:
                rank = int(rank_match.group(1))
                # Call prediction logic
                # Default to GM category and no specific branch for general queries
                results = predict_colleges(rank, None, 'GM')
                
                # Sort by highest admission probability (Descending Cutoff)
                # Higher cutoff means easier to get in (higher probability)
                results.sort(key=lambda x: x['cutoff'], reverse=True)
                
                response = f"Entered Rank: {rank}\n\n"
                
                if results:
                    response += "Eligible Colleges and Branches (Based on Final Round Cutoffs):\n"
                    # Limit to top 10-15 to avoid huge messages
                    for i, res in enumerate(results[:15], 1):
                        response += f"{i}. {res['college']} – {res['branch']} (Final Closing Rank: {res['cutoff']})\n"
                else:
                    response += "Based on previous years’ final round cutoffs, no colleges are available for the given rank."
                
                return response

            # First, check if the user is asking about a specific college
            college_response = self.get_college_info(message)
            if college_response:
                return college_response

            # Predict intent
            probs = self.model.predict_proba([message])[0]
            max_prob = np.max(probs)
            predicted_tag = self.model.classes_[np.argmax(probs)]
            
            if max_prob < 0.3: 
                return "I'm not sure I understand. You can ask me about COMEDK exam, colleges, cutoffs, or how to use this predictor."
                
            for intent in self.intents:
                if intent['tag'] == predicted_tag:
                    return random.choice(intent['responses'])
                    
            return "I'm sorry, can you ask about colleges, cutoffs etc?"
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Sorry, I encountered an error."

chatbot = ChatBot()
