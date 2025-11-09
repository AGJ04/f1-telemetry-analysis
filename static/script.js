// -----------------------------
// Helper Functions
// -----------------------------

function showLoading(show) {
    document.getElementById("loading").style.display = show ? "block" : "none";
}

function showError(msg) {
    document.getElementById("error").textContent = msg || "";
}

function setDisabled(selectId, disabled = true) {
    document.getElementById(selectId).disabled = disabled;
}

function populateSelect(selectId, items, formatter = i => i, placeholder = "Select") {
    const sel = document.getElementById(selectId);
    sel.innerHTML = "";

    const placeholderOption = document.createElement("option");
    placeholderOption.value = "";
    placeholderOption.text = placeholder;
    placeholderOption.disabled = true;
    placeholderOption.selected = true;
    sel.add(placeholderOption);

    items.forEach(i => {
        const opt = document.createElement("option");
        opt.value = i;
        opt.text = formatter(i);
        sel.add(opt);
    });

    setDisabled(selectId, items.length === 0);
}

async function fetchData(endpoint, params = {}) {
    const url = new URL(endpoint, window.location.origin);
    Object.keys(params).forEach(k => url.searchParams.append(k, params[k]));
    try {
        const res = await fetch(url);
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        return data;
    } catch (err) {
        showError(err.message);
        return null;
    }
}

// -----------------------------
// Dropdown Fetch Functions
// -----------------------------

async function fetchYears() {
    showError("");
    const years = await fetchData("/years");
    if (!years) return;
    populateSelect("year", years, y => y, "Select Year");
    setDisabled("gp", true);
    setDisabled("session", true);
    setDisabled("driver", true);
    setDisabled("lap", true);
}

async function fetchGps() {
    showError("");
    const year = document.getElementById("year").value;
    const gps = await fetchData("/gps", { year });
    if (!gps) return;
    populateSelect("gp", gps, g => g, "Select GP");
    setDisabled("gp", false);
    setDisabled("session", true);
    setDisabled("driver", true);
    setDisabled("lap", true);
}

async function fetchSessions() {
    showError("");
    const year = document.getElementById("year").value;
    const gp = document.getElementById("gp").value;
    const sessions = await fetchData("/sessions", { year, gp });
    if (!sessions) return;
    populateSelect("session", sessions, s => s, "Select Session");
    setDisabled("session", false);
    setDisabled("driver", true);
    setDisabled("lap", true);
}

async function fetchDrivers() {
    showError("");

    const driverSelect = document.getElementById("driver");
    driverSelect.innerHTML = "";

    const loadingOption = document.createElement("option");
    loadingOption.text = "Loading drivers...";
    loadingOption.disabled = true;
    loadingOption.selected = true;
    driverSelect.add(loadingOption);
    setDisabled("driver", true);

    const year = document.getElementById("year").value;
    const gp = document.getElementById("gp").value;
    const session = document.getElementById("session").value;

    const drivers = await fetchData("/drivers", { year, gp, session });
    if (!drivers) return;

    populateSelect("driver", drivers, d => d, "Select Driver");
    setDisabled("driver", false);
    setDisabled("lap", true);
}

async function fetchLaps() {
    showError("");
    const params = {
        year: document.getElementById("year").value,
        gp: document.getElementById("gp").value,
        session: document.getElementById("session").value,
        driver: document.getElementById("driver").value
    };
    const laps = await fetchData("/laps", params);
    if (!laps) return;
    populateSelect("lap", laps, l => `Lap ${l}`, "Select Lap");
    setDisabled("lap", laps.length === 0);
}

// -----------------------------
// Telemetry Plotting
// -----------------------------

async function loadTelemetry() {
    showError("");
    showLoading(true);

    const params = {
        year: document.getElementById("year").value,
        gp: document.getElementById("gp").value,
        session: document.getElementById("session").value,
        driver: document.getElementById("driver").value,
        lap: document.getElementById("lap").value
    };

    const data = await fetchData("/telemetry", params);
    showLoading(false);
    if (!data) return;

    const Distance = data.map(d => d.Distance);
    const Speed = data.map(d => d.Speed);
    const Throttle = data.map(d => d.Throttle);
    const Brake = data.map(d => d.Brake);
    const X = data.map(d => d.X);
    const Y = data.map(d => d.Y);

    // -----------------------------
    // Speed vs Distance
    // -----------------------------
    Plotly.react("speed-plot", [
        {
            x: Distance,
            y: Speed,
            type: "scatter",
            mode: "lines",
            name: "Speed",
            line: { color: "blue" },
            hovertemplate: "Distance: %{x} m<br>Speed: %{y} km/h<extra></extra>",
            selected: { marker: { opacity: 1 }, line: { opacity: 1 } },
            unselected: { marker: { opacity: 1 }, line: { opacity: 1 } }
        }
    ], { title: "Speed vs Distance", responsive: true, hovermode: "closest" });

    // -----------------------------
    // Throttle & Brake vs Distance
    // -----------------------------
    Plotly.react("throttle-brake-plot", [
        {
            x: Distance,
            y: Throttle,
            name: "Throttle",
            mode: "lines",
            line: { color: "green" },
            hovertemplate: "Distance: %{x} m<br>Throttle: %{y}<extra></extra>",
            selected: { marker: { opacity: 1 }, line: { opacity: 1 } },
            unselected: { marker: { opacity: 1 }, line: { opacity: 1 } }
        },
        {
            x: Distance,
            y: Brake,
            name: "Brake",
            mode: "lines+markers",
            marker: { size: 6 },
            line: { color: "red" },
            hovertemplate: "Distance: %{x} m<br>Brake: %{y}<extra></extra>",
            selected: { marker: { opacity: 1 }, line: { opacity: 1 } },
            unselected: { marker: { opacity: 1 }, line: { opacity: 1 } }
        }
    ], { title: "Throttle & Brake vs Distance", responsive: true, hovermode: "closest" });

    // -----------------------------
    // Track Map
    // -----------------------------
    Plotly.react("track-map-plot", [
        {
            x: X,
            y: Y,
            mode: "markers",
            marker: { color: Speed, size: 6, colorbar: { title: "Speed [km/h]" } },
            hovertemplate: "X: %{x}<br>Y: %{y}<br>Speed: %{marker.color} km/h<extra></extra>",
            selected: { marker: { opacity: 1 } },
            unselected: { marker: { opacity: 1 } }
        }
    ], { title: "Track Map", yaxis: { scaleanchor: "x" }, responsive: true, hovermode: "closest" });
}

// -----------------------------
// Event Listeners
// -----------------------------
document.getElementById("load").addEventListener("click", loadTelemetry);
document.getElementById("year").addEventListener("change", fetchGps);
document.getElementById("gp").addEventListener("change", fetchSessions);
document.getElementById("session").addEventListener("change", fetchDrivers);
document.getElementById("driver").addEventListener("change", fetchLaps);

// Initialize
fetchYears();
