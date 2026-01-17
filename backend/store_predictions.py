import pandas as pd
from flask import Flask, render_template, request
from sqlalchemy import create_engine, text
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import GradientBoostingRegressor
import numpy as np

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static",
)

# -------------------- DB --------------------
from backend.database import engine

# -------------------- ROUND ORDER --------------------
ROUND_ORDER = ["R1", "R2", "R3", "R4"]  # ascending order

# -------------------- GENERATE PREDICTIONS (TREND BASED) --------------------
def generate_predictions():
    print("🔄 Generating predictions using Historical Trend Analysis per Round...")

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
    """
    df = pd.read_sql(query, engine)

    if df.empty:
        print("❌ No data available")
        return

    # ---- PREPROCESS ----
    df["round"] = df["round"].astype(str).str.strip().str.upper()
    
    # ---- 1. FILTER ACTIVE COURSES ONLY (2024-2025) ----
    # Identify valid (College Code, Branch Code/Name) pairs from recent years
    # identifying by code is better if available
    
    # DEBUG: Check RV 2025 Data immediately after load
    # rv_2025_check = df[...] removed for production

    # First, let's try to extract branch code from valid rows
    # Branch codes are usually 2-3 uppercase letters at the start (e.g., "CS-...")
    df["extracted_code"] = df["branch"].astype(str).str.extract(r"^([A-Z]{2,3})[\s-]").fillna("")
    
    # Create a unique key for tracking courses: College Code + Extracted Branch Code (if exists) OR Full Branch Name
    # But Branch Name changes...
    # Let's rely on the CSV data.
    # We want to keep:
    #   Rows where (College Code, Normalized Branch) appeared in 2025.
    
    # Helper to check existence in recent years - STRICTLY 2025 as per user request
    recent_df = df[df["year"] == 2025]
    
    # We need to link old rows (2021-2023) to new rows (2025).
    # Linkage:
    #   1. Match by Branch Code (e.g. "AI" -> "AI")
    #   2. Match by exact or very similar name if code missing
    
    from backend.branches_data import engineering_branches, architecture_branches
    
    # Build a Map: Code -> Official Name
    code_to_name = {b["code"]: b["name"] for b in engineering_branches + architecture_branches}
    
    def normalize_branch(row):
        # Try to find code in the branch string
        raw_branch = str(row["branch"]).strip().replace('\r', '').replace('\n', '')
        
        # Check specific codes from our known list first to avoid false positives
        # But CSV has explicit format "XX-Name" often
        import re
        match = re.match(r"^([A-Z]{2,3})[\s-]", raw_branch)
        if match:
             code = match.group(1)
             if code in code_to_name:
                 return code, code_to_name[code]
        
        return None, raw_branch

    # Apply normalization to the whole DF
    # This might be slow, so optimize? 
    # Actually, let's just create a 'normalized_branch_name' column.
    
    # Optimization: processing unique branch names
    unique_branches = df["branch"].unique()
    branch_map = {}
    for b in unique_branches:
        code, name = normalize_branch({"branch": b})
        branch_map[b] = (code, name)

    df["temp_branch_info"] = df["branch"].map(branch_map)
    df["branch_code"] = df["temp_branch_info"].apply(lambda x: x[0])
    df["normalized_branch"] = df["temp_branch_info"].apply(lambda x: x[1])
    
    # Now, identify active branches for each college
    # Key: (College Code, Branch Code) if Code exists
    # Key: (College Code, Normalized Branch Name) if Code is None
    
    # Set of active keys from 2025
    active_keys = set()
    
    recent_data = df[df["year"] == 2025]
    for _, row in recent_data.iterrows():
        c_code = row["college_code"]
        b_code = row["branch_code"]
        b_name = row["normalized_branch"]
        
        if b_code:
            active_keys.add((c_code, "CODE", b_code))
        else:
            active_keys.add((c_code, "NAME", b_name))
            
    # Filter the main DF
    def is_active(row):
        c_code = row["college_code"]
        b_code = row["branch_code"]
        b_name = row["normalized_branch"]
        
        if b_code:
            if (c_code, "CODE", b_code) in active_keys:
                return True
        # If we didn't match by code, try by name
        if (c_code, "NAME", b_name) in active_keys:
            return True
        
        # Special Case: Old names might differ from new names even after normalization if code is missing.
        # But for Comedk, Codes are usually reliable in recent years.
        # If an old row (2021) has branch "Artificial Intelligence" and NO code, 
        # and new row (2024) has "CI-..." (Code CI), they WON'T match.
        # This is EXACTLY what we want -> Drop the old "Artificial Intelligence" because it's replaced by "CI"
        
        return False

    initial_count = len(df)
    df = df[df.apply(is_active, axis=1)]
    print(f"ℹ️ Filtered inactive branches: {initial_count} -> {len(df)} rows. (Kept only branches present in 2024/2025)")

    # Use the normalized name as the final branch name
    df["branch"] = df["normalized_branch"]

    # Unified College Names: Use the most recent year's name for each college_code
    # This prevents splitting data when a college changes its name string
    latest_names = df.sort_values("year").groupby("college_code").tail(1).set_index("college_code")["college_name"].to_dict()
    df["college_name"] = df["college_code"].map(latest_names).fillna(df["college_name"])

    df["college_name_clean"] = df["college_name"].str.strip().str.upper()
    df["branch_clean"] = df["branch"].str.strip().str.upper()
    
    # NORMALIZE CATEGORY: GM/KKR -> GM
    df["category"] = df["category"].replace("GM/KKR", "GM")
    df["category_clean"] = df["category"].str.strip().str.upper()

    # ---- EXCLUSIONS ----
    # User Request: Remove Information Science from RVCE
    mask_exclude = (
        (df["college_name"].str.contains("R.V. College of Engineering", case=False, na=False)) & 
        (df["branch"].str.contains("Information Science", case=False, na=False))
    )
    if mask_exclude.any():
        print(f"ℹ️ Excluding {mask_exclude.sum()} rows for RVCE - Information Science (Removed branch)")
        df = df[~mask_exclude]
    
    # Extract round number
    df["round_num"] = df["round"].str.extract(r"(\d+)")[0].astype(float)
    df = df.dropna(subset=["round_num", "closing_rank"])
    df["round_num"] = df["round_num"].astype(int)

    # ---- PREDICTION LOOP ----
    preds = []
    
    # Group by unique College-Branch-Category
    # We use original names for output, cleaned for grouping if needed, but grouping by code is safer if unique
    # Using code + clean names for grouping
    groups = df.groupby(["college_code", "college_name", "branch", "category"])
    
    print(f"✅ Processing {len(groups)} unique college-course-category combinations...")

    for (c_code, c_name, branch, category), group in groups:
        round_preds = {}
        
        # Get Branch Code if available in the group
        # Since we grouped by branch (which is normalized name), we need to extract code again or take from first row
        # However, we didn't group by branch_code.
        # Let's grab the code from the recent data matching this group.
        # It's safer to take the mode or first non-null branch_code from the group data.
        b_code = group["branch_code"].dropna().unique()
        branch_code_val = b_code[0] if len(b_code) > 0 else None

        # Analyze each round independently
        # We only predict rounds that have history for this specific group
        available_rounds = sorted(group["round_num"].unique())
        
        for r in available_rounds:
            hist_data = group[group["round_num"] == r].sort_values("year")
            
            years = hist_data["year"].values
            cutoffs = hist_data["closing_rank"].values
            
            if len(years) == 0:
                continue
                
            # Trend Logic
            if len(years) >= 2:
                # Simple Linear Regression: y = mx + c
                n = len(years)
                sum_x = np.sum(years)
                sum_y = np.sum(cutoffs)
                sum_xy = np.sum(years * cutoffs)
                sum_xx = np.sum(years * years)
                
                denom = (n * sum_xx - sum_x**2)
                if denom != 0:
                    slope = (n * sum_xy - sum_x * sum_y) / denom
                    intercept = (sum_y - slope * sum_x) / n
                    pred_val = slope * 2026 + intercept
                else:
                    pred_val = cutoffs[-1]
                
                # Safety: Conservative Estimation
                # If slope is positive (cutoff getting worse/easier), we dampen it significantly.
                last_val = cutoffs[-1]
                
                # Base Prediction from Regression
                base_pred = pred_val

                # 1. Slope Dampening for Increasing Ranks (easier)
                if slope > 0:
                    # If trend is projecting higher ranks (easier), restrict growth
                    max_growth = last_val * 1.25
                    if base_pred > max_growth:
                        base_pred = max_growth
                
                # 2. General Safety Bounds relative to Last Year
                # Logic:
                # - User Request: RV College CSE (and related) should be "Improved" (Easier/Higher Rank)
                # - Other Top Colleges (< 2000) should be "Stricter" (Harder/Lower Rank) - "Don't disturb"

                is_rv_cse = ("R V College" in c_name) and ("Computer Science" in branch)

                if last_val < 2000:
                    if is_rv_cse:
                        # Easier for RV CSE
                        min_val = last_val + 5
                        if base_pred < min_val:
                            base_pred = min_val
                        
                        max_safe = last_val * 1.15
                        if base_pred > max_safe: 
                            base_pred = max_safe
                    else:
                        # Stricter for other top colleges
                        target_val = last_val - 5
                        if target_val < 1: target_val = 1
                        base_pred = target_val
                   
                else:
                    # General trend for others: Cutoff increases (Easier)
                    min_val = last_val + 5
                    if base_pred < min_val:
                        base_pred = min_val
                    
                    max_safe = last_val * 1.3
                    if base_pred > max_safe:
                        base_pred = max_safe
                
                pred_val = base_pred

            else:
                # Use last known value
                is_rv_cse = "R V College of Engineering" in c_name and "Computer Science" in branch
                if is_rv_cse:
                     pred_val = cutoffs[-1] + 5
                elif cutoffs[-1] < 2000:
                     pred_val = max(1, cutoffs[-1] - 5)
                else:
                     pred_val = cutoffs[-1] + 5
                
            round_preds[r] = int(pred_val)
            
        # ---- POST-PROCESSING: ENFORCE GAPS ----
        # R1 < R2 < R3 should generally hold.
        # Ensure minimum gap significantly visible.
        
        valid_rounds = sorted(round_preds.keys())
        
        for i in range(len(valid_rounds)):
            r_curr = valid_rounds[i]
            val_curr = round_preds[r_curr]
            
            # 1. Base sanity: rank > 0
            if val_curr < 1: 
                val_curr = 1
                round_preds[r_curr] = val_curr
            
            # 2. Sequential gap
            if i > 0:
                r_prev = valid_rounds[i-1]
                val_prev = round_preds[r_prev]
                
                # Check strict order: val_curr must be > val_prev
                # Plus a 'realistic' gap.
                # e.g. 5% gap or 100 ranks, whichever is suitable.
                # For top ranks (e.g. 500), 5% is 25.
                # For mid ranks (e.g. 10000), 5% is 500.
                
                gap = max(50, int(val_prev * 0.05))
                
                if val_curr < val_prev + gap:
                    val_curr = val_prev + gap
                    round_preds[r_curr] = val_curr
        
        # Add to main list
        for r in valid_rounds:
             preds.append({
                "year": 2026,
                "round": f"R{r}",
                "college_code": c_code,
                "college_name": c_name,
                "branch": branch,
                "branch_code": branch_code_val,
                "category": category,
                "predicted_closing_rank": round_preds[r]
            })

    # ---- STORE PREDICTIONS ----
    pred_df = pd.DataFrame(preds)
    pred_df.to_sql("predictions_2026", engine, if_exists="replace", index=False)
    print("✅ Predictions stored safely")


# -------------------- FETCH USER RESULTS --------------------
def fetch_predictions(rank, category):
    sql = text("""
        SELECT
            college_name,
            branch,
            round,
            predicted_closing_rank
        FROM predictions_2026
        WHERE category = :category
          AND predicted_closing_rank >= :rank
    """)

    df = pd.read_sql_query(sql, engine, params={
        "rank": rank,
        "category": category
    })

    if df.empty:
        return []

    # sort by round ascending: R1 first
    df["round_num"] = df["round"].str.extract(r"R\s*0*(\d+)")[0].astype(int)
    df.sort_values(["college_name", "branch", "round_num"], inplace=True)
    df.drop_duplicates(subset=["college_name", "branch"], keep="first", inplace=True)
    df.sort_values("predicted_closing_rank", inplace=True)

    return df.to_dict(orient="records")


# -------------------- ROUTE --------------------
@app.route("/", methods=["GET", "POST"])
def predictor():
    results = None
    error = None

    if request.method == "POST":
        try:
            rank = int(request.form["rank"])
            category = request.form["category"]
            results = fetch_predictions(rank, category)
        except Exception:
            error = "Invalid input"

    return render_template("index.html", results=results, error=error)


# -------------------- MAIN --------------------
if __name__ == "__main__":
    generate_predictions()
    app.run(debug=True)









