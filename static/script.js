// static/script.js
function loadTelemetry() {
    const driver = document.getElementById('driver-select').value;
    const gp = document.getElementById('gp-select').value;

    fetch(`/telemetry?driver=${driver}&gp=${gp}`)
        .then(response => response.json())
        .then(data => {
            const distances = data.map(d => d.Distance.toFixed(0));
            const speeds = data.map(d => d.Speed);

            const ctx = document.getElementById('speedChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: { labels: distances, datasets: [{ label: 'Speed [km/h]', data: speeds, borderColor: 'red', fill: false }] },
                options: { responsive: true, scales: { x: { title: { display: true, text: 'Distance [m]' } }, y: { title: { display: true, text: 'Speed [km/h]' } } } }
            });
        });
}

