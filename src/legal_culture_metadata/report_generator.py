import polars as pl
import json
import os

def export_reports(matrix_df, sim_df, output_dir="output", trend_df=None):
    """
    Outputs final CSV, JSON and Markdown summaries.
    """
    if matrix_df is None:
        print("No data to export.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # 1. Court Topic Matrix (Heatmap-ready CSV)
    matrix_df.write_csv(os.path.join(output_dir, "court_topic_matrix.csv"))
    
    # 2. Similarity Matrix
    if sim_df is not None:
        sim_df.write_csv(os.path.join(output_dir, "similarity_matrix.csv"))

    # 3. Yearly Trends
    if trend_df is not None:
        trend_df.write_csv(os.path.join(output_dir, "yearly_trends.csv"))
    
    # 3. Litigation Personality JSON
    personality_dict = {}
    # Use standard python types for JSON serialization
    for row in matrix_df.iter_rows(named=True):
        court = row["court_name"]
        personality_dict[court] = {
            cat: round(row[cat], 2) for cat in matrix_df.columns if cat not in ["court_name", "Entropy", "Dominant_Categories", "Personality", "Cluster"]
        }
        personality_dict[court]["Entropy"] = round(row["Entropy"], 2)
        personality_dict[court]["Personality"] = row["Personality"]
        if "Cluster" in row:
            personality_dict[court]["Cluster"] = int(row["Cluster"])
        
    with open(os.path.join(output_dir, "litigation_personality.json"), "w") as f:
        json.dump(personality_dict, f, indent=4)
        
    # 4. Markdown Summary Report
    with open(os.path.join(output_dir, "summary_report.md"), "w") as f:
        f.write("# Mapping Regional Legal Culture\n")
        f.write("## Computational Analysis of Indian High Courts (2008–2025)\n\n")
        
        f.write("### Court-wise Profiles\n")
        f.write("| Court | Dominant Category | Personality | Entropy |\n")
        f.write("|-------|-------------------|-------------|---------|\n")
        for row in matrix_df.sort("court_name").iter_rows(named=True):
            f.write(f"| {row['court_name']} | {row['Dominant_Categories'].split(';')[0]} | {row['Personality']} | {row['Entropy']:.2f} |\n")
        
        if "Cluster" in matrix_df.columns:
            f.write("\n### Similarity Clusters\n")
            for cluster_id in sorted(matrix_df["Cluster"].unique()):
                cluster_courts = matrix_df.filter(pl.col("Cluster") == cluster_id)["court_name"].to_list()
                f.write(f"- **Group {cluster_id}**: {', '.join(cluster_courts)}\n")

    print(f"Academic report and data artifacts generated in {output_dir}/")
