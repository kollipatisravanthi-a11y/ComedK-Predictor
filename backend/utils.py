import pandas as pd
import os
import glob

def load_comedk_data(base_dir):
    """
    Loads COMEDK data from Excel or CSV and standardizes it.
    base_dir: The directory containing the 'data' folder (usually the project root or backend folder's parent).
    """
    # Handle paths relative to the backend or project root
    # We assume the structure is project_root/data/raw
    
    # If base_dir is the backend folder, go up one level
    if os.path.basename(base_dir) == 'backend':
        data_dir = os.path.join(base_dir, '../data/raw')
    else:
        data_dir = os.path.join(base_dir, 'data/raw')
        
    # Look for all comedk_*.xlsx files
    excel_files = glob.glob(os.path.join(data_dir, 'comedk_*.xlsx'))
    csv_path = os.path.join(data_dir, 'comedk_data.csv')
    
    dfs = []
    
    # Process Excel files
    for excel_path in excel_files:
        try:
            df = pd.read_excel(excel_path)
            print(f"Loaded data from {excel_path}")
            
            # Determine round from filename
            filename = os.path.basename(excel_path).lower()
            round_name = "Unknown"
            if "r1" in filename: round_name = "Round 1"
            elif "r2" in filename: round_name = "Round 2"
            elif "r3" in filename: round_name = "Round 3"
            elif "r4" in filename: round_name = "Round 4"
            
            # Determine year from filename
            year = "N/A"
            if "2024" in filename: year = "2024"
            elif "2025" in filename: year = "2025"
            elif "2023" in filename: year = "2023"
            
            # Transform if wide
            if 'College Code' in df.columns and 'Seat Category' in df.columns:
                print(f"Detected wide format data in {filename}. Transforming...")
                id_vars = ['College Code', 'College Name', 'Seat Category']
                # Value vars are all other columns that are not Unnamed
                value_vars = [c for c in df.columns if c not in id_vars and not str(c).startswith('Unnamed')]
                
                df_melted = df.melt(id_vars=id_vars, value_vars=value_vars, var_name='Branch', value_name='Rank')
                
                # Rename to standard columns
                df_melted.rename(columns={
                    'College Code': 'College_Code',
                    'College Name': 'College_Name',
                    'Seat Category': 'Category',
                    'Branch': 'Course_Name',
                    'Rank': 'Rank'
                }, inplace=True)
                
                # Extract Course Code from Course_Name if possible (e.g., "CS-Computer Science")
                # We assume the format is "CODE-Name" or "CODE - Name"
                try:
                    # Split by first hyphen
                    split_data = df_melted['Course_Name'].astype(str).str.split('-', n=1, expand=True)
                    if split_data.shape[1] == 2:
                        df_melted['Course_Code'] = split_data[0].str.strip()
                        # If the code is too long (e.g. it wasn't a code), maybe ignore? 
                        # But usually codes are short (2-3 chars). Let's keep it for now.
                except Exception as e:
                    print(f"Could not extract course code: {e}")
                
                # Clean Rank
                df_melted['Rank'] = pd.to_numeric(df_melted['Rank'], errors='coerce')
                df_melted.dropna(subset=['Rank'], inplace=True)
                
                df_melted['Round'] = round_name
                df_melted['Year'] = year
                dfs.append(df_melted)
            else:
                # Assume standard
                df['Round'] = round_name
                if 'Year' not in df.columns:
                    df['Year'] = year
                dfs.append(df)
                
        except Exception as e:
            print(f"Error reading Excel {excel_path}: {e}")
    
    # Try CSV if no Excel files loaded OR if we want to combine them
    # Currently the logic says "if not dfs", which means if Excel loaded, CSV is ignored.
    # But the CSV has the "CS", "EC" data we need!
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            print(f"Loaded data from {csv_path}")
            df['Round'] = 'Unknown'
            # Ensure columns match standard
            # CSV has: College_Code,College_Name,City,Course_Code,Course_Name,Opening_Rank,Closing_Rank,Year
            # We need: College_Code, College_Name, Category, Course_Name, Rank, Course_Code, Round, Year
            
            # Rename Closing_Rank to Rank
            if 'Closing_Rank' in df.columns:
                df.rename(columns={'Closing_Rank': 'Rank'}, inplace=True)
            
            # Add missing columns
            if 'Category' not in df.columns:
                df['Category'] = 'GM' # Default to GM for CSV data
                
            dfs.append(df)
        except Exception as e:
            print(f"Error reading CSV: {e}")
            
    if not dfs:
        return pd.DataFrame()
        
    final_df = pd.concat(dfs, ignore_index=True)
    return final_df

    # Check for Standard CSV Format (if it was already processed or is the old format)
    # Expected: College_Code, College_Name, Category, Course_Name, Rank
    # Or variations handled by prediction.py
    
    return df
