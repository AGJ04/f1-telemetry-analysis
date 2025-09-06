# src/app.py

import streamlit as st
import fastf1 as ff1
from fastf1 import plotting
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from PIL import Image
import plotly.express as px

# -------------------------
# Setup FastF1 Cache
# -------------------------
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cache_folder = os.path.join(project_root, "cache")
if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)
ff1.Cache.enable_cache(cache_folder)
plotting.setup_mpl()

st.set_page_config(page_title="F1 Telemetry Dashboard", layout="wide")
st.title("🏎️ F1 Telemetry Dashboard (Enhanced Edition)")

# -------------------------
# Sidebar: Session & Driver Selection
# -------------------------
st.sidebar.header("Session & Driver Selection")
year = st.sidebar.number_input("Year", min_value=2000, max_value=2025, value=2023)
schedule = ff1.get_event_schedule(year)
races = schedule['EventName'].tolist()
gp = st.sidebar.selectbox("Grand Prix", races)
session_type = st.sidebar.selectbox("Session Type", ["FP1", "FP2", "FP3", "Q", "R"])

with st.spinner("Loading session data..."):
    session = ff1.get_session(year, gp, session_type)
    session.load()

drivers = sorted(session.laps['Driver'].unique())
driver1 = st.sidebar.selectbox("Driver 1", drivers, index=0)
driver2 = st.sidebar.selectbox("Driver 2", [d for d in drivers if d != driver1], index=0)

laps1 = session.laps.pick_driver(driver1)
laps2 = session.laps.pick_driver(driver2)
lap_num1 = st.sidebar.select_slider(f"{driver1} Lap", options=list(range(len(laps1))))
lap_num2 = st.sidebar.select_slider(f"{driver2} Lap", options=list(range(len(laps2))))

# -------------------------
# Driver Images & Team Colors
# -------------------------
driver_images = {
    "Lewis Hamilton": "src/images/hamilton.png",
    "Max Verstappen": "src/images/verstappen.png",
    "Charles Leclerc": "src/images/leclerc.png",
    # Add other drivers here
}

driver_colors = {
    "Lewis Hamilton": "#00D2BE",
    "Max Verstappen": "#1E41FF",
    "Charles Leclerc": "#DC0000",
    # Add other drivers here
}

def get_driver_image(driver):
    if driver in driver_images:
        return Image.open(driver_images[driver])
    return None

# -------------------------
# Telemetry Functions
# -------------------------
def get_lap_telemetry(session, driver, lap_index):
    lap = session.laps.pick_driver(driver).iloc[lap_index]
    return lap.get_telemetry(), lap

def interactive_line_plot(tel1, tel2, drv1, drv2, metric='Speed', ylabel='Speed [km/h]'):
    df1 = tel1[['Distance', metric]].copy(); df1['Driver'] = drv1
    df2 = tel2[['Distance', metric]].copy(); df2['Driver'] = drv2
    df = pd.concat([df1, df2])
    fig = px.line(df, x='Distance', y=metric, color='Driver', labels={'Distance':'Distance [m]', metric: ylabel},
                  title=f"{metric} Comparison")
    st.plotly_chart(fig)

def track_map_heatmap(lap_obj, driver, metric='Speed'):
    telemetry = lap_obj.get_telemetry()
    if 'X' not in telemetry.columns or 'Y' not in telemetry.columns:
        st.warning(f"No X/Y coordinates for {driver}")
        return
    fig = px.scatter(telemetry, x='X', y='Y', color=metric, color_continuous_scale='viridis',
                     title=f"{driver} Track {metric} Map", size_max=5)
    fig.update_layout(yaxis=dict(scaleanchor="x", scaleratio=1))
    st.plotly_chart(fig)

def sector_delta_heatmap(lap1, lap2, drv1, drv2):
    sectors1 = [lap1.Sector1Time.total_seconds(), lap1.Sector2Time.total_seconds(), lap1.Sector3Time.total_seconds()]
    sectors2 = [lap2.Sector1Time.total_seconds(), lap2.Sector2Time.total_seconds(), lap2.Sector3Time.total_seconds()]
    delta = [s1-s2 for s1,s2 in zip(sectors1,sectors2)]
    fig = px.bar(x=['Sector 1','Sector 2','Sector 3'], y=delta,
                 color=['green' if d<0 else 'red' for d in delta],
                 title=f"Sector Delta ({drv1}-{drv2})")
    st.plotly_chart(fig)

def kpi_table(telemetry, driver):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Max Speed", f"{telemetry['Speed'].max():.1f} km/h")
    col2.metric("Average Speed", f"{telemetry['Speed'].mean():.1f} km/h")
    col3.metric("Avg Throttle", f"{telemetry['Throttle'].mean():.1f} %")
    col4.metric("Avg Brake", f"{telemetry['Brake'].mean():.1f} %")

def gforce_calculation(tel):
    tel['ax'] = tel['Speed'].diff() / tel['Time'].diff().dt.total_seconds()
    # Lateral G approximation: diff in heading or Y coordinates if available
    if 'X' in tel.columns and 'Y' in tel.columns:
        tel['ay'] = np.sqrt((tel['X'].diff()**2 + tel['Y'].diff()**2)) / tel['Time'].diff().dt.total_seconds()
    else:
        tel['ay'] = 0
    return tel

def download_telemetry_csv(tel, driver, lap_index):
    csv_file = f"{driver}_lap{lap_index}_telemetry.csv"
    tel.to_csv(csv_file, index=False)
    return csv_file

# -------------------------
# Run Analysis
# -------------------------
if st.button("Compare Laps"):
    tel1, lap1 = get_lap_telemetry(session, driver1, lap_num1)
    tel2, lap2 = get_lap_telemetry(session, driver2, lap_num2)

    if tel1 is None or tel2 is None:
        st.error("One of the drivers has no telemetry.")
    else:
        # Driver Images
        col1, col2 = st.columns(2)
        with col1:
            img1 = get_driver_image(driver1)
            if img1: st.image(img1, width=150, caption=driver1)
        with col2:
            img2 = get_driver_image(driver2)
            if img2: st.image(img2, width=150, caption=driver2)

        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Speed", "Throttle/Brake", "Track Map", "Sector Delta", "G-Force"])
        with tab1:
            interactive_line_plot(tel1, tel2, driver1, driver2, metric='Speed', ylabel='Speed [km/h]')
        with tab2:
            interactive_line_plot(tel1, tel2, driver1, driver2, metric='Throttle', ylabel='Throttle [%]')
            interactive_line_plot(tel1, tel2, driver1, driver2, metric='Brake', ylabel='Brake [%]')
        with tab3:
            track_map_heatmap(lap1, driver1, metric='Speed')
            track_map_heatmap(lap2, driver2, metric='Speed')
        with tab4:
            sector_delta_heatmap(lap1, lap2, driver1, driver2)
        with tab5:
            tel1 = gforce_calculation(tel1)
            tel2 = gforce_calculation(tel2)
            interactive_line_plot(tel1, tel2, driver1, driver2, metric='ax', ylabel='Longitudinal G')
            interactive_line_plot(tel1, tel2, driver1, driver2, metric='ay', ylabel='Lateral G')

        # KPIs
        st.subheader("Driver KPIs")
        col1, col2 = st.columns(2)
        with col1: kpi_table(tel1, driver1)
        with col2: kpi_table(tel2, driver2)

        # Download CSVs
        st.subheader("Download Telemetry Data")
        csv1 = download_telemetry_csv(tel1, driver1, lap_num1)
        csv2 = download_telemetry_csv(tel2, driver2, lap_num2)
        st.download_button(label=f"Download {driver1} Lap {lap_num1} CSV", data=open(csv1,'rb'), file_name=csv1)
        st.download_button(label=f"Download {driver2} Lap {lap_num2} CSV", data=open(csv2,'rb'), file_name=csv2)
