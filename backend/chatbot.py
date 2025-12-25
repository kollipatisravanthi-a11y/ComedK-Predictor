import random

class ChatBot:
    def __init__(self):
        self.greetings = ["hello", "hi", "hey", "greetings", "good morning", "good evening"]
        self.farewells = ["bye", "goodbye", "see you", "cya"]
        
        self.responses = {
            "default": "I'm not sure I understand. You can ask me about COMEDK exam, colleges, cutoffs, or how to use this predictor.",
            "greeting": "Hello! I'm your COMEDK Assistant. How can I help you today?",
            "farewell": "Goodbye! Good luck with your college search!",
            "exam": "COMEDK UGET is a common entrance test held at the national level for admission to around 190 unaided private engineering colleges in Karnataka.",
            "colleges": "There are over 190 colleges accepting COMEDK scores. You can view the top colleges in the 'Colleges' tab.",
            "cutoff": "Cutoffs vary by college and branch. You can use our 'Predictor' tool to check which colleges you are eligible for based on your rank.",
            "rank": "Your rank is determined by your score in the COMEDK UGET exam. Lower rank is better.",
            "counselling": "Counselling usually happens in 3 rounds. You need to register, fill choices, and lock them.",
            "documents": "Common documents required are Admit Card, Rank Card, 10th/12th Marks Cards, ID Proof, etc.",
            "fees": "The tuition fee for COMEDK colleges is generally around 2-2.5 Lakhs per annum, but it varies by college.",
            "predictor": "To use the predictor, go to the 'Predictor' page, enter your rank, select your preferred branches, and click 'Predict Colleges'."
        }

    def get_response(self, message):
        message = message.lower()
        
        # Check for greetings
        if any(word in message for word in self.greetings):
            return self.responses["greeting"]
            
        # Check for farewells
        if any(word in message for word in self.farewells):
            return self.responses["farewell"]
            
        # Keyword matching
        if "exam" in message or "test" in message:
            return self.responses["exam"]
        elif "college" in message or "institute" in message:
            return self.responses["colleges"]
        elif "cutoff" in message or "rank" in message and "cutoff" in message:
            return self.responses["cutoff"]
        elif "rank" in message:
            return self.responses["rank"]
        elif "counselling" in message or "process" in message:
            return self.responses["counselling"]
        elif "document" in message or "certificate" in message:
            return self.responses["documents"]
        elif "fee" in message or "cost" in message:
            return self.responses["fees"]
        elif "predict" in message or "how to" in message:
            return self.responses["predictor"]
            
        return self.responses["default"]

chatbot = ChatBot()
