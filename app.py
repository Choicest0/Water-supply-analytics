import pandas as pd
import requests
import streamlit as st

# 1. Configure Streamlit Page
st.set_page_config(
    page_title="Regional Water Telemetry",
    page_icon="🌊",
    layout="wide"
)

# 2. Inject External CSS File
def load_css(file_name: str):
    with open(file_name, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    load_css("style.css")
except FileNotFoundError:
    pass

# 3. Fetch Data from Flask Backend API
API_URL = "http://127.0.0.1:5000/api/telemetry"

def fetch_telemetry_data() -> pd.DataFrame:
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            json_data = response.json()
            return pd.DataFrame(json_data["data"])
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Unable to connect to Flask Backend API. Ensure `backend.py` is running on port 5000!")
    return pd.DataFrame()

# 4. Header Section
st.title("🌊 Water Analytics Telemetry Dashboard")
st.caption("Real-time telemetry and field action directive engine (Pure Python Architecture)")

col_btn1, col_btn2 = st.columns([1, 5])
with col_btn1:
    refresh_clicked = st.button("🔄 Refresh Stream", type="primary")

# Load data on load or button refresh
if "telemetry_df" not in st.session_state or refresh_clicked:
    st.session_state.telemetry_df = fetch_telemetry_data()

df = st.session_state.telemetry_df

if not df.empty:
    # 5. Summary Metrics Row
    total_nodes = len(df)
    safe_nodes = len(df[df["Safety_Status"] == "SAFE"])
    warning_nodes = len(df[df["Safety_Status"] == "WARNING"])
    critical_nodes = len(df[df["Safety_Status"] == "CRITICAL"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Nodes", total_nodes)
    m2.metric("Safe Sectors", safe_nodes)
    m3.metric("Warnings", warning_nodes)
    m4.metric("Critical Alerts", critical_nodes)

    st.divider()

    # 6. Critical Alert Directives Callout
    critical_df = df[df["Safety_Status"] == "CRITICAL"]
    if not critical_df.empty:
        st.subheader("🚨 Urgent Field Actions Required")
        for _, row in critical_df.iterrows():
            st.markdown(
                f"""
                <div class="critical-card">
                    ⚠️ <strong>{row['Sector_ID']}</strong>: {row['Field_Directive']} 
                    <em>(pH: {row['pH_Level']} | TDS: {row['TDS_PPM']} PPM | Turbidity: {row['Turbidity_NTU']} NTU)</em>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 7. Main Telemetry Data Table
    st.subheader("📊 Live Telemetry Logs")
    st.dataframe(
        df[["Timestamp", "Sector_ID", "pH_Level", "TDS_PPM", "Turbidity_NTU", "Safety_Status", "Field_Directive"]],
        use_container_width=True,
        hide_index=True
    )

    # 8. Export CSV Functionality
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="💾 Export Report CSV",
        data=csv_data,
        file_name="water_telemetry_report.csv",
        mime="text/csv"
    )
