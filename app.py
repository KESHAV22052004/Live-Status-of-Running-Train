import streamlit as st
import pandas as pd
from train_status import IndianRailwaysClient
import os
from dotenv import load_dotenv
import plotly.graph_objects as go

load_dotenv()

st.set_page_config(page_title="Indian Railways Live Status", layout="wide")

st.title("🚆 Indian Railways Live Status & Search")
st.markdown("Fetch real-time train locations and schedules for free.")

# Sidebar for Key
with st.sidebar:
    st.header("Settings")
    key = st.text_input("RapidAPI Key (Optional)", value=os.getenv("IRCTC_RAPIDAPI_KEY", ""), type="password")
    st.info("No key? No problem! It will use erail.in schedule data.")

client = IndianRailwaysClient(rapidapi_key=key)

query = st.text_input("Enter Train Number or Name (e.g. 12301, Rajdhani)", "")

if query:
    if not query.isdigit():
        results = client.search_trains(query)
        if results:
            train_options = {f"{t['train_no']} - {t['train_name']}": t['train_no'] for t in results[:10]}
            selected_train = st.selectbox("Select a train", options=list(train_options.keys()))
            train_no = train_options[selected_train]
        else:
            st.error("No trains found.")
            train_no = None
    else:
        train_no = query

    if train_no:
        if st.button("Fetch Status"):
            with st.spinner("Fetching data..."):
                status = client.get_live_status(train_no)
                
                if status:
                    d = status["data"]
                    st.success(f"Showing status for {d['trainName']}")
                    st.info(d.get('currentLocationInfo', ''))

                    df = pd.DataFrame(d["stations"])
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=df["stationName"], y=df["arrivalDelay"], name="Delay (min)", marker_color="indianred"))
                    fig.add_trace(go.Scatter(x=df["stationName"], y=df["distance"], name="Distance (km)", yaxis="y2", mode="lines+markers"))
                    
                    fig.update_layout(
                        yaxis=dict(title="Delay (min)"),
                        yaxis2=dict(title="Distance (km)", overlaying="y", side="right"),
                        hovermode="x unified",
                        template="plotly_white"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.table(df[["stationName", "arrival", "departure", "distance"]])
                else:
                    st.error("Could not fetch data for this train.")
