import pandas as pd
import os
from glob import glob
import re

# ----------------------------
# 1️⃣ SET FOLDER PATH
# ----------------------------
folder = r"C:\Projects\COMEDK_DTL\data\raw"
output_file_name = "COMEDK_BARCH_ALL_ROUNDS.csv"

# ----------------------------
# 2️⃣ GET ALL FILES
# ----------------------------
# Find all CSV files in the folder
all_files = glob(os.path.join(folder, "*.csv"))

# Filter out the script itself, the output file if it exists, and the temp file
files = [f for f in all_files 
         if "EXCELTOCSV.py" not in f 
         and output_file_name not in f
         and "COMEDK_2025_BARCH_R3.csv" not in f # duplicate/temp
        ]

print(f"Found {len(files)} B.Arch files to process.")

if not files:
    print("❌ No files found! Check folder path.")
    exit()

# ----------------------------
# 3️⃣ HELPER FUNCTIONS
# ----------------------------

def extract_meta_from_filename(filename):
    # Extracts year and round from filenames like:
    # BARCH_2022_R1.csv, BARCH_2024_R2_2.csv, COMEDK_2022_BARCH_R1.csv
    base = os.path.basename(filename).upper()
    
    # Defaults
    year = 2024
    round_val = "R1"
    
    # 1. Extract Year (YYYY)
    y_match = re.search(r"202[0-9]", base)
    if y_match:
        year = int(y_match.group(0))
        
    # 2. Extract Round
    # Logic: Look for R1, R2, R3. If R2_1 or R2_2, map to R2 (or keep specific if needed)
    # The master data uses R1, R2, R3. 
    # We should normalize specific sub-rounds to main rounds for prediction logic, 
    # or keep them if detailed tracking is needed. 
    # Let's map to main rounds R1, R2, R3 for simplicity to match master.
    
    if "R1" in base: round_val = "R1"
    elif "R2" in base: round_val = "R2"
    elif "R3" in base: round_val = "R3"
    
    return year, round_val

# ----------------------------
# 4️⃣ PROCESS FILES
# ----------------------------
all_data = []

for file in files:
    try:
        # Read CSV
        # Some might have no headers or different encodings, handle simply for now
        df = pd.read_csv(file)
        
        # Determine Year/Round from filename
        year, round_val = extract_meta_from_filename(file)
        
        # NORMALIZE COLUMNS
        # Goal: year, round, college_code, college_name, branch, category, closing_rank
        
        # Common variations in column names?
        # Let's clean up column names: strip spaces, lower case for matching
        df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(' ', '_').str.replace('.', '')

        # Standardize 'Round No' or similar if present inside file to overwrite filename Metadata?
        # Usually checking filename is safer if file content is messy.
        
        df['year'] = year
        df['round'] = round_val
        
        # Map found columns to standard names
        # We need: college_code, college_name, branch, category, closing_rank
        # Mappings based on likely headers:
        
        # college_code
        if 'code' in df.columns: df.rename(columns={'code': 'college_code'}, inplace=True)
        elif 'college_code' not in df.columns and len(df.columns) > 0:
             # Blind guess? No, let's look for known patterns if needed.
             pass

        # college_name
        if 'college' in df.columns: df.rename(columns={'college': 'college_name'}, inplace=True)
        if 'institute_name' in df.columns: df.rename(columns={'institute_name': 'college_name'}, inplace=True)

        # branch
        if 'course' in df.columns: df.rename(columns={'course': 'branch'}, inplace=True)
        if 'course_name' in df.columns: df.rename(columns={'course_name': 'branch'}, inplace=True)
        
        # category
        if 'cat' in df.columns: df.rename(columns={'cat': 'category'}, inplace=True)
        
        # closing_rank
        if 'rank' in df.columns: df.rename(columns={'rank': 'closing_rank'}, inplace=True)
        if 'cutoff' in df.columns: df.rename(columns={'cutoff': 'closing_rank'}, inplace=True)
        if 'cr' in df.columns: df.rename(columns={'cr': 'closing_rank'}, inplace=True) # sometimes used
        
        # Check if mandatory columns exist
        required = ['college_code', 'branch', 'closing_rank']
        missing = [c for c in required if c not in df.columns]
        
        if missing:
            # Fallback: Assume positional if simple CSV (Code, Name, Branch, Category, Rank)
            # Typically: Code, Name, Branch, Category, Rank (5 cols)
            if len(df.columns) >= 5:
                # We assume column order: Code, Name, Branch, Category, Rank/CR
                print(f"⚠️ {os.path.basename(file)} missing headers {missing}. Using positional mapping.")
                # Create a copy to avoid SettingWithCopy warnings if relevant
                temp_df = df.iloc[:, :5].copy()
                temp_df.columns = ['college_code', 'college_name', 'branch', 'category', 'closing_rank']
                # Restore meta
                temp_df['year'] = year
                temp_df['round'] = round_val
                df = temp_df
            else:
                print(f"❌ Skipping {os.path.basename(file)}: Missing required columns {missing} and structure unclear.")
                continue

        # Clean Closing Rank
        df['closing_rank'] = pd.to_numeric(df['closing_rank'], errors='coerce')
        df = df.dropna(subset=['closing_rank'])
        df['closing_rank'] = df['closing_rank'].astype(int)
        
        # Ensure 'branch' has values
        df['branch'] = df['branch'].fillna("Architecture") # Default if missing
        
        # Ensure category exists
        if 'category' not in df.columns:
            df['category'] = 'GM' # Default
            
        # Select final columns
        final_cols = ['year', 'round', 'college_code', 'college_name', 'branch', 'category', 'closing_rank']
        
        # Fill missing with None/Empty before selection
        for c in final_cols:
            if c not in df.columns:
                df[c] = None
                
        all_data.append(df[final_cols])
        print(f"   Processed {os.path.basename(file)} ({len(df)} rows)")

    except Exception as e:
        print(f"❌ Error reading {file}: {e}")

# ----------------------------
# 5️⃣ MERGE & SAVE
# ----------------------------
if all_data:
    merged_df = pd.concat(all_data, ignore_index=True)
    
    output_path = os.path.join(folder, output_file_name)
    merged_df.to_csv(output_path, index=False)
    
    print(f"\n✅ SUCCESS! Merged {len(merged_df)} records into:")
    print(f"   {output_path}")
else:
    print("\n❌ No data merged.")









