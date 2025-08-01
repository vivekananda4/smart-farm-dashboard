import streamlit as st
import boto3
import pandas as pd
from decimal import Decimal
import time

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('SmartFarmData')

st.set_page_config(page_title="Smart Farm Monitoring Dashboard", layout="wide")
st.title("🌱 Smart Farm Monitoring Dashboard")

# Fetch data from DynamoDB
def fetch_data():
    response = table.scan()
    data = response.get("Items", [])
    for item in data:
        for k, v in item.items():
            if isinstance(v, Decimal):
                item[k] = float(v)
    return pd.DataFrame(data)

refresh_rate = 10  # refresh every 10 seconds
placeholder = st.empty()

while True:
    data = fetch_data()
    with placeholder.container():
        if not data.empty:
            data = data.sort_values(by="timestamp", ascending=False)
            latest = data.iloc[0]

            st.subheader("📊 Latest Sensor Readings")
            col1, col2, col3 = st.columns(3)
            col1.metric("🌡 Temperature (°C)", latest["temperature"])
            col2.metric("💧 Soil Moisture (%)", latest["soilMoisture"])
            col3.metric("💦 Humidity (%)", latest["humidity"])
            col1.metric("☀️ Light (lux)", latest["light"])
            col2.metric("🌧 Rain", latest["rain"])
            col3.metric("CO₂ (ppm)", latest["co2"])

            st.subheader("🤖 ML Irrigation Prediction")
            if str(latest["ml_prediction"]) in ["1", "1.0", "True", "true"]:
                st.error("🚨 Irrigation Needed! Start irrigation immediately.")
            else:
                st.success("✅ No irrigation needed at this time.")

            st.subheader("📜 Alert History (Last 20)")
            history = data.head(20)
            history["Status"] = history["ml_prediction"].apply(lambda x: "Irrigation Needed" if str(x) in ["1", "1.0"] else "No Irrigation")
            st.dataframe(history[["device_id", "timestamp", "soilMoisture", "temperature", "Status"]])
        else:
            st.warning("No data yet. Start the simulation to see results.")
    time.sleep(refresh_rate)

