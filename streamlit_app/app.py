import streamlit as st
import pandas as pd
import plotly.express as px
import joblib

# --- PAGE CONFIG ---
st.set_page_config(page_title="HDB Resale Price Insights", layout="wide")

# --- HERO SECTION ---
banner_path = "assets/banner2.png"

st.markdown(f"""
    <style>
    .hero-container {{
        position: relative;
        width: 100%;
        height: 260px;
        background-image: url("{banner_path}");
        background-size: cover;
        background-position: center;
        border-radius: 12px;
        margin-bottom: 30px;
    }}
    .hero-overlay {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.35);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        color: white;
        text-align: center;
        font-family: 'Helvetica', sans-serif;
    }}
    .hero-overlay h1 {{
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }}
    .hero-overlay p {{
        font-size: 18px;
        font-weight: 300;
        margin: 0;
        letter-spacing: 0.5px;
    }}
    </style>

    <div class="hero-container">
        <div class="hero-overlay">
            <h1>WOW! Real Estate</h1>
            <p>Where Data Meets Real Estate Decisions</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
df = pd.read_csv("HDB_dummies.csv")

# --- LOAD TRAINED MODEL PIPELINE ---
model = joblib.load("hdb_pipeline.joblib")  # unified pipeline (handles encoding internally)

# --- SIDEBAR FILTERS ---
st.sidebar.header("🏘 Property Filters")

flat_type = st.sidebar.selectbox("Flat Type:", [
    "1 ROOM", "2 ROOM", "3 ROOM", "4 ROOM", "5 ROOM", "EXECUTIVE", "MULTI-GENERATION"
])

storey_range = st.sidebar.selectbox("Storey Range:", [
    "Low (1-6)", "Mid (7-12)", "High (13-18)", "Very High (19-30)", "Ultra High (31+)"
])

planning_area = st.sidebar.selectbox("Planning Area:", [
    "Ang Mo Kio", "Bedok", "Bishan", "Bukit Batok", "Bukit Merah",
    "Bukit Panjang", "Bukit Timah", "Changi", "Choa Chu Kang", "Clementi",
    "Downtown Core", "Geylang", "Hougang", "Jurong East", "Jurong West",
    "Kallang", "Marine Parade", "Novena", "Outram", "Pasir Ris",
    "Punggol", "Queenstown", "Rochor", "Sembawang", "Sengkang",
    "Serangoon", "Tampines", "Tanglin", "Toa Payoh", "Western Water Catchment",
    "Woodlands", "Yishun"
])

floor_area = st.sidebar.slider("Floor Area (sqft)", 300, 2000, 1000)
hdb_age = st.sidebar.slider("HDB Age (years)", 0, 60, 25)

# --- BUILD INPUT DATAFRAME ---
input_data = pd.DataFrame({
    "flat_type": [flat_type],
    "storey_range": [storey_range],
    "planning_area": [planning_area],
    "floor_area_sqft": [floor_area],
    "hdb_age": [hdb_age]
})

# --- PREDICT PRICE ---
if st.sidebar.button("Predict Resale Price"):
    predicted_price = model.predict(input_data)[0]
    st.sidebar.metric(label="Predicted Resale Price (SGD)", value=f"${predicted_price:,.0f}")

# --- FILTER DATAFRAME FOR SNAPSHOT ---
filtered_df = df[
    (df["flat_type"] == flat_type) &
    (df["planning_area"] == planning_area)
]

# --- HANDLE CASE WHEN FILTERED DATA IS EMPTY ---
if filtered_df.empty:
    st.warning("No records found for the selected filters. Please try another combination.")
else:
    # --- MARKET SNAPSHOT ---
    st.markdown("### 📊 Market Snapshot")

    total_records = len(filtered_df)
    median_price = filtered_df["resale_price"].median()
    avg_floor_area = filtered_df["floor_area_sqft"].mean()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🌆 Planning Area", planning_area)
    col2.metric("🏠 Flat Type", flat_type)
    col3.metric("🏢 Total Records", f"{total_records:,}")
    col4.metric("💵 Median Price", f"${median_price:,.0f}")
    col5.metric("📈 Avg Floor Area", f"{avg_floor_area:,.0f} sqft")

    st.markdown("---")

    # --- CHARTS ---
    colA, colB = st.columns(2)
    with colA:
        fig1 = px.histogram(filtered_df, x="resale_price", nbins=25,
                            title="Distribution of Resale Prices (SGD)",
                            color_discrete_sequence=["#0072B2"])
        st.plotly_chart(fig1, use_container_width=True)

    with colB:
        fig2 = px.scatter(filtered_df, x="hdb_age", y="resale_price",
                          title="Resale Price vs HDB Age",
                          color_discrete_sequence=["#D55E00"],
                          opacity=0.7)
        st.plotly_chart(fig2, use_container_width=True)

# --- FOOTER ---
st.markdown("""
<div style="text-align:center; padding-top:20px; font-size:13px; color:gray;">
Built by SHYE GROUP using Streamlit · © 2025 WOW! Real Estate
</div>
""", unsafe_allow_html=True)
