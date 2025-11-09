import os
from flask import Flask, render_template, jsonify, request
import fastf1 as ff1
import pandas as pd
from src.telemetry_analysis import get_lap_telemetry

# -------------------------
# Setup Flask App
# -------------------------
project_root = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(project_root, "templates")
static_dir = os.path.join(project_root, "static")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Enable FastF1 cache
cache_dir = os.path.join(project_root, "cache")
os.makedirs(cache_dir, exist_ok=True)
ff1.Cache.enable_cache(cache_dir)

# Simple in-memory session cache
SESSION_CACHE = {}

def load_session(year, gp, session_type):
    key = f"{year}-{gp}-{session_type}"
    if key not in SESSION_CACHE:
        session = ff1.get_session(year, gp, session_type)
        session.load()
        SESSION_CACHE[key] = session
    return SESSION_CACHE[key]

# -------------------------
# Routes
# -------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/telemetry")
def telemetry():
    """Return telemetry for a given driver and lap."""
    try:
        year = int(request.args.get("year", 2023))
        gp = request.args.get("gp")
        session_type = request.args.get("session")
        driver = request.args.get("driver")
        lap_index = int(request.args.get("lap", 0))

        telemetry_df = get_lap_telemetry(year, gp, session_type, driver, lap_index)

        # Convert timedelta columns to seconds safely
        for col in telemetry_df.select_dtypes(include=["timedelta64[ns]"]).columns:
            telemetry_df[col] = telemetry_df[col].apply(
                lambda x: x.total_seconds() if pd.notnull(x) else None
            )

        # Replace all remaining NaN/NaT with None for valid JSON
        import numpy as np
        telemetry_df = telemetry_df.replace({np.nan: None})

        return jsonify(telemetry_df.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/years")
def years():
    return jsonify(list(range(2018, 2026)))

@app.route("/gps")
def gps():
    try:
        year = int(request.args.get("year"))
        schedule = ff1.get_event_schedule(year)
        gps = schedule["EventName"].tolist()
        return jsonify(gps)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/sessions")
def sessions():
    try:
        year = int(request.args.get("year"))
        gp = request.args.get("gp")
        available = []
        for s in ["FP1", "FP2", "FP3", "Q", "R"]:
            try:
                _ = ff1.get_session(year, gp, s)
                available.append(s)
            except Exception:
                pass
        return jsonify(available)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/drivers")
def drivers():
    try:
        year = int(request.args.get("year", 2023))
        gp = request.args.get("gp", "Monaco Grand Prix")
        session_type = request.args.get("session", "Q")
        session = load_session(year, gp, session_type)
        drivers = sorted(session.laps['Driver'].unique().tolist())
        return jsonify(drivers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/laps")
def laps():
    try:
        year = int(request.args.get("year"))
        gp = request.args.get("gp")
        session_type = request.args.get("session")
        driver = request.args.get("driver")
        session = load_session(year, gp, session_type)
        laps_df = session.laps.pick_drivers(driver)
        return jsonify(laps_df["LapNumber"].tolist())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
