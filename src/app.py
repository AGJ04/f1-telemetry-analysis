# src/app.py

import streamlit as st
import fastf1 as ff1
from fastf1 import plotting
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from PIL import Image

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
st.title("🏎️ F1 Telemetry Dashboard")

# -------------------------
# Sidebar: Session & Driver Selection
# -------------------------
st.sidebar.header("Session & Driver Selection")
year = st.sidebar.number_input("Year", min_value=2000, max_value=2025, value=2023)

# Grand Prix
schedule = ff1.get_event_schedule(year)
races = schedule['EventName'].tolist()
gp = st.sidebar.selectbox("Grand Prix", races)

# Session Type
session_type = st.sidebar.selectbox("Session Type", ["FP1", "FP2", "FP3", "Q", "R"])

# Load session
with st.spinner("Loading session data..."):
    session = ff1.get_session(year, gp, session_type)
    session.load()

drivers = sorted(session.laps['Driver'].unique())
driver1 = st.sidebar.selectbox("Driver 1", drivers, index=0)
driver2 = st.sidebar.selectbox("Driver 2", [d for d in drivers if d != driver1], index=0)

# -------------------------
# Driver images mapping
# -------------------------
driver_images = {
    "Lewis Hamilton": "src/images/hamilton.png",
    "Max Verstappen": "src/images/verstappen.png",
    "Charles Leclerc": "src/images/leclerc.png",
    # Add other drivers here...
}

def get_driver_image(driver):
    if driver in driver_images:
        return Image.open(driver_images[driver])
    return None

# -------------------------
# Functions
# -------------------------
def get_fastest_lap_telemetry(session, driver):
    laps = session.laps.pick_driver(driver)
    if laps.empty:
        return None, None
    lap = laps.pick_fastest()
    if lap is None:
        return None, None
    return lap.get_telemetry(), lap

def plot_speed_comparison(tel1, tel2, drv1, drv2):
    plt.figure(figsize=(10,4))
    plt.plot(tel1['Distance'], tel1['Speed'], label=drv1)
    plt.plot(tel2['Distance'], tel2['Speed'], label=drv2)
    plt.xlabel("Distance [m]")
    plt.ylabel("Speed [km/h]")
    plt.title("Fastest Lap Speed Comparison")
    plt.legend()
    st.pyplot(plt.gcf())
    plt.clf()

def plot_throttle_brake(tel1, tel2, drv1, drv2):
    plt.figure(figsize=(10,4))
    plt.plot(tel1['Distance'], tel1['Throttle'], label=f"{drv1} Throttle", color='green')
    plt.plot(tel1['Distance'], tel1['Brake'], label=f"{drv1} Brake", color='red')
    plt.plot(tel2['Distance'], tel2['Throttle'], label=f"{drv2} Throttle", color='lime')
    plt.plot(tel2['Distance'], tel2['Brake'], label=f"{drv2} Brake", color='darkred')
    plt.xlabel("Distance [m]")
    plt.ylabel("Throttle / Brake %")
    plt.title("Throttle & Brake Comparison")
    plt.legend()
    st.pyplot(plt.gcf())
    plt.clf()

def plot_track_speed_map(lap_obj, driver):
    telemetry = lap_obj.get_telemetry()
    if 'X' not in telemetry.columns or 'Y' not in telemetry.columns:
        st.warning(f"No X/Y coordinates available for {driver}'s lap.")
        return
    plt.figure(figsize=(6,6))
    plt.scatter(telemetry['X'], telemetry['Y'], c=telemetry['Speed'], cmap='viridis', s=5)
    plt.axis('equal')
    plt.colorbar(label='Speed [km/h]')
    plt.title(f"{driver} Track Speed Map")
    st.pyplot(plt.gcf())
    plt.clf()

def sector_analysis(lap1, lap2, drv1, drv2):
    sectors1 = [lap1.Sector1Time.total_seconds(), lap1.Sector2Time.total_seconds(), lap1.Sector3Time.total_seconds()]
    sectors2 = [lap2.Sector1Time.total_seconds(), lap2.Sector2Time.total_seconds(), lap2.Sector3Time.total_seconds()]
    fig, ax = plt.subplots(figsize=(6,4))
    ax.bar([f"Sector {i}" for i in range(1,4)], sectors1, alpha=0.5, label=drv1)
    ax.bar([f"Sector {i}" for i in range(1,4)], sectors2, alpha=0.5, label=drv2)
    ax.set_ylabel("Sector Time [s]")
    ax.set_title("Sector Comparison")
    ax.legend()
    st.pyplot(fig)
    plt.clf()

def kpi_table(telemetry, driver):
    st.metric("Max Speed", f"{telemetry['Speed'].max():.1f} km/h", delta=None)
    st.metric("Average Speed", f"{telemetry['Speed'].mean():.1f} km/h", delta=None)
    st.metric("Average Throttle", f"{telemetry['Throttle'].mean():.1f} %", delta=None)
    st.metric("Average Brake", f"{telemetry['Brake'].mean():.1f} %", delta=None)

def lap_delta_heatmap(tel1, tel2, drv1, drv2):
    merged = pd.merge_asof(tel1, tel2, on='Distance', suffixes=(f'_{drv1}', f'_{drv2}'))
    merged['Delta'] = merged[f'Time_{drv1}'] - merged[f'Time_{drv2}']
    plt.figure(figsize=(10,3))
    plt.scatter(merged['Distance'], np.zeros_like(merged['Distance']), c=merged['Delta'], cmap='bwr', s=15)
    plt.colorbar(label=f"Delta Time ({drv1}-{drv2}) [s]")
    plt.title("Lap Delta Heatmap")
    plt.xlabel("Distance [m]")
    st.pyplot(plt.gcf())
    plt.clf()

def session_summary(session):
    st.subheader("Session Summary")
    fastest_laps = session.laps.groupby('Driver')['LapTime'].min().sort_values()
    st.table(fastest_laps)

# -------------------------
# Run Analysis
# -------------------------
if st.button("Compare Laps"):
    tel1, lap1 = get_fastest_lap_telemetry(session, driver1)
    tel2, lap2 = get_fastest_lap_telemetry(session, driver2)

    if tel1 is None or tel2 is None:
        st.error("One of the drivers has no laps in this session.")
    else:
        # Show driver images side by side
        col1, col2 = st.columns(2)
        with col1:
            img1 = get_driver_image(driver1)
            if img1: st.image(img1, width=150, caption=driver1)
        with col2:
            img2 = get_driver_image(driver2)
            if img2: st.image(img2, width=150, caption=driver2)

        # Tabs for plots
        tab1, tab2, tab3 = st.tabs(["Speed", "Throttle & Brake", "Track Map"])
        with tab1:
            plot_speed_comparison(tel1, tel2, driver1, driver2)
        with tab2:
            plot_throttle_brake(tel1, tel2, driver1, driver2)
        with tab3:
            plot_track_speed_map(lap1, driver1)
            plot_track_speed_map(lap2, driver2)

        st.subheader("Sector Analysis")
        sector_analysis(lap1, lap2, driver1, driver2)

        st.subheader("Driver KPIs")
        col1, col2 = st.columns(2)
        with col1:
            kpi_table(tel1, driver1)
        with col2:
            kpi_table(tel2, driver2)

        st.subheader("Lap Delta Heatmap")
        lap_delta_heatmap(tel1, tel2, driver1, driver2)

        session_summary(session)
