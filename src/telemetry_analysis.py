# src/telemetry_analysis.py

import fastf1 as ff1
import pandas as pd
import os

# Setup FastF1 cache
cache_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)
ff1.Cache.enable_cache(cache_folder)


def get_lap_telemetry(year, gp, session_type, driver, lap_index=0):
    """
    Fetch telemetry data for a specific driver's lap in a given session.

    Args:
        year (int): Year of the race (e.g. 2023)
        gp (str): Grand Prix name (e.g. 'Monaco Grand Prix')
        session_type (str): Session type (FP1, FP2, FP3, Q, R)
        driver (str): Driver name (e.g. 'Lewis Hamilton')
        lap_index (int): Which lap to fetch (0 = fastest lap)

    Returns:
        pd.DataFrame: Telemetry data with speed, throttle, brake, distance, etc.
    """
    session = ff1.get_session(year, gp, session_type)
    session.load()

    laps = session.laps.pick_driver(driver)
    if laps.empty:
        raise ValueError(f"No laps found for {driver} in {gp} {session_type} {year}")

    if lap_index == 0:
        lap = laps.pick_fastest()
    else:
        lap = laps.iloc[lap_index]

    telemetry = lap.get_telemetry()
    telemetry["Driver"] = driver
    telemetry["LapTime"] = lap['LapTime']

    return telemetry