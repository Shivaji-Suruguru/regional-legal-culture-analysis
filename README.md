# Regional Legal Culture Analysis Engine

## Overview
**Title**: *Mapping Regional Legal Culture through Metadata-Driven Computational Analysis of Indian High Courts (2008–2025)*

The **Regional Legal Culture Analysis Engine** is a specialized computational law tool designed to analyze the "litigation personality" of different Indian High Courts. Using only structured metadata, the engine identifies dominant legal patterns, computes cultural diversity in litigation via Shannon Entropy, and clusters courts based on their sociological similarities.

This project is built for high-performance processing using **Polars** and is designed to work with the metadata extracted from the [Indian High Court Judgments Dataset](https://github.com/vanga/indian-high-court-judgments).

---

## 🚀 Key Features

### 1. Court-Level Litigation Personality
Automatically identifies the "personality" of a High Court based on case distributions:
- **Administrative-Heavy**: High volume of Writ petitions (Article 226/227).
- **Service-Law Dominant**: Heavy focus on government employment, pension, and promotion disputes.
- **Land-Conflict Dominant**: Preponderance of land acquisition and property disputes.
- **Revenue-Focused**: Tax and commercial litigation heavy.

### 2. Advanced Metadata Analytics
- **Shannon Entropy Scoring**: Measures how diversified or specialized a court's litigation culture is.
- **Yearly Trend Analysis**: Tracks the evolution of case categories from 2008 to 2025.
- **Similarity Clustering**: Uses Cosine Similarity and K-Means clustering to group courts with similar "sociological thumbprints."

### 3. High-Performance Architecture
- **Memory Efficient**: Uses columnar processing via Polars/DuckDB; supports 10M+ rows without high RAM overhead.
- **Robust Category Mapping**: Uses rule-based regex to standardize thousands of varied case types into unified buckets.
- **Flexible Date Parsing**: Multi-format support with regex-based year extraction fallbacks.

---

## 📁 Project Structure

- `src/legal_culture_metadata/`
  - `loader.py`: Handles CSV/Parquet ingestion and court mapping.
  - `category_standardizer.py`: Normalizes case types into master buckets.
  - `court_aggregator.py`: Groups data and computes entropy/stats.
  - `similarity_engine.py`: Performs clustering and similarity matrix computation.
  - `report_generator.py`: Generates academic and machine-readable exports.
- `main.py`: The central pipeline controller and demo generator.
- `data/court-codes.json`: Mapping of internal court codes to official names.

---

## 📊 Use Cases

- **Academic Research**: Quantitatively compare the legal cultures of different Indian states.
- **Policy Planning**: Identify regions with excessive land or service litigation to inform judicial reforms.
- **Legal Analytics**: Predict the "vibe" of a court for strategic litigation planning.
- **Data Engineering**: A blueprint for building fast, memory-safe analytics engines on large-scale legal datasets.

---

## 🛠️ Installation & Usage

### Prerequisites
- Python 3.8+
- Recommended: `polars`, `numpy`, `scikit-learn`

### Setup
```bash
pip install -r requirements.txt
```

### Running the Dashboard (New!)
Launch the interactive visualization dashboard:
```bash
streamlit run app.py
```

### Running the Backend Engine
1. Place your metadata (CSV or Parquet) in the `data/` or `opendata/` directory.
2. Run the pipeline:
   ```bash
    python main.py
   ```
3. If no data is found, the engine will automatically generate **Demo Data** to show the analysis in action.

---

## 📈 Output Artifacts
The engine saves all results to the `output/` folder:
- `summary_report.md`: A human-readable academic summary.
- `litigation_personality.json`: Detailed JSON profiles for every court.
- `court_topic_matrix.csv`: Percentage distributions for heatmaps.
- `similarity_matrix.csv`: Mathematical similarity scores between states.
- `yearly_trends.csv`: Year-over-year category shifts.

---

## ⚖️ License & Reproducibility
Designed for academic reproducibility. Use only metadata outputs (CSV/Parquet) from `process_metadata.py` or `opendata_parquet.py`. 
**Do not process raw PDFs.**
