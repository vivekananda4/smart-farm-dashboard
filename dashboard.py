import streamlit as st
import requests
import pandas as pd
import time
import plotly.express as px

# -------------------------------
# CONFIG
# -------------------------------
API_URL = "https://49z25uc8ag.execute-api.us-east-1.amazonaws.com/prod"  # Your API Gateway endpoint

st.set_page_config(page_title="Smart Farm Dashboard", layout="wide")

st.title("Smart Farm IoT Monitoring Dashboard")

# Auto refresh every 10 seconds
refresh_rate = 10

# -------------------------------
# Function to fetch data
# -------------------------------
@st.cache_data(ttl=refresh_rate)
def get_data():
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Handle nested body if needed
            if isinstance(data, dict) and "body" in data:
                data = data["body"]
                if isinstance(data, str):
                    import json
                    data = json.loads(data)
            return data
        else:
            st.error(f"Error: API returned {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

# -------------------------------
# Fetch latest data
# -------------------------------
data = get_data()

if data:
    df = pd.DataFrame(data)

    # Convert timestamp (if numeric) to readable time
    if "timestamp" in df.columns:
        try:
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        except Exception:
            pass

    # Latest record
    latest = df.iloc[0]

    # -------------------------------
    # Metrics row
    # -------------------------------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric( Temperature (°C)", latest["temperature"])
    col2.metric(" Humidity (%)", latest["humidity"])
    col3.metric(" Light (lux)", latest["light"])
    col4.metric(" Soil Moisture (%)", latest["soilMoisture"])

    # -------------------------------
    # Charts
    # -------------------------------
    st.subheader(" Sensor Data Trends")

    fig_temp = px.line(df, x="timestamp", y="temperature", title="Temperature Over Time")
    fig_hum = px.line(df, x="timestamp", y="humidity", title="Humidity Over Time")
    fig_light = px.line(df, x="timestamp", y="light", title="Light Intensity Over Time")
    fig_soil = px.line(df, x="timestamp", y="soilMoisture", title="Soil Moisture Over Time")

    st.plotly_chart(fig_temp, use_container_width=True)
    st.plotly_chart(fig_hum, use_container_width=True)
    st.plotly_chart(fig_light, use_container_width=True)
    st.plotly_chart(fig_soil, use_container_width=True)

    # -------------------------------
    # Alerts
    # -------------------------------
    st.subheader(" Alerts")
    if latest["temperature"] > 35:
        st.error(" High temperature detected!")
    if latest["humidity"] < 30:
        st.warning(" Low humidity level!")
    if latest["soilMoisture"] < 20:
        st.warning(" Soil moisture critically low!")

    # -------------------------------
    # Data Table
    # -------------------------------
    st.subheader(" Latest 20 Records")
    st.dataframe(df.head(20))

else:
    st.warning("No data received from API.")

# Auto refresh button
st.info("Page auto-refreshes every 10 seconds. Click 'Rerun' to refresh manually.")
