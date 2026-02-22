import polars as pl
import json
import os

def load_court_codes(path="data/court-codes.json"):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def load_metadata(file_paths):
    """
    Loads metadata from CSV or Parquet files.
    file_paths: list of strings or single string
    """
    if isinstance(file_paths, str):
        file_paths = [file_paths]
    
    dfs = []
    for fp in file_paths:
        if not os.path.exists(fp):
            print(f"Warning: File {fp} not found.")
            continue
            
        if fp.endswith(".csv"):
            df = pl.read_csv(fp, infer_schema_length=None)
        elif fp.endswith(".parquet"):
            df = pl.read_parquet(fp)
        else:
            print(f"Unsupported file format for {fp}")
            continue
        dfs.append(df)
        
    if not dfs:
        return None
        
    return pl.concat(dfs)

def preprocess_df(df, court_codes):
    """
    Map court_code to court_name and select relevant columns.
    """
    if df is None:
        return None
        
    # Standardize column naming if possible
    # In the repo, court_code is like '9~13'
    
    if "court_code" in df.columns:
        mapping_df = pl.DataFrame({
            "court_code": list(court_codes.keys()),
            "court_name": list(court_codes.values())
        })
        df = df.join(mapping_df, on="court_code", how="left")
    
    # Fill null court_name with existing 'court' col if present
    if "court_name" in df.columns and "court" in df.columns:
        df = df.with_columns(
            pl.col("court_name").fill_null(pl.col("court"))
        )
    elif "court" in df.columns:
        df = df.rename({"court": "court_name"})
    
    # Year extraction with multiple format support
    date_col = None
    for col in ["date_of_registration", "date", "decision_date", "date_parsed"]:
        if col in df.columns:
            date_col = col
            break
            
    if date_col:
        # Attempt multiple formats
        df = df.with_columns(
            pl.coalesce([
                pl.col(date_col).str.strptime(pl.Date, format="%Y-%m-%d", strict=False),
                pl.col(date_col).str.strptime(pl.Date, format="%d-%m-%Y", strict=False),
                pl.col(date_col).str.strptime(pl.Date, format="%d/%m/%Y", strict=False),
            ]).alias("date_parsed")
        )
        # Fallback to extracting year via regex if date parsing fails
        df = df.with_columns(
            pl.col("date_parsed").dt.year().alias("filing_year")
        )
        
        # If year is still null, try extracting 4 digits from the date string
        df = df.with_columns(
            pl.when(pl.col("filing_year").is_null())
            .then(pl.col(date_col).str.extract(r"(\d{4})", 1).cast(pl.Int32))
            .otherwise(pl.col("filing_year"))
            .alias("filing_year")
        )
    
    return df
