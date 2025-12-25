import json
import random
import os
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from backend.colleges_data import colleges_list

class ChatBot:
    def __init__(self):
        self.intents = []
        self.model = None
        self.colleges_df = None
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
            
            # Load college data from CSV for courses
            csv_path = os.path.join(base_dir, '../data/raw/comedk_data.csv')
            if os.path.exists(csv_path):
                self.colleges_df = pd.read_csv(csv_path)
            else:
                print("Warning: comedk_data.csv not found.")
                self.colleges_df = pd.DataFrame()
            
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
