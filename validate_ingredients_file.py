import pandas as pd

def validate_ingredients_csv(csv_path="ingredients.csv"):
    """
    Validate the structure and content of the ingredients CSV.
    Returns a list of issues found (empty if everything looks good).
    """
    issues = []
    
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return [f"❌ Could not read CSV: {e}"]
    
    # Required columns
    required_cols = ["name", "protein_per_100g", "calories_per_100g"]
    for col in required_cols:
        if col not in df.columns:
            issues.append(f"❌ Missing required column: '{col}'")
    
    if "name" in df.columns:
        # Empty or duplicate names
        if df["name"].isnull().any():
            issues.append("⚠️ Some ingredients have no name.")
        duplicates = df["name"][df["name"].duplicated()].unique()
        if len(duplicates) > 0:
            issues.append(f"⚠️ Duplicate ingredient names found: {', '.join(duplicates)}")
    
    # Check numeric values
    for col in ["protein_per_100g", "calories_per_100g", "weight_per_unit"]:
        if col in df.columns:
            bad_values = df[~df[col].apply(lambda x: str(x).replace('.', '', 1).isdigit() or pd.isna(x))]
            if not bad_values.empty:
                issues.append(f"⚠️ Column '{col}' contains non-numeric values.")
            
            if df[col].dtype != "O":  # only check if numeric
                negatives = df[df[col] < 0]
                if not negatives.empty:
                    issues.append(f"⚠️ Column '{col}' contains negative values.")
        
    if "measurement_unit" in df.columns and "weight_per_unit" in df.columns:
        # allowed units that don't require weight_per_unit
        base_units = {"g", "ml", "g/ml", None}
        
        mismatches = df[
            (~df["measurement_unit"].isin(base_units)) &  # requires weight_per_unit
            (df["weight_per_unit"].isnull() | (df["weight_per_unit"] == ""))  # but missing
        ]
        if not mismatches.empty:
            rows = [f"row {i} ({row['name']})" if "name" in df.columns else f"row {i}" 
                    for i, row in mismatches.iterrows()]
            issues.append("⚠️ Some rows have 'measurement_unit' without 'weight_per_unit' (or vice versa): " 
                        + "\n ".join(rows))
        if not issues:
            return ["✅ No issues found. CSV looks good!"]
        return issues

problems = validate_ingredients_csv("configuration/ingredients.csv")
for p in problems:
    print(p)
