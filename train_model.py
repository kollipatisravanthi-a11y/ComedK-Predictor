"""
Train machine learning model for COMEDK rank prediction.
Uses ensemble methods for accurate predictions.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os

def load_data(filepath='data/comedk_training_data.csv'):
    """Load training data from CSV."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Training data not found at {filepath}")
    return pd.read_csv(filepath)

def prepare_features(df):
    """Prepare features for training."""
    # Features: individual subject scores and total score
    X = df[['physics_score', 'chemistry_score', 'math_score', 'total_score']].values
    y = df['rank'].values
    return X, y

def train_model(X, y):
    """Train the rank prediction model."""
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest model
    print("Training Random Forest model...")
    rf_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train_scaled, y_train)
    
    # Train Gradient Boosting model
    print("Training Gradient Boosting model...")
    gb_model = GradientBoostingRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    )
    gb_model.fit(X_train_scaled, y_train)
    
    # Evaluate models
    print("\n=== Model Evaluation ===")
    
    for name, model in [("Random Forest", rf_model), ("Gradient Boosting", gb_model)]:
        y_pred = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        print(f"\n{name}:")
        print(f"  Mean Absolute Error: {mae:.2f}")
        print(f"  Root Mean Squared Error: {rmse:.2f}")
        print(f"  R² Score: {r2:.4f}")
    
    # Use Random Forest as primary model (usually performs better for this task)
    return rf_model, scaler, X_test_scaled, y_test

def save_model(model, scaler, model_path='models/rank_predictor.pkl', 
               scaler_path='models/scaler.pkl'):
    """Save trained model and scaler."""
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"\nModel saved to {model_path}")
    print(f"Scaler saved to {scaler_path}")

def main():
    """Main training pipeline."""
    print("Loading training data...")
    df = load_data()
    
    print(f"Loaded {len(df)} training samples")
    print(f"Score range: {df['total_score'].min():.2f} - {df['total_score'].max():.2f}")
    print(f"Rank range: {df['rank'].min()} - {df['rank'].max()}")
    
    print("\nPreparing features...")
    X, y = prepare_features(df)
    
    print("\nTraining model...")
    model, scaler, X_test, y_test = train_model(X, y)
    
    # Save model
    save_model(model, scaler)
    
    print("\n=== Training Complete ===")
    print("Model is ready for predictions!")

if __name__ == "__main__":
    main()
