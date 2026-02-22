import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# Set page config
st.set_page_config(
    page_title="Regional Legal Culture Engine",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for premium look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .personality-card {
        padding: 20px;
        border-radius: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_name=True)

# Load Data
@st.cache_data
def load_data():
    output_dir = "output"
    matrix = pd.read_csv(os.path.join(output_dir, "court_topic_matrix.csv"))
    trends = pd.read_csv(os.path.join(output_dir, "yearly_trends.csv"))
    with open(os.path.join(output_dir, "litigation_personality.json"), "r") as f:
        personality = json.load(f)
    return matrix, trends, personality

def main():
    st.sidebar.title("⚖️ Legal Culture Engine")
    st.sidebar.markdown("---")
    
    if not os.path.exists("output/court_topic_matrix.csv"):
        st.error("Engine outputs not found. Please run the analysis pipeline first.")
        if st.button("Run Analysis Pipeline"):
            with st.spinner("Executing Metadata Pipeline..."):
                import subprocess
                subprocess.run(["python", "main.py"])
                st.rerun()
        return

    matrix, trends, personality = load_data()
    
    menu = ["Dashboard Overview", "Court Profiles", "Comparative Analytics", "Temporal Trends"]
    choice = st.sidebar.radio("Navigation", menu)

    if choice == "Dashboard Overview":
        st.title("🏛️ Regional Legal Culture Dashboard")
        st.markdown("### Mapping the Sociological Thumbprint of Indian High Courts")
        
        # Metric Rows
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Courts Analyzed", len(matrix))
        
        # Most common personality
        common_personality = matrix['Personality'].mode()[0]
        col2.metric("Dominant Culture", common_personality)
        
        avg_entropy = matrix['Entropy'].mean()
        col3.metric("Avg Litigation Diversity", f"{avg_entropy:.2f}")
        
        col4.metric("Data Range", "2008 - 2025")

        st.markdown("---")
        
        # Overview Distribution
        st.subheader("Distribution of Litigation Personalities Across Regions")
        fig_pie = px.sunburst(
            matrix, 
            path=['Personality', 'court_name'], 
            values='Entropy',
            color='Personality',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    elif choice == "Court Profiles":
        st.title("👤 High Court Personality Profiles")
        
        selected_court = st.selectbox("Select a High Court", matrix['court_name'].unique())
        
        court_data = matrix[matrix['court_name'] == selected_court].iloc[0]
        p_data = personality[selected_court]
        
        # Personality Card
        st.markdown(f"""
            <div class="personality-card">
                <h2>{selected_court}</h2>
                <h3>Persona: {court_data['Personality']}</h3>
                <p>Entropy (Litigation Diversity): {court_data['Entropy']:.2f}</p>
                <p>Primary Drivers: {court_data['Dominant_Categories']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Radar Chart for Court Categories
        cols = [c for c in matrix.columns if c not in ['court_name', 'Entropy', 'Dominant_Categories', 'Personality', 'Cluster']]
        values = [p_data[c] for c in cols]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=cols,
            fill='toself',
            name=selected_court,
            line_color='#764ba2'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            title=f"Litigation Composition: {selected_court}"
        )
        st.plotly_chart(fig, use_container_width=True)

    elif choice == "Comparative Analytics":
        st.title("📊 Regional Comparative Analytics")
        
        # Heatmap
        st.subheader("Category-wise Percentage Heatmap")
        plot_df = matrix.set_index('court_name')
        cols = [c for c in matrix.columns if c not in ['court_name', 'Entropy', 'Dominant_Categories', 'Personality', 'Cluster']]
        
        fig_heat = px.imshow(
            plot_df[cols],
            labels=dict(x="Category", y="Court", color="Percentage"),
            color_continuous_scale="Viridis",
            aspect="auto"
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        
        # Diversity Bar Chart
        st.subheader("Litigation Diversity (Entropy) by Court")
        fig_bar = px.bar(
            matrix.sort_values('Entropy', ascending=False),
            x='court_name',
            y='Entropy',
            color='Personality',
            title="Diversity of Practice Areas"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    elif choice == "Temporal Trends":
        st.title("📈 Temporal Litigation Evolution")
        
        selected_courts = st.multiselect("Select Courts to Compare", trends['court_name'].unique(), default=[trends['court_name'].unique()[0]])
        
        if selected_courts:
            trend_subset = trends[trends['court_name'].isin(selected_courts)]
            
            fig_line = px.line(
                trend_subset,
                x='filing_year',
                y='count',
                color='standardized_category',
                line_group='court_name',
                symbol='court_name',
                markers=True,
                title="Trend of Case Categories Over Time"
            )
            fig_line.update_xaxes(type='category')
            st.plotly_chart(fig_line, use_container_width=True)
            
            st.info("Note: Sample demo data may show simplified trends. Full dataset analysis reveals long-term shifts in judicial priorities.")

if __name__ == "__main__":
    main()
