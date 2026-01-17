import pandas as pd
import os
from glob import glob

# ----------------------------
# 1️⃣ SET FOLDER PATH
# ----------------------------
folder = r"C:\Projects\COMEDK_DTL\data\raw"  # folder with all CSV/Excel files

# ----------------------------
# 2️⃣ GET ALL FILES
# ----------------------------
# Look for both CSV and Excel files
files = glob(os.path.join(folder, "*.csv")) + glob(os.path.join(folder, "*.xlsx"))

# Exclude the script itself and the output file from the list
output_file_name = "COMEDK_BARCH_ALL_ROUNDS.csv"
files = [f for f in files if "EXCELTOCSV.py" not in f and output_file_name not in f]

print(f"Found {len(files)} files:", files)

if not files:
    print("❌ No files found! Please check the folder path and file extensions.")
    exit()

# ----------------------------
# 3️⃣ READ & APPEND FILES
# ----------------------------
all_data = []

for file in files:
    print(f"Reading {os.path.basename(file)}...")
    try:
        if file.endswith(".xlsx"):
            # Try reading with header first
            df = pd.read_excel(file)
            
            # If columns look like default index or known specific structure without headers
            # Adjust logic here if you have specific typeless excel files
            # For now, simplistic check: if 'closing_rank' is not in columns, maybe it has no header
            if 'closing_rank' not in df.columns and 'branch' not in df.columns:
                 df = pd.read_excel(file, header=None)
                 # Map columns if we know the structure (Assuming 6 cols based on previous code)
                 if len(df.columns) >= 6:
                    df = df.iloc[:, :6]
                    df.columns = ["college_code", "college_name", "branch", "closing_rank", "category", "remarks"]
            
        else:
            df = pd.read_csv(file)
        
        # NORMALIZE COLUMN NAMES
        # We want 'branch' as the standard column name for the course
        if "course_name" in df.columns:
            df.rename(columns={"course_name": "branch"}, inplace=True)
            
        # Clean closing_rank
        if "closing_rank" in df.columns:
            df["closing_rank"] = pd.to_numeric(df["closing_rank"], errors="coerce")
            df = df.dropna(subset=["closing_rank"])
            df["closing_rank"] = df["closing_rank"].astype(int)
        
        # Add 'round' info if missing
        if "round" not in df.columns:
            round_name = os.path.basename(file).split(".")[0]
            df["round"] = round_name

        all_data.append(df)
        
    except Exception as e:
        print(f"⚠️ Error processing {file}: {e}")

# ----------------------------
# 4️⃣ CONCATENATE ALL DATA
# ----------------------------
if not all_data:
    print("❌ No valid data collected from files.")
    exit()

merged_df = pd.concat(all_data, ignore_index=True)

# ----------------------------
# 5️⃣ FINAL CLEAN & SAVE
# ----------------------------

# Extract Year and Round from the 'round' column (which contains filename)
# Expected formats like: COMEDK_2022_BARCH_R1, COMEDK_2024_BARCH_R2_1
def extract_meta(val):
    val = str(val).upper()
    year = 2024 # Default fallback
    round_val = "R1"
    
    # Extract Year
    import re
    y_match = re.search(r"202[0-9]", val)
    if y_match:
        year = int(y_match.group(0))
        
    # Extract Round
    if "R1" in val: round_val = "R1"
    elif "R2" in val: round_val = "R2"
    elif "R3" in val: round_val = "R3"
    
    return year, round_val

if not merged_df.empty:
    merged_df[["year", "clean_round"]] = merged_df["round"].apply(lambda x: pd.Series(extract_meta(x)))
    merged_df["round"] = merged_df["clean_round"]
    merged_df.drop(columns=["clean_round"], inplace=True)

# Ensure category exists, default to 'GM' if missing
if "category" not in merged_df.columns:
    merged_df["category"] = "GM"

# Keep standard columns to match master CSV
cols_to_keep = ["year", "round", "college_code", "college_name", "branch", "category", "closing_rank"]
available_cols = [c for c in cols_to_keep if c in merged_df.columns]

final_df = merged_df[available_cols]

# Add missing columns if any
for col in cols_to_keep:
    if col not in final_df.columns:
        final_df[col] = None

final_df = final_df[cols_to_keep] # Enforce order

output_path = os.path.join(folder, output_file_name)
final_df.to_csv(output_path, index=False)


print(f"✅ Merged file created: {output_path}")
print(f"   Total records: {len(final_df)}")








