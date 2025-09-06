import os
import fastf1 as ff1
from fastf1 import plotting
import matplotlib.pyplot as plt

# ---------- Setup Cache ----------
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cache_folder = os.path.join(project_root, "cache")

if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)

ff1.Cache.enable_cache(cache_folder)
plotting.setup_mpl()

# ---------- Functions ----------


def get_fastest_lap_telemetry(year, gp, session_type, driver):
    session = ff1.get_session(year, gp, session_type)
    session.load()
    lap = session.laps.pick_driver(driver).pick_fastest()
    return lap.get_telemetry()


def plot_speed_comparison(tel1, tel2, drv1, drv2):
    plt.figure(figsize=(10, 5))
    plt.plot(tel1['Distance'], tel1['Speed'], label=drv1)
    plt.plot(tel2['Distance'], tel2['Speed'], label=drv2)
    plt.xlabel("Distance [m]")
    plt.ylabel("Speed [km/h]")
    plt.title("Fastest Lap Speed Comparison")
    plt.legend()
    plt.show()


def get_fastest_lap_telemetry(year, gp, session_type, driver):
    session = ff1.get_session(year, gp, session_type)
    session.load()

    laps = session.laps.pick_driver(driver)
    if laps.empty:
        return None  # No laps for this driver

    lap = laps.pick_fastest()
    if lap is None:
        return None  # Driver has no valid fastest lap

    return lap.get_telemetry()
