import polars as pl

CATEGORY_MAPPING = {
    "Criminal": [r"Crl", r"Criminal", r"Bail", r"Cr\.A", r"CRA", r"Crl\.Rev", r"Cr\.M", r"IPC", r"CrPC"],
    "Service": [r"Service", r"S\.W\.P", r"W\.P\.S", r"Promotion", r"Pension", r"Selection", r"Gratuity", r"Departmental"],
    "Writ": [r"Writ", r"W\.P", r"W\.A", r"WP", r"CWP", r"Mandamus", r"Certiorari", r"Quo Warranto"],
    "Land/Property": [r"Land", r"Property", r"Revenue", r"Acquisition", r"Rent", r"Partition", r"Tenancy", r"Encroachment"],
    "Tax": [r"Tax", r"Income Tax", r"GST", r"VAT", r"Sales Tax", r"C\.M\.A", r"T\.R\.C", r"Excise", r"Customs"],
    "Constitutional": [r"Constitutional", r"PIL", r"Public Interest", r"Article 226", r"Article 227", r"Habeas Corpus"],
    "Civil": [r"Civil", r"C\.A", r"RSA", r"SFA", r"TFA", r"Suit", r"CPC", r"Injunction", r"Decree"],
    "Bail": [r"Bail", r"Anticipatory Bail", r"Regular Bail"],
    "Company": [r"Company", r"Commercial", r"Insolvency", r"Arbitration", r"O\.S", r"NCLT", r"Winding Up"]
}

def standardize_categories(df):
    """
    Standardizes case types based on title and description using rule-based mapping.
    """
    if df is None:
        return None
        
    # Combined title and description for searching
    search_cols = []
    if "title" in df.columns: search_cols.append("title")
    if "description" in df.columns: search_cols.append("description")
    
    if not search_cols:
        df = df.with_columns(pl.lit("Unknown").alias("standardized_category"))
        return df

    # Create a search column
    df = df.with_columns(
        pl.concat_str([pl.col(c).fill_null("") for c in search_cols], separator=" ").alias("search_text")
    )
    
    # Initialize category column with 'Other'
    condition = pl.lit("Other")
    
    # Apply rules in REVERSE order so that the FIRST category in the map has top priority
    # (Since each 'when' overrides the 'otherwise' which contains previous loop results)
    for cat in reversed(list(CATEGORY_MAPPING.keys())):
        patterns = CATEGORY_MAPPING[cat]
        combined_pattern = "|".join(patterns)
        condition = pl.when(pl.col("search_text").str.contains(f"(?i){combined_pattern}")) \
                      .then(pl.lit(cat)) \
                      .otherwise(condition)
                      
    df = df.with_columns(condition.alias("standardized_category"))
    
    return df
