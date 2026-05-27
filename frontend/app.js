const API_URL = 'http://localhost:8000';

const map = L.map('map').setView([0, 0], 2);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 18,
}).addTo(map);

const issIcon = L.divIcon({
    className: '',
    html: '<div class="iss-marker">🛸</div>',
    iconSize: [30, 30],
    iconAnchor: [15, 15],
});

let issMarker = null;

function formatCountdown(targetDate) {
    const now = new Date();
    const diff = targetDate - now;

    if (diff <= 0) {
        return 'Wystartował';
    }

    const totalSeconds = Math.floor(diff / 1000);
    const days = Math.floor(totalSeconds / 86400);
    const hours = Math.floor((totalSeconds % 86400) / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    return `${days}d ${hours}h ${minutes}m ${seconds}s`;
}

function renderISSInfo(data) {
    const container = document.getElementById('iss-info');

    if (!data) {
        container.innerHTML = '<p class="no-data">Brak danych</p>';
        return;
    }

    const lat = parseFloat(data.latitude).toFixed(4);
    const lon = parseFloat(data.longitude).toFixed(4);
    const alt = data.altitude ? parseFloat(data.altitude).toFixed(1) + ' km' : 'N/A';
    const vel = data.velocity ? parseFloat(data.velocity).toFixed(1) + ' km/h' : 'N/A';
    const country = data.country || 'Ocean / Brak danych';

    container.innerHTML = `
        <div class="iss-row">
            <span class="iss-label">Szerokość</span>
            <span class="iss-value">${lat}°</span>
        </div>
        <div class="iss-row">
            <span class="iss-label">Długość</span>
            <span class="iss-value">${lon}°</span>
        </div>
        <div class="iss-row">
            <span class="iss-label">Wysokość</span>
            <span class="iss-value">${alt}</span>
        </div>
        <div class="iss-row">
            <span class="iss-label">Prędkość</span>
            <span class="iss-value">${vel}</span>
        </div>
        <div class="iss-row">
            <span class="iss-label">Nad</span>
            <span class="iss-value">${country}</span>
        </div>
    `;

    const lat2 = parseFloat(data.latitude);
    const lon2 = parseFloat(data.longitude);

    if (issMarker) {
        issMarker.setLatLng([lat2, lon2]);
    } else {
        issMarker = L.marker([lat2, lon2], { icon: issIcon }).addTo(map);
    }
}

function renderLaunches(launches) {
    const container = document.getElementById('launches-list');

    if (!launches || launches.length === 0) {
        container.innerHTML = '<p class="no-data">Brak danych</p>';
        return;
    }

    container.innerHTML = launches.map((launch) => {
        const date = new Date(launch.date_utc);
        const dateStr = date.toLocaleDateString('pl-PL', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
        const isPast = date < new Date();
        const status = isPast ? 'Wystrzelono' : formatCountdown(date);

        const provider = launch.provider_name ? `<div class="launch-provider">${launch.provider_name}</div>` : '';
        const webcast = launch.webcast_url
            ? `<a class="launch-webcast" href="${launch.webcast_url}" target="_blank" rel="noopener">▶ oglądaj</a>`
            : '';

        return `
            <div class="launch-card">
                ${provider}
                <div class="launch-name">${launch.name}</div>
                <div class="launch-date">${dateStr} UTC</div>
                <div class="launch-countdown ${isPast ? 'past' : ''}">${status}</div>
                ${webcast}
            </div>
        `;
    }).join('');
}

async function fetchISSPosition() {
    try {
        const resp = await fetch(`${API_URL}/iss/current`);
        if (resp.status === 404) {
            renderISSInfo(null);
            return;
        }
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        renderISSInfo(data);
    } catch (err) {
        console.warn('Nie udało się pobrać pozycji ISS:', err);
        renderISSInfo(null);
    }
}

async function fetchUpcomingLaunches() {
    try {
        const resp = await fetch(`${API_URL}/launches/upcoming`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        renderLaunches(data.slice(0, 5));
    } catch (err) {
        console.warn('Nie udało się pobrać startów:', err);
        renderLaunches(null);
    }
}

let countdownInterval = null;
let currentLaunches = null;

async function refreshLaunches() {
    const resp = await fetch(`${API_URL}/launches/upcoming`).catch(() => null);
    if (!resp || !resp.ok) {
        renderLaunches(null);
        return;
    }
    currentLaunches = (await resp.json()).slice(0, 5);
    renderLaunches(currentLaunches);
}

function startCountdownTick() {
    if (countdownInterval) clearInterval(countdownInterval);
    countdownInterval = setInterval(() => {
        if (currentLaunches) {
            renderLaunches(currentLaunches);
        }
    }, 1000);
}

(async function init() {
    await fetchISSPosition();
    await refreshLaunches();
    startCountdownTick();

    setInterval(fetchISSPosition, 5000);
    setInterval(refreshLaunches, 5 * 60 * 1000);
})();
