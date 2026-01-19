import pandas as pd
import os

codes = ['E018', 'E057', 'E072', 'E086', 'E087', 'E149', 'E162', 'E174', 'E177', 'E182', 'E185', 'E186', 'E210']
csv_path = 'data/processed/COMEDK_MASTER_2021_2025.csv'

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    mapping = df[df['college_code'].isin(codes)][['college_code', 'college_name']].drop_duplicates()
    res = {}
    for _, row in mapping.iterrows():
        res[row['college_code']] = row['college_name']
    
    # Print in a very structured way so I don't miss anything
    for code in sorted(codes):
        print(f"FOUNDCODE:{code}||{res.get(code, 'Unknown')}")
else:
    print(f"CSV not found at {csv_path}")
