"""
COMEDK Rank Predictor - Core prediction module.
"""

import joblib
import numpy as np
import os

class RankPredictor:
    """Class for predicting COMEDK ranks based on scores."""
    
    def __init__(self, model_path='models/rank_predictor.pkl', 
                 scaler_path='models/scaler.pkl'):
        """Initialize predictor with trained model and scaler."""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Please train the model first.")
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(f"Scaler not found at {scaler_path}. Please train the model first.")
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
    
    def predict_rank(self, physics_score, chemistry_score, math_score):
        """
        Predict COMEDK rank based on subject scores.
        
        Args:
            physics_score: Score in Physics (0-60)
            chemistry_score: Score in Chemistry (0-60)
            math_score: Score in Mathematics (0-60)
        
        Returns:
            dict: Predicted rank and related information
        """
        # Validate inputs
        if not (0 <= physics_score <= 60):
            raise ValueError("Physics score must be between 0 and 60")
        if not (0 <= chemistry_score <= 60):
            raise ValueError("Chemistry score must be between 0 and 60")
        if not (0 <= math_score <= 60):
            raise ValueError("Mathematics score must be between 0 and 60")
        
        # Calculate total score
        total_score = physics_score + chemistry_score + math_score
        
        # Prepare features
        features = np.array([[physics_score, chemistry_score, math_score, total_score]])
        features_scaled = self.scaler.transform(features)
        
        # Predict rank
        predicted_rank = self.model.predict(features_scaled)[0]
        predicted_rank = max(1, int(round(predicted_rank)))  # Ensure rank is at least 1
        
        # Calculate confidence interval (approximate)
        # This is a simplified approach - in production, you might want to use
        # prediction intervals from the model
        confidence_range = int(predicted_rank * 0.1)  # ±10% of predicted rank
        
        return {
            'predicted_rank': predicted_rank,
            'rank_range': {
                'lower': max(1, predicted_rank - confidence_range),
                'upper': predicted_rank + confidence_range
            },
            'total_score': total_score,
            'subject_scores': {
                'physics': physics_score,
                'chemistry': chemistry_score,
                'mathematics': math_score
            }
        }
    
    def get_rank_insights(self, physics_score, chemistry_score, math_score):
        """
        Get detailed insights about the predicted rank.
        
        Returns:
            dict: Prediction results with insights
        """
        result = self.predict_rank(physics_score, chemistry_score, math_score)
        total_score = result['total_score']
        
        # Add performance category
        if total_score >= 150:
            category = "Excellent"
            message = "Outstanding performance! You're in the top tier."
        elif total_score >= 120:
            category = "Very Good"
            message = "Great job! You have strong chances for good colleges."
        elif total_score >= 90:
            category = "Good"
            message = "Good performance. You should get admission to decent colleges."
        elif total_score >= 60:
            category = "Average"
            message = "Average performance. Consider improving your preparation."
        else:
            category = "Needs Improvement"
            message = "More preparation needed to secure a better rank."
        
        result['performance_category'] = category
        result['message'] = message
        
        return result

if __name__ == "__main__":
    # Example usage
    predictor = RankPredictor()
    
    # Test predictions
    test_cases = [
        (55, 58, 60),  # High scores
        (45, 48, 50),  # Good scores
        (30, 35, 32),  # Average scores
    ]
    
    print("=== COMEDK Rank Predictor - Test Predictions ===\n")
    for physics, chemistry, math in test_cases:
        result = predictor.get_rank_insights(physics, chemistry, math)
        print(f"Scores - Physics: {physics}, Chemistry: {chemistry}, Math: {math}")
        print(f"Total Score: {result['total_score']}/180")
        print(f"Predicted Rank: {result['predicted_rank']}")
        print(f"Rank Range: {result['rank_range']['lower']} - {result['rank_range']['upper']}")
        print(f"Category: {result['performance_category']}")
        print(f"Message: {result['message']}")
        print("-" * 60)
