"""
Generate synthetic COMEDK training data for rank prediction model.
This creates realistic exam score and rank data based on typical COMEDK patterns.
"""

import pandas as pd
import numpy as np
import json

def generate_training_data(num_samples=10000):
    """
    Generate synthetic COMEDK exam data.
    
    COMEDK exam has:
    - Physics: 60 questions
    - Chemistry: 60 questions  
    - Mathematics: 60 questions
    - Total: 180 questions
    - Each correct answer: +1 mark
    - Each wrong answer: 0 marks (no negative marking)
    """
    np.random.seed(42)
    
    data = []
    
    for i in range(num_samples):
        # Generate scores with realistic distributions
        # Higher performers tend to score well across all subjects
        base_ability = np.random.beta(2, 5) * 100  # Overall ability level
        
        # Subject scores (out of 60 each)
        physics_score = np.clip(
            np.random.normal(base_ability * 0.6, 10), 0, 60
        )
        chemistry_score = np.clip(
            np.random.normal(base_ability * 0.6, 10), 0, 60
        )
        math_score = np.clip(
            np.random.normal(base_ability * 0.6, 10), 0, 60
        )
        
        total_score = physics_score + chemistry_score + math_score
        
        # Calculate rank (inverse relationship with score)
        # Adding some noise to make it realistic
        rank_base = (180 - total_score) ** 2 * 3
        rank = int(np.clip(rank_base + np.random.normal(0, 500), 1, 50000))
        
        data.append({
            'physics_score': round(physics_score, 2),
            'chemistry_score': round(chemistry_score, 2),
            'math_score': round(math_score, 2),
            'total_score': round(total_score, 2),
            'rank': rank
        })
    
    # Sort by rank to ensure consistency
    data = sorted(data, key=lambda x: x['rank'])
    
    # Reassign ranks to be sequential
    for idx, item in enumerate(data, 1):
        item['rank'] = idx
    
    return pd.DataFrame(data)

def save_data(df, filepath='data/comedk_training_data.csv'):
    """Save the training data to a CSV file."""
    df.to_csv(filepath, index=False)
    print(f"Training data saved to {filepath}")
    print(f"Total samples: {len(df)}")
    print(f"\nData statistics:")
    print(df.describe())

if __name__ == "__main__":
    df = generate_training_data(10000)
    save_data(df)
