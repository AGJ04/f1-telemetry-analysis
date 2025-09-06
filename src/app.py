# src/app.py

import streamlit as st
import fastf1 as ff1
from fastf1 import plotting
import matplotlib.pyplot as plt
import pandas as pd
import os

# -------------------------
# Setup FastF1 Cache
# -------------------------
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cache_folder = os.path.join(project_root, "cache")
if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)
ff1.Cache.enable_cache(cache_folder)
plotting.setup_mpl()

st.title("F1 Telemetry Comparison App 🏎️")

# -------------------------
# Sidebar Inputs
# -------------------------
st.sidebar.header("Select Session & Drivers")

# Year
year = st.sidebar.number_input(
    "Year", min_value=2000, max_value=2025, value=2023)

# Grand Prix
schedule = ff1.get_event_schedule(year)
races = schedule['EventName'].tolist()
gp = st.sidebar.selectbox("Grand Prix", races)

# Session Type
session_type = st.sidebar.selectbox(
    "Session Type", ["FP1", "FP2", "FP3", "Q", "R"])

# Load session
session = ff1.get_session(year, gp, session_type)
with st.spinner("Loading session data..."):
    session.load()

# Driver dropdowns
drivers = sorted(session.laps['Driver'].unique())
driver1 = st.sidebar.selectbox("Driver 1", drivers, index=0)
driver2 = st.sidebar.selectbox("Driver 2", drivers, index=1)

# -------------------------
# Functions
# -------------------------


def get_fastest_lap_telemetry(session, driver):
    laps = session.laps.pick_driver(driver)
    if laps.empty:
        return None
    lap = laps.pick_fastest()
    if lap is None:
        return None
    return lap.get_telemetry(), lap


def plot_speed_comparison(tel1, tel2, drv1, drv2):
    plt.figure(figsize=(10, 5))
    plt.plot(tel1['Distance'], tel1['Speed'], label=drv1)
    plt.plot(tel2['Distance'], tel2['Speed'], label=drv2)
    plt.xlabel("Distance [m]")
    plt.ylabel("Speed [km/h]")
    plt.title("Fastest Lap Speed Comparison")
    plt.legend()
    st.pyplot(plt.gcf())
    plt.clf()


def plot_lap_delta(lap1, lap2, drv1, drv2):
    # Compute delta times
    merged = pd.merge_asof(lap1, lap2, on='Distance',
                           suffixes=(f'_{drv1}', f'_{drv2}'))
    merged['Delta'] = merged[f'Time_{drv1}'] - merged[f'Time_{drv2}']

    plt.figure(figsize=(10, 4))
    plt.plot(merged['Distance'], merged['Delta'])
    plt.axhline(0, color='black', linestyle='--')
    plt.xlabel("Distance [m]")
    plt.ylabel(f"Delta Time ({drv1} - {drv2}) [s]")
    plt.title("Lap Delta Over Track")
    st.pyplot(plt.gcf())
    plt.clf()


# -------------------------
# Run Analysis
# -------------------------
if st.button("Compare Laps"):
    tel1, lap1 = get_fastest_lap_telemetry(session, driver1)
    tel2, lap2 = get_fastest_lap_telemetry(session, driver2)

    if tel1 is None or tel2 is None:
        st.error("One of the drivers has no laps in this session.")
    else:
        st.subheader("Speed Comparison")
        plot_speed_comparison(tel1, tel2, driver1, driver2)

        st.subheader("Lap Delta (Time Difference)")
        plot_lap_delta(lap1, lap2, driver1, driver2)
