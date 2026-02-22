import polars as pl
import numpy as np

def compute_entropy(probs):
    """
    Shannon Entropy to measure diversity of litigation.
    """
    probs = probs[probs > 0]
    if len(probs) == 0:
        return 0.0
    return -np.sum(probs * np.log2(probs))

def aggregate_court_data(df):
    """
    Group by court and compute distribution.
    """
    if df is None:
        return None, None
        
    # Ensure we have court names
    df = df.filter(pl.col("court_name").is_not_null())
    
    # 1. Distribution stats
    court_stats = df.group_by(["court_name", "standardized_category"]).agg(
        pl.len().alias("count")
    )
    
    court_totals = df.group_by("court_name").agg(
        pl.len().alias("total_cases")
    )
    
    stats = court_stats.join(court_totals, on="court_name")
    stats = stats.with_columns(
        (pl.col("count") / pl.col("total_cases") * 100).alias("percentage")
    )
    
    # 2. Wide matrix for similarity engine
    matrix = stats.pivot(on="standardized_category", index="court_name", values="percentage").fill_null(0)
    
    # 3. Compute Entropy and Dominant Categories
    categories = [c for c in matrix.columns if c != "court_name"]
    
    entropy_list = []
    top_cats_list = []
    
    for row in matrix.select(categories).iter_rows():
        vals = np.array(row) / 100.0
        entropy_list.append(compute_entropy(vals))
        
        # Get top 3 categories
        cat_vals = list(zip(categories, row))
        sorted_cats = sorted(cat_vals, key=lambda x: x[1], reverse=True)
        top_3 = [f"{c} ({v:.1f}%)" for c, v in sorted_cats[:3]]
        top_cats_list.append("; ".join(top_3))
        
    matrix = matrix.with_columns([
        pl.Series("Entropy", entropy_list),
        pl.Series("Dominant_Categories", top_cats_list)
    ])
    
    # Personality assignment
    matrix = generate_personality(matrix)
    
    return stats, matrix

def compute_yearly_trend(df):
    """
    Compute Court x Year x Category distribution.
    """
    if "filing_year" not in df.columns:
        return None
        
    trend = df.group_by(["court_name", "filing_year", "standardized_category"]).agg(
        pl.len().alias("count")
    ).sort(["court_name", "filing_year", "count"], descending=[False, False, True])
    
    return trend

def generate_personality(matrix):
    """
    Rule-based labeling of litigation personality.
    """
    categories = [c for c in matrix.columns if c not in ["court_name", "Entropy", "Dominant_Categories"]]
    
    personalities = []
    for row in matrix.iter_rows(named=True):
        # Find max category
        max_cat = "Other"
        max_val = -1
        for cat in categories:
            if row[cat] > max_val:
                max_val = row[cat]
                max_cat = cat
        
        if max_cat == "Service":
            label = "Service-Law Dominant"
        elif max_cat == "Criminal":
            label = "Criminal-Dominant"
        elif max_cat == "Land/Property":
            label = "Land-Conflict Dominant"
        elif max_cat == "Writ":
            label = "Administrative-Heavy"
        elif max_cat == "Tax":
            label = "Revenue-Focused"
        else:
            label = f"{max_cat}-Heavy"
            
        personalities.append(label)
        
    return matrix.with_columns(pl.Series("Personality", personalities))
