# app.py

from flask import Flask, render_template, jsonify, request
from src.telemetry_analysis import get_lap_telemetry
import fastf1 as ff1

# -------------------------
# Setup Flask App
# -------------------------
app = Flask(__name__)

# Enable FastF1 cache
ff1.Cache.enable_cache("cache")

# -------------------------
# Routes
# -------------------------

@app.route("/")
def index():
    """Serve the main dashboard page."""
    return render_template("index.html")


@app.route("/telemetry")
def telemetry():
    """
    Serve telemetry data as JSON.
    Accepts query parameters:
    - year
    - gp (Grand Prix name)
    - session (FP1, FP2, FP3, Q, R)
    - driver
    - lap (lap index, default 0)
    """
    try:
        # Get parameters from request
        year = int(request.args.get("year", 2023))
        gp = request.args.get("gp", "Monaco Grand Prix")
        session_type = request.args.get("session", "Q")
        driver = request.args.get("driver", "Lewis Hamilton")
        lap_index = int(request.args.get("lap", 0))

        # Fetch telemetry using your module
        telemetry_df = get_lap_telemetry(year, gp, session_type, driver, lap_index)

        # Return as JSON
        return jsonify(telemetry_df.to_dict(orient='records'))

    except Exception as e:
        # Return error message as JSON
        return jsonify({"error": str(e)}), 500


@app.route("/drivers")
def drivers():
    """
    Return a list of drivers for a given session.
    Query params: year, gp, session
    """
    try:
        year = int(request.args.get("year", 2023))
        gp = request.args.get("gp", "Monaco Grand Prix")
        session_type = request.args.get("session", "Q")

        session = ff1.get_session(year, gp, session_type)
        session.load()
        driver_list = sorted(session.laps['Driver'].unique())
        return jsonify(driver_list)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/laps")
def laps():
    """
    Return a list of laps for a driver in a session.
    Query params: year, gp, session, driver
    """
    try:
        year = int(request.args.get("year", 2023))
        gp = request.args.get("gp", "Monaco Grand Prix")
        session_type = request.args.get("session", "Q")
        driver = request.args.get("driver", "Lewis Hamilton")

        session = ff1.get_session(year, gp, session_type)
        session.load()
        laps = session.laps.pick_driver(driver)
        lap_numbers = laps.index.tolist()
        return jsonify(lap_numbers)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# Run Server
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
