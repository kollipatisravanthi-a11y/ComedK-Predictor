import pandas as pd
import os

from backend.utils import load_comedk_data

class CollegePredictor:
    def __init__(self, data_path=None):
        # Resolve path relative to this script file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.df = load_comedk_data(base_dir)
        # Standardize columns to lowercase
        if not self.df.empty:
            self.df.columns = [c.strip().lower() for c in self.df.columns]

    def load_data(self):
        # Deprecated, logic moved to utils.py but kept for compatibility if called explicitly
        pass

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
            'branch': ['branch', 'course', 'branch_code', 'course_code', 'course_name'],
            'category': ['category', 'cat'],
            'rank': ['rank', 'cutoff', 'closing_rank', 'cutoff_rank'],
            'round': ['round', 'round_name'],
            'year': ['year', 'academic_year']
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
                # Use word boundaries to avoid partial matches (e.g. 'CS' in 'Robotics')
                pattern = r'\b(' + '|'.join(branch_code) + r')\b'
                filtered_df = filtered_df[filtered_df[actual_cols['branch']].astype(str).str.contains(pattern, case=False, na=False, regex=True)]
            else:
                pattern = r'\b' + branch_code + r'\b'
                filtered_df = filtered_df[filtered_df[actual_cols['branch']].astype(str).str.contains(pattern, case=False, na=False, regex=True)]

        # Filter by Category
        if category and 'category' in actual_cols:
             filtered_df = filtered_df[filtered_df[actual_cols['category']].astype(str).str.contains(category, case=False, na=False)]

        # Filter by Rank (Cutoff >= User Rank)
        filtered_df[actual_cols['rank']] = pd.to_numeric(filtered_df[actual_cols['rank']], errors='coerce')
        filtered_df = filtered_df.dropna(subset=[actual_cols['rank']])
        
        eligible_df = filtered_df[filtered_df[actual_cols['rank']] >= rank]
        
        # Sort by Cutoff Rank (Ascending) - Best colleges (closest to rank) first
        eligible_df = eligible_df.sort_values(by=actual_cols['rank'], ascending=True)
        
        # Avoid duplicates (College + Branch combination)
        # Keep the one with the lowest cutoff rank (closest to user rank) as per sorting above
        eligible_df = eligible_df.drop_duplicates(subset=[actual_cols['college'], actual_cols['branch']], keep='first')
        
        # Get Top 10 colleges for EACH branch
        # This ensures that if the user selected multiple branches (e.g. CS, EC),
        # they get the best options for CS AND the best options for EC, 
        # rather than just the global top 10 which might be dominated by one branch.
        # eligible_df = eligible_df.groupby(actual_cols['branch']).head(10)
        
        # Sort the final combined list by rank again for display
        eligible_df = eligible_df.sort_values(by=actual_cols['rank'], ascending=True)
        
        results = []
        for _, row in eligible_df.iterrows():
            item = {
                'college': row[actual_cols['college']],
                'branch': row[actual_cols['branch']],
                'cutoff': int(row[actual_cols['rank']]),
                'location': 'Karnataka' 
            }
            if 'round' in actual_cols:
                item['round'] = row[actual_cols['round']]
            if 'year' in actual_cols:
                item['year'] = row[actual_cols['year']]
            results.append(item)
            
        return results

    def get_courses_by_college(self, college_code):
        if self.df.empty:
            return []
            
        # Filter by college code
        # Assuming 'college_code' column exists or we map it
        col_map = {
            'college_code': ['college_code', 'code', 'institute_code'],
            'branch': ['branch', 'course', 'branch_code', 'course_code', 'course_name'],
            'rank': ['rank', 'cutoff', 'closing_rank', 'cutoff_rank']
        }
        
        actual_cols = {}
        for key, candidates in col_map.items():
            for c in candidates:
                if c in self.df.columns:
                    actual_cols[key] = c
                    break
                    
        if 'college_code' not in actual_cols:
            return []
            
        college_df = self.df[self.df[actual_cols['college_code']] == college_code]
        
        if college_df.empty:
            return []
            
        # Get unique branches
        # We want to show the branch name and maybe the latest cutoff if available
        # Let's just list the available branches for now
        
        courses = []
        if 'branch' in actual_cols:
            unique_branches = college_df[actual_cols['branch']].unique()
            for branch in unique_branches:
                # Find the latest cutoff for this branch if possible
                branch_data = college_df[college_df[actual_cols['branch']] == branch]
                
                # Try to get the lowest cutoff (most competitive) to show as reference
                cutoff = "N/A"
                if 'rank' in actual_cols:
                    try:
                        min_rank = branch_data[actual_cols['rank']].min()
                        cutoff = int(min_rank)
                    except:
                        pass
                
                courses.append({
                    'name': branch,
                    'cutoff': cutoff
                })
                
        return courses

# Singleton instance
predictor = CollegePredictor()

def predict_colleges(rank, branch, category='GM'):
    return predictor.predict(rank, branch, category)

def get_college_courses(college_code):
    return predictor.get_courses_by_college(college_code)
