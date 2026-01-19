import pandas as pd
import os
from backend.database import engine
from backend.store_predictions import generate_predictions

def setup_database():
    print("🚀 Starting Database Setup...")
    
    # 1. Load Master Data CSV
    master_csv = r'data\processed\COMEDK_MASTER_2021_2025.csv'
    if not os.path.exists(master_csv):
        print(f"❌ Error: {master_csv} not found in current directory: {os.getcwd()}")
        print(f"Directory contents: {os.listdir(os.path.dirname(master_csv)) if os.path.exists(os.path.dirname(master_csv)) else 'Directory does not exist!'}")
        return

    print(f"📂 Reading {master_csv}...")
    try:
        df_master = pd.read_csv(master_csv)
        print(f"   Loaded {len(df_master)} rows from master file.")
        print(f"   Columns: {df_master.columns.tolist()}")

        # 1.1 Load B.Arch Data (if exists)
        barch_csv = r'data\processed\COMEDK_MASTER_BARCH.csv'
        if os.path.exists(barch_csv):
            print(f"📂 Reading {barch_csv}...")
            try:
                df_barch = pd.read_csv(barch_csv)
                if not df_barch.empty:
                    # Rename columns to match master if needed
                    # BArch: year,round_no,college_code,college_name,branch,category,closing_rank
                    if 'round_no' in df_barch.columns:
                        df_barch.rename(columns={'round_no': 'round'}, inplace=True)
                    
                    # Convert round 1 -> R1
                    # Ensure round column is string type first
                    df_barch['round'] = 'R' + df_barch['round'].astype(str).str.replace('R', '', regex=False)

                    # Normalize columns to match master
                    # Master: year,round,round_order,college_code,college_name,branch,category,closing_rank
                    
                    # Add missing round_order if needed
                    if 'round_order' not in df_barch.columns:
                        # Map R1->1, R2->2, etc.
                        df_barch['round_order'] = df_barch['round'].astype(str).str.extract(r'(\d+)').fillna(0).astype(int)
                    
                    # Ensure all master columns exist
                    for col in df_master.columns:
                        if col not in df_barch.columns:
                            df_barch[col] = None
                            
                    # align columns
                    df_barch = df_barch[df_master.columns]
                    
                    print(f"   Appending {len(df_barch)} B.Arch rows.")
                    df_master = pd.concat([df_master, df_barch], ignore_index=True)
                else:
                    print("   ⚠️ B.Arch file is empty.")
            except Exception as ex:
                print(f"   ⚠️ Error reading B.Arch file: {ex}")

        # 2. Write to SQLite
        print("💾 Saving to SQLite database (comedk.db)...")
        try:
            df_master.to_sql('COMEDK_MASTER_2021_2025', engine, if_exists='replace', index=False)
            print("✅ Master data secured in database.")
        except Exception as e:
            print(f"❌ Error writing master data to database: {e}")
            import traceback
            traceback.print_exc()
            return
        
    except Exception as e:
        print(f"❌ Error loading master data: {e}")
        import traceback
        traceback.print_exc()
        return

    # 3. Generate Predictions
    print("\n🔮 Generating 2026 Predictions based on historical trends...")
    try:
        generate_predictions()
        print("✅ Predictions generated and stored in 'predictions_2026' table.")
        # Export predictions_2026 to CSV for inspection
        try:
            import pandas as pd
            from sqlalchemy import text
            df_pred = pd.read_sql_query(text("SELECT * FROM predictions_2026"), engine)
            pred_csv = r'data/processed/predictions_2026_export.csv'
            df_pred.to_csv(pred_csv, index=False)
            print(f"✅ Exported predictions_2026 to {pred_csv} with {len(df_pred)} rows.")
        except Exception as ex:
            print(f"❌ Error exporting predictions_2026 to CSV: {ex}")
            import traceback
            traceback.print_exc()
    except Exception as e:
        print(f"❌ Error generating predictions: {e}")
        import traceback
        traceback.print_exc()

    print("\n🎉 Setup Complete! You can now run 'python run.py'.")

if __name__ == "__main__":
    setup_database()
