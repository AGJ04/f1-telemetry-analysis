document.addEventListener("DOMContentLoaded", () => {
    const yearInput = document.getElementById("year");
    const gpInput = document.getElementById("gp");
    const sessionSelect = document.getElementById("session");
    const driverSelect = document.getElementById("driver");
    const lapSelect = document.getElementById("lap");
    const loadBtn = document.getElementById("load");
    const output = document.getElementById("telemetry-data");

    // Fetch drivers when session details change
    async function loadDrivers() {
        const year = yearInput.value;
        const gp = gpInput.value;
        const session = sessionSelect.value;

        driverSelect.innerHTML = "<option>Loading...</option>";
        const res = await fetch(`/drivers?year=${year}&gp=${gp}&session=${session}`);
        const data = await res.json();

        driverSelect.innerHTML = "";
        if (data.error) {
            driverSelect.innerHTML = `<option>${data.error}</option>`;
        } else {
            data.forEach(driver => {
                const opt = document.createElement("option");
                opt.value = driver;
                opt.textContent = driver;
                driverSelect.appendChild(opt);
            });
            await loadLaps(); // load laps for first driver
        }
    }

    // Fetch laps for selected driver
    async function loadLaps() {
        const year = yearInput.value;
        const gp = gpInput.value;
        const session = sessionSelect.value;
        const driver = driverSelect.value;

        lapSelect.innerHTML = "<option>Loading...</option>";
        const res = await fetch(`/laps?year=${year}&gp=${gp}&session=${session}&driver=${driver}`);
        const data = await res.json();

        lapSelect.innerHTML = "";
        if (data.error) {
            lapSelect.innerHTML = `<option>${data.error}</option>`;
        } else {
            data.forEach((lap, i) => {
                const opt = document.createElement("option");
                opt.value = i;
                opt.textContent = `Lap ${lap}`;
                lapSelect.appendChild(opt);
            });
        }
    }

    // Load telemetry
    async function loadTelemetry() {
        const year = yearInput.value;
        const gp = gpInput.value;
        const session = sessionSelect.value;
        const driver = driverSelect.value;
        const lap = lapSelect.value;

        output.textContent = "Loading telemetry...";
        const res = await fetch(`/telemetry?year=${year}&gp=${gp}&session=${session}&driver=${driver}&lap=${lap}`);
        const data = await res.json();

        if (data.error) {
            output.textContent = "Error: " + data.error;
        } else {
            output.textContent = JSON.stringify(data, null, 2);
        }
    }

    // Event listeners
    sessionSelect.addEventListener("change", loadDrivers);
    gpInput.addEventListener("change", loadDrivers);
    yearInput.addEventListener("change", loadDrivers);
    driverSelect.addEventListener("change", loadLaps);
    loadBtn.addEventListener("click", loadTelemetry);

    // Initial load
    loadDrivers();
});
