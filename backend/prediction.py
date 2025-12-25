import pandas as pd
import os

class CollegePredictor:
    def __init__(self, data_path=None):
        if data_path is None:
            # Resolve path relative to this script file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_path = os.path.join(base_dir, '..', 'data', 'raw', 'comedk_data.csv')
        else:
            self.data_path = data_path
            
        self.df = None
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_path):
            try:
                self.df = pd.read_csv(self.data_path)
                # Ensure columns are standardized
                self.df.columns = [c.strip().lower() for c in self.df.columns]
            except Exception as e:
                print(f"Error loading data: {e}")
                self.df = pd.DataFrame()
        else:
            print(f"Data file not found at {self.data_path}")
            self.df = pd.DataFrame()

    def predict(self, rank, branch_code, category='GM'):
        if self.df.empty:
            # Fallback for demo if no data exists
            return []

        try:
            rank = int(rank)
        except ValueError:
            return []

        filtered_df = self.df.copy()
        
        # Flexible column matching
        col_map = {
            'college': ['college', 'college_name', 'institute'],
            'branch': ['branch', 'course', 'branch_code', 'course_code'],
            'category': ['category', 'cat'],
            'rank': ['rank', 'cutoff', 'closing_rank', 'cutoff_rank']
        }
        
        actual_cols = {}
        for key, candidates in col_map.items():
            for c in candidates:
                if c in filtered_df.columns:
                    actual_cols[key] = c
                    break
        
        if len(actual_cols) < 3:
            print(f"Missing required columns in dataset. Found: {actual_cols}")
            return []

        # Filter by Branch
        if branch_code:
            if isinstance(branch_code, list):
                # Create a regex pattern to match any of the selected branches
                # e.g., if branch_code=['CS', 'EC'], pattern='CS|EC'
                pattern = '|'.join(branch_code)
                filtered_df = filtered_df[filtered_df[actual_cols['branch']].astype(str).str.contains(pattern, case=False, na=False)]
            else:
                filtered_df = filtered_df[filtered_df[actual_cols['branch']].astype(str).str.contains(branch_code, case=False, na=False)]

        # Filter by Category
        if category and 'category' in actual_cols:
             filtered_df = filtered_df[filtered_df[actual_cols['category']].astype(str).str.contains(category, case=False, na=False)]

        # Filter by Rank (Cutoff >= User Rank)
        filtered_df[actual_cols['rank']] = pd.to_numeric(filtered_df[actual_cols['rank']], errors='coerce')
        filtered_df = filtered_df.dropna(subset=[actual_cols['rank']])
        
        eligible_df = filtered_df[filtered_df[actual_cols['rank']] >= rank]
        eligible_df = eligible_df.sort_values(by=actual_cols['rank'])
        
        results = []
        for _, row in eligible_df.iterrows():
            results.append({
                'college': row[actual_cols['college']],
                'branch': row[actual_cols['branch']],
                'cutoff': int(row[actual_cols['rank']]),
                'location': 'Karnataka' 
            })
            
        return results

# Singleton instance
predictor = CollegePredictor()

def predict_colleges(rank, branch, category='GM'):
    return predictor.predict(rank, branch, category)
