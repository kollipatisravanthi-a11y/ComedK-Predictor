import pandas as pd
import os

def clean_data(input_path, output_path):
    """
    Cleans the raw COMEDK dataset.
    
    Steps:
    1. Load data
    2. Remove duplicates
    3. Handle missing values
    4. Rename columns
    5. Save to processed folder
    """
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    df = pd.read_csv(input_path)
    
    # Example cleaning steps
    df.drop_duplicates(inplace=True)
    df.fillna(method='ffill', inplace=True) # Example strategy
    
    # Rename columns if necessary
    # df.rename(columns={'OldName': 'NewName'}, inplace=True)
    
    df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path}")

if __name__ == "__main__":
    # Example usage
    raw_file = '../data/raw/comedk_raw.csv'
    processed_file = '../data/processed/comedk_clean.csv'
    clean_data(raw_file, processed_file)
