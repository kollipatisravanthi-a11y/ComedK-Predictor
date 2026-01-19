import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder
from sqlalchemy import text
from backend.database import engine
from backend.branches_data import engineering_branches, architecture_branches
import sys
import os

# Ensure we can import from backend if running directly (though module run is preferred)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class MLEngine:
    def __init__(self):
        self.categorical_cols = ["college_code", "branch_code", "category", "seat_type", "round_no"]
        self.encoders = {}
        self.model = None

    def fetch_data(self):
        print("📊 Fetching historical data from database...")
        query = """
        SELECT
            year,
            round,
            college_code,
            college_name,
            branch,
            category,
            closing_rank
        FROM COMEDK_MASTER_2021_2025
        WHERE closing_rank IS NOT NULL
        ORDER BY year ASC
        """
        df = pd.read_sql(query, engine)
        return df

    def prepare_data(self, df):
        print("🛠️  Preparing and cleaning data...")
        
        # 1. Clean Round Information
        df["round_no"] = df["round"].astype(str).str.extract(r"(\d+)").astype(float).fillna(1).astype(int)
        
        # 2. Normalize Branch Info (Simplified logic compared to old store_predictions)
        # We will trust the recent data's structure for training
        # For this implementation, we focus on rows that can be validly encoded.
        
        # Create a branch code map for robust encoding if needed, 
        # but for XGBoost, we can just label encode the strings directly if consistent.
        # However, to maintain consistency with 'previous_year' logic, we need to align rows.
        
        # Let's clean column types
        df["college_code"] = df["college_code"].astype(str).str.strip()
        df["branch"] = df["branch"].astype(str).str.strip()
        df["category"] = df["category"].astype(str).str.strip()
        
        # Handle Category Normalization
        df["category"] = df["category"].replace({"GM/KKR": "GM", "HKR": "KKR"})
        
        # 3. Create 'previous_year_cutoff' feature
        # We need to self-join or shift. Since data is sparse (not time-series per se for every single combo),
        # we can't just shift. We must join on keys.
        
        # Unique keys: college, branch, category, round
        # We want to find the cutoff for the SAME key in (year - 1)
        
        df_prev = df.copy()
        df_prev["year"] = df_prev["year"] + 1  # Shift year forward to match current
        df_prev = df_prev.rename(columns={"closing_rank": "previous_year_cutoff"})
        
        # Join
        train_df = pd.merge(
            df, 
            df_prev[["year", "college_code", "branch", "category", "round_no", "previous_year_cutoff"]],
            on=["year", "college_code", "branch", "category", "round_no"],
            how="inner" 
        )
        
        # We also need a 'seat_type' column if we want to match the demo script, 
        # but the DB data doesn't seem to have 'seat_type' explicitly populated in the select above?
        # The demo script used 'seat_type'. If it's not in DB, we ignore or infer.
        # Assuming 'seat_type' is constant or implied 'AT' (All India) or similar for now.
        train_df["seat_type"] = "AT" # Default placeholder
        
        # Assign branch_code (mock or extraction) for feature completeness
        # We can just encode 'branch' name as 'branch_code'
        train_df["branch_code"] = train_df["branch"] 
        
        return train_df

    def train_model(self, train_df):
        print("🧠 Training XGBoost model...")
        
        X = train_df.drop(["closing_rank", "college_name", "branch", "round"], axis=1) # Drop non-features
        y = train_df["closing_rank"]
        
        # Encode
        for col in self.categorical_cols:
            if col in X.columns:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
                self.encoders[col] = le
        
        # Train
        self.model = XGBRegressor(
            n_estimators=400,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=42
        )
        self.model.fit(X, y)
        print("✅ Model trained successfully.")

    def generate_predictions_2026(self, full_historical_df):
        print("🔮 Generating predictions for 2026...")
        
        # We need the 2025 data to serve as 'previous_year_cutoff' for 2026
        last_year_data = full_historical_df[full_historical_df["year"] == 2025].copy()
        
        if last_year_data.empty:
            print("⚠️ No 2025 data found. Cannot predict 2026.")
            return pd.DataFrame()

        predictions = []
        
        # Prepare input for 2026
        # The 'year' for prediction is 2026
        # 'previous_year_cutoff' is the 'closing_rank' from 2025
        
        for _, row in last_year_data.iterrows():
            # For each existing record in 2025, we predict 2026
            # We assume the same rounds exist. 
            
            input_row = row.copy()
            input_row["year"] = 2026
            input_row["previous_year_cutoff"] = row["closing_rank"]
            input_row["seat_type"] = "AT" # Default
            
            # Helper for encoding
            # We must use the SAME encoders. Handle unseen labels gracefully?
            # XGBoost handles numeric, but LE needs string match.
            # If a college/branch is new (unlikely if coming from 2025), it might fail.
            
            try:
                # Construct features dict
                features = {
                    "college_code": row["college_code"],
                    "branch_code": row["branch"], # Using branch name as code per training
                    "category": row["category"],
                    "seat_type": "AT",
                    "year": 2026,
                    "previous_year_cutoff": row["closing_rank"],
                    "round_no": int(str(row["round"]).replace("R", ""))
                }
                
                # Check domain rules helper
                pred_rank = self._predict_single(features)
                
                predictions.append({
                    "year": 2026,
                    "college_code": row["college_code"],
                    "college_name": row["college_name"],
                    "branch": row["branch"],
                    "category": row["category"],
                    "round": row["round"],
                    "predicted_closing_rank": pred_rank
                })
                
            except Exception as e:
                # print(f"Skipping row due to error: {e}")
                continue
                
        return pd.DataFrame(predictions)

    def _predict_single(self, input_dict):
        # Convert to DF for prediction
        input_df = pd.DataFrame([input_dict])
        
        # Encode
        for col in self.categorical_cols:
            if col in self.encoders:
                # Handle unseen labels by assigning a default or known
                # Simplified: assumption is 2025 data was present in historical set (or encoders cover it)
                # If 2025 data was NOT in 'train_df' (because it had no 'previous' 2024 match?), it might be missing from encoders?
                # Actually, fetch_data gets ALL data. prepare_data filters for inner join.
                # If a college appeared ONLY in 2025, it won't be in train set, so encoder won't know it.
                # FALLBACK: Use raw value 0 or handle error.
                
                val = str(input_dict[col])
                if val in self.encoders[col].classes_:
                    input_df[col] = self.encoders[col].transform([val])
                else:
                    # Fallback or error. For now, assign 0
                    input_df[col] = 0
        
        # Predict
        # Columns must match training order!
        # Train cols: year, college_code, branch_code, category, round_no, seat_type, previous_year_cutoff 
        # (check train_df columns in train_model)
        
        # Let's ensure column order matches X in train_model
        # X dropped "closing_rank", "college_name", "branch", "round"
        # It kept: year, college_code, category, round_no, previous_year_cutoff, seat_type, branch_code
        
        # Reorder input_df to match
        feature_order = self.model.feature_names_in_
        input_df = input_df[feature_order]
        
        pred_raw = self.model.predict(input_df)[0]
        predicted = int(pred_raw)
        
        # Domain Rules (from xgb_cutoff_predictor.py)
        last_year = input_dict["previous_year_cutoff"]
        
        # Rule 1: Rank >= 1
        predicted = max(1, predicted)
        
        # Rule 2: No unrealistic improvement (rank drops too much)
        # Lower rank = better. "Improvement" means rank gets smaller (e.g. 1000 -> 500)
        # "predicted < last_year - 500" means it improved by more than 500.
        if predicted < last_year - 500:
            predicted = last_year - 500
            
        # Rule 3: No unrealistic drop (rank increases too much)
        if predicted > last_year + 1000:
            predicted = last_year + 1000
            
        # Rule 4: Round 3 loosens
        if input_dict["round_no"] >= 3:
            predicted += 100
            
        return int(predicted)

def run_pipeline():
    engine_ml = MLEngine()
    
    # 1. Fetch
    df = engine_ml.fetch_data()
    
    # 2. Prepare Train
    train_df = engine_ml.prepare_data(df)
    
    if train_df.empty:
        print("❌ Not enough historical data overlap to train (need at least 2 consecutive years).")
        return pd.DataFrame()

    # 3. Train
    engine_ml.train_model(train_df)
    
    # 4. Predict
    preds_df = engine_ml.generate_predictions_2026(df)
    
    return preds_df
