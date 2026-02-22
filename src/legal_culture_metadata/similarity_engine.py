import polars as pl
import numpy as np
try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

def compute_similarity(matrix_df):
    """
    Compute cosine similarity between courts and cluster them.
    """
    if matrix_df is None:
        return None, None
        
    if not SKLEARN_AVAILABLE:
        print("Scikit-learn not installed. Skipping similarity and clustering.")
        return None, matrix_df

    # Features: category percentages
    features = [c for c in matrix_df.columns if c not in ["court_name", "Entropy", "Dominant_Categories", "Personality", "Cluster"]]
    X = matrix_df.select(features).to_numpy()
    names = matrix_df["court_name"].to_list()
    
    # 1. Similarity Matrix
    sim_matrix = cosine_similarity(X)
    sim_df = pl.DataFrame(sim_matrix, schema=names)
    sim_df = sim_df.insert_column(0, pl.Series("court_name", names))
    
    # 2. Clustering (K-Means)
    n_clusters = min(4, len(names))
    if n_clusters > 1:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X)
        matrix_df = matrix_df.with_columns(
            pl.Series("Cluster", [int(c) for c in clusters])
        )
    else:
        matrix_df = matrix_df.with_columns(pl.lit(0).alias("Cluster"))
        
    return sim_df, matrix_df
