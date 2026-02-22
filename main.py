import sys
import os
import polars as pl

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from legal_culture_metadata.loader import load_metadata, preprocess_df, load_court_codes
from legal_culture_metadata.category_standardizer import standardize_categories
from legal_culture_metadata.court_aggregator import aggregate_court_data, compute_yearly_trend
from legal_culture_metadata.similarity_engine import compute_similarity
from legal_culture_metadata.report_generator import export_reports

def run_pipeline(input_path):
    print(f"--- Regional Legal Culture Analysis Engine ---")
    print(f"Target: {input_path}")
    
    # 1. Load data and codes
    court_codes = load_court_codes()
    df_raw = load_metadata(input_path)
    
    if df_raw is None:
        print("Error: No data loaded.")
        return

    # 2. Preprocess
    print("[1/6] Preprocessing metadata...")
    df = preprocess_df(df_raw, court_codes)
    
    # 3. Standardize Categories
    print("[2/6] Mapping case types to standardized categories...")
    df = standardize_categories(df)
    
    # 4. Aggregate
    print("[3/6] Computing court-level distributions and entropy...")
    stats, matrix = aggregate_court_data(df)
    
    # 5. Yearly Trend
    print("[4/6] Analyzing year-wise trends...")
    trend_df = compute_yearly_trend(df)
    
    # 6. Similarity and Clustering
    print("[5/6] Computing litigation similarity clusters...")
    sim_df, matrix_updated = compute_similarity(matrix)
    
    # 7. Export Reports
    print("[6/6] Generating reports and JSON profiles...")
    export_reports(matrix_updated, sim_df, trend_df=trend_df)
    
    print("\n✓ Pipeline execution successful.")

def generate_demo_data():
    """Generates realistic dummy data for Punjab & Haryana and Madras High Courts."""
    print("Generating demo metadata with varied formats...")
    # 3~22: Punjab & Haryana, 33~10: Madras
    data = [
        {"court_code": "3~22", "title": "Service Writ Petition No. 500/2021", "description": "Promotion case", "date_of_registration": "2021-05-15"},
        {"court_code": "3~22", "title": "Crl.A. No. 10/2022", "description": "Theft appeal", "date_of_registration": "10-01-2022"},
        {"court_code": "33~10", "title": "W.P. 123/2020", "description": "Mandamus petition", "date_of_registration": "20/12/2020"},
        {"court_code": "24~17", "title": "Tax Appeal 1/2023", "description": "GST dispute", "date_of_registration": "2023/04/01"},
        {"court_code": "28~2", "title": "Land Case", "description": "Revenue matter", "date_of_registration": "Not Available (2022)"}, # Test regex extractor
        {"court_code": "3~22", "title": "Bail Application 99/2021", "description": "Accused seeking bail", "date_of_registration": "2021-12-01"},
    ]
    # Multiply to simulate volume
    data = data * 50
    df = pl.DataFrame(data)
    
    if not os.path.exists("data"):
        os.makedirs("data")
    df.write_csv("data/metadata.csv")
    print("Demo data saved to data/metadata.csv")

if __name__ == "__main__":
    # Check for input
    # Prioritize Parquet as per requirement
    input_file = None
    if os.path.exists("opendata/metadata.parquet"):
        input_file = "opendata/metadata.parquet"
    elif os.path.exists("data/metadata.csv"):
        input_file = "data/metadata.csv"
    
    if not input_file:
        generate_demo_data()
        input_file = "data/metadata.csv"
        
    run_pipeline(input_file)
