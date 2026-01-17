import pandas as pd
import os
from backend.database import engine
from backend.store_predictions import generate_predictions

def setup_database():
    print("🚀 Starting Database Setup...")
    
    # 1. Load Master Data CSV
    master_csv = 'COMEDK_MASTER_2021_2025.csv'
    if not os.path.exists(master_csv):
        print(f"❌ Error: {master_csv} not found in current directory.")
        return

    print(f"📂 Reading {master_csv}...")
    try:
        df = pd.read_csv(master_csv)
        print(f"   Loaded {len(df)} rows.")
        
        # 2. Write to SQLite
        print("💾 Saving to SQLite database (comedk.db)...")
        df.to_sql('COMEDK_MASTER_2021_2025', engine, if_exists='replace', index=False)
        print("✅ Master data secured in database.")
        
    except Exception as e:
        print(f"❌ Error loading master data: {e}")
        return

    # 3. Generate Predictions
    print("\n🔮 Generating 2026 Predictions based on historical trends...")
    try:
        generate_predictions()
        print("✅ Predictions generated and stored in 'predictions_2026' table.")
    except Exception as e:
        print(f"❌ Error generating predictions: {e}")

    print("\n🎉 Setup Complete! You can now run 'python run.py'.")

if __name__ == "__main__":
    setup_database()
