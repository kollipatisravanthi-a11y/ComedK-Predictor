import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.colleges_data import colleges_list, architecture_colleges, medical_colleges, dental_colleges
    
    all_colleges = colleges_list + architecture_colleges + medical_colleges + dental_colleges
    code_to_name = {c['code']: c['name'] for c in all_colleges}
    
    print(f"Loaded {len(code_to_name)} college codes from colleges_data.py")
    
    csv_path = os.path.join(os.path.dirname(__file__), 'backend', 'final_cutoff_data.csv')
    if not os.path.exists(csv_path):
        print(f"CSV not found at {csv_path}")
        # Try absolute path based on previous knowledge or current dir
        csv_path = "c:\\Projects\\COMEDK_DTL\\backend\\final_cutoff_data.csv"
        
    print(f"Reading CSV from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    print("CSV Columns:", df.columns.tolist())
    
    if 'college_code' not in df.columns:
        print("ERROR: 'college_code' column missing from CSV")
        sys.exit(1)
        
    unique_codes = df['college_code'].unique()
    print(f"Found {len(unique_codes)} unique codes in CSV")
    
    missing_codes = []
    for code in unique_codes:
        if code not in code_to_name:
            missing_codes.append(code)
            
    if missing_codes:
        print(f"❌ Found {len(missing_codes)} codes in CSV that are MISSING from colleges_data:")
        print(missing_codes[:20]) # Print first 20
    else:
        print("✅ All codes in CSV are present in colleges_data mapping.")
        
    # Check sample row with mapping
    df['college_name'] = df['college_code'].map(code_to_name)
    print("\nSample Output (First 5 rows with mapped name):")
    print(df[['college_code', 'college_name']].head())

except Exception as e:
    print(f"Exception: {e}")
