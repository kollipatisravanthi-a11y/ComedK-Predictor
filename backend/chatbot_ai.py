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
from backend.utils import load_comedk_data
from backend.prediction import predict_colleges

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
            
            # Create and train pipeline
            self.model = make_pipeline(TfidfVectorizer(), LogisticRegression())
            self.model.fit(patterns, tags)
            print("Chatbot model trained successfully.")
            
            # Load college data using utils
            self.colleges_df = load_comedk_data(base_dir)
            
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
            response += f"Location: {found_college['location']}\n\n"
            
            # Look up courses in the CSV
            if not self.colleges_df.empty:
                # Filter by college code or name
                # The CSV has 'College_Code' and 'College_Name'
                # colleges_list has 'code' and 'name'
                
                college_courses = self.colleges_df[self.colleges_df['College_Code'] == found_college['code']]
                
                if not college_courses.empty:
                    response += "Available Courses (based on recent data):\n"
                    courses = college_courses['Course_Name'].unique()
                    for course in courses:
                        response += f"- {course}\n"
                else:
                    response += "Course details are not available in my current database, but they likely offer standard engineering branches."
            else:
                response += "Course details are currently unavailable."
                
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
                    
            return "I'm having trouble processing that."
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Sorry, I encountered an error."

chatbot = ChatBot()
