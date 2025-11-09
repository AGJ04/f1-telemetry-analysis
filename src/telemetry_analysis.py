import fastf1 as ff1
import os
import pandas as pd

def get_lap_telemetry(year, gp, session_type, driver, lap_index=0):
    session = ff1.get_session(year, gp, session_type)
    session.load()
    laps = session.laps.pick_drivers(driver)
    if laps.empty:
        raise ValueError(f"No laps found for {driver} in {gp} {session_type} {year}")

    lap = laps.pick_fastest() if lap_index == 0 else laps.iloc[lap_index]
    telemetry = lap.get_telemetry()
    telemetry["Driver"] = driver
    telemetry["LapTime"] = lap["LapTime"]
    return telemetry
