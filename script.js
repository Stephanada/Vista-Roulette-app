const STATE = {
    stations: [],
    currentStationIndex: null, // index in the *filtered* pool
    lastStationSlug: null,
    audioPlayer: null,
    isPlaying: false,
    filters: {
        provinceLock: 'any',
        formatLock: 'any'
    }
};

const TIMEZONES = {
    'ON': 'America/Toronto',
    'AB': 'America/Edmonton',
    'NS': 'America/Halifax',
    'NT': 'America/Yellowknife',
    'SK': 'America/Regina' // Lloydminster is usually Mountain Time, but standardizing to AB covers it
};

// BC specific exceptions
const BC_EXCEPTIONS = {
    'Dawson Creek': 'America/Edmonton',
    'Cranbrook': 'America/Edmonton'
};

// DOM Elements
const els = {
    stationName: document.getElementById('station-name'),
    stationFormat: document.getElementById('format-string'),
    spinBtn: document.getElementById('spin-btn'),
    playPauseBtn: document.getElementById('play-pause-btn'),
    playIcon: document.querySelector('.play-icon'),
    pauseIcon: document.querySelector('.pause-icon'),
    audioPlayer: document.getElementById('audio-player'),
    statusIndicator: document.getElementById('status-indicator'),

    // Filters & Display Extras
    provinceSelect: document.getElementById('province-select'),
    formatSelect: document.getElementById('format-select'),
    stationDisplay: document.getElementById('station-display'),
    stationLogo: document.getElementById('station-logo'),
    townLinkContainer: document.getElementById('town-link-container'),
    stationTown: document.getElementById('station-town'),
    mytownnowLink: document.getElementById('mytownnow-link'),

    // Local Info
    localTime: document.getElementById('local-time'),
    weatherTown: document.getElementById('weather-town'),
    weatherTemp: document.getElementById('weather-temp'),
    weatherIcon: document.getElementById('weather-icon')
};

// State for intervals
let timeInterval;

// Global function to handle logo loading errors
window.handleLogoError = function(img) {
    img.style.display = 'none';
    const fallbackDiv = document.getElementById('logo-fallback');
    if (fallbackDiv) {
        fallbackDiv.style.display = 'flex';
    }
};

// Initialization
async function init() {
    try {
        const response = await fetch('stations_db.json');
        if (!response.ok) throw new Error('Failed to fetch stations_db.json');

        STATE.stations = await response.json();

        populateDropdowns();

        // Start local time clock
        startClock();

        // Pick a random station to start
        selectStation(getRandomStation());

        setupEventListeners();
    } catch (err) {
        els.stationName.textContent = "Error Loading Data";
        els.stationFormat.textContent = err.message;
        console.error(err);
    }
}

function populateDropdowns() {
    const provinces = [...new Set(STATE.stations.map(s => s.prov))].filter(Boolean).sort();
    const formats = [...new Set(STATE.stations.map(s => s.format))].filter(Boolean).sort();

    provinces.forEach(prov => {
        const option = document.createElement('option');
        option.value = prov;
        option.textContent = prov;
        els.provinceSelect.appendChild(option);
    });

    formats.forEach(format => {
        const option = document.createElement('option');
        option.value = format;
        option.textContent = format;
        els.formatSelect.appendChild(option);
    });
}

function setupEventListeners() {
    els.spinBtn.addEventListener('click', handleSpin);

    els.playPauseBtn.addEventListener('click', togglePlayPlayer);

    els.provinceSelect.addEventListener('change', (e) => {
        STATE.filters.provinceLock = e.target.value;
        validateSpinAvailability();
    });

    els.formatSelect.addEventListener('change', (e) => {
        STATE.filters.formatLock = e.target.value;
        validateSpinAvailability();
    });

    // Audio Event listeners for accurate status
    els.audioPlayer.addEventListener('playing', () => updateAudioUI(true, false));
    els.audioPlayer.addEventListener('pause', () => updateAudioUI(false, false));
    els.audioPlayer.addEventListener('waiting', () => updateAudioUI(false, true));
    els.audioPlayer.addEventListener('error', () => {
        els.statusIndicator.className = 'status-indicator';
        els.stationFormat.textContent = "Stream Offline / Error";
    });
}

function selectStation(station) {
    if (!station) return;
    STATE.currentStationIndex = station; // This should probably be an index or the station object itself, not an index.
    els.stationName.textContent = station.name;
    els.stationFormat.textContent = `${station.format} • ${station.slug.toUpperCase()}`;

    // Logo-First Strategy with Text Fallback
    const logoContainer = document.querySelector('.station-logo-container');
    logoContainer.innerHTML = ''; // Clear previous content
    
    if (station.logo_url && station.website) {
        // Create link wrapper
        const logoLink = document.createElement('a');
        logoLink.href = station.website;
        logoLink.target = '_blank';
        logoLink.style.display = 'block';
        
        // Create image element
        const logoImg = document.createElement('img');
        logoImg.id = 'station-logo';
        logoImg.src = station.logo_url;
        logoImg.alt = station.display_brand || station.name;
        logoImg.onerror = function() { window.handleLogoError(this); };
        
        // Create fallback div
        const fallbackDiv = document.createElement('div');
        fallbackDiv.id = 'logo-fallback';
        fallbackDiv.textContent = station.display_brand || `My${station.town?.replace(/\s/g, '')}Now`;
        fallbackDiv.style.display = 'none';
        
        logoLink.appendChild(logoImg);
        logoLink.appendChild(fallbackDiv);
        logoContainer.appendChild(logoLink);
    } else if (station.display_brand) {
        // No logo URL, show fallback immediately
        const fallbackDiv = document.createElement('div');
        fallbackDiv.id = 'logo-fallback';
        fallbackDiv.textContent = station.display_brand;
        logoContainer.appendChild(fallbackDiv);
    }

    if (station.town) {
        const displayBrand = station.display_brand || "MyTownNow";
        
        els.mytownnowLink.textContent = displayBrand;
        els.mytownnowLink.href = station.website || station.mytownnow_url || "https://vistaradio.ca";
        els.townLinkContainer.style.display = 'block';
        els.weatherTown.textContent = station.town;
        fetchWeather(station.town);
    } else {
        els.townLinkContainer.style.display = 'none';
        els.weatherTown.textContent = "--";
        els.weatherTemp.textContent = "--°C";
        els.weatherIcon.textContent = "☁️";
    }

    // Load URL into audio player but don't auto-play immediately
    // If was playing, keep playing
    const wasPlaying = STATE.isPlaying;
    els.audioPlayer.src = station.stream_url;

    if (wasPlaying) {
        els.audioPlayer.play().catch(console.error);
    }
}

// Logic to get a filtered random station
function getRandomStation() {
    let pool = STATE.stations;

    // Apply Filters
    if (STATE.filters.provinceLock !== 'any') {
        pool = pool.filter(s => s.prov === STATE.filters.provinceLock);
    }
    if (STATE.filters.formatLock !== 'any') {
        pool = pool.filter(s => s.format === STATE.filters.formatLock);
    }

    if (pool.length === 0) return null;

    // True Random: Prevent playing exactly the same station twice in a row if possible
    let available = pool;
    if (pool.length > 1 && STATE.lastStationSlug) {
        available = pool.filter(s => s.slug !== STATE.lastStationSlug);
    }

    const randomIndex = Math.floor(Math.random() * available.length);
    STATE.lastStationSlug = available[randomIndex].slug;
    return available[randomIndex];
}

function validateSpinAvailability() {
    let pool = STATE.stations;
    if (STATE.filters.provinceLock !== 'any') {
        pool = pool.filter(s => s.prov === STATE.filters.provinceLock);
    }
    if (STATE.filters.formatLock !== 'any') {
        pool = pool.filter(s => s.format === STATE.filters.formatLock);
    }

    if (pool.length === 0) {
        els.spinBtn.disabled = true;
        els.spinBtn.textContent = "NO MATCHES";
    } else {
        els.spinBtn.disabled = false;
        els.spinBtn.textContent = "RADIO ROULETTE";
    }
}

// Local Info Logic
function startClock() {
    if (timeInterval) clearInterval(timeInterval);
    updateTime(); // Initial call
    timeInterval = setInterval(updateTime, 1000);
}

function updateTime() {
    // Determine Timezone based on active station
    let tz = 'America/Vancouver'; // Default to PT
    const station = STATE.stations.find(s => s.slug === STATE.lastStationSlug);
    let tzAbbrev = "PST";

    if (station) {
        if (station.prov === 'BC' && BC_EXCEPTIONS[station.town]) {
            tz = BC_EXCEPTIONS[station.town];
        } else if (TIMEZONES[station.prov]) {
            tz = TIMEZONES[station.prov];
        }

        if (tz === 'America/Edmonton' || tz === 'America/Yellowknife') tzAbbrev = "MST";
        else if (tz === 'America/Toronto') tzAbbrev = "EST";
        else if (tz === 'America/Halifax') tzAbbrev = "AST";
    }

    const now = new Date();

    try {
        const timeOptions = { hour: 'numeric', minute: '2-digit', hour12: true, timeZone: tz };
        const timeString = new Intl.DateTimeFormat('en-US', timeOptions).format(now);

        els.localTime.innerHTML = `${timeString} <span class="timezone-label">${tzAbbrev}</span>`;
    } catch (e) {
        // Fallback
        let hours = now.getHours();
        const minutes = now.getMinutes().toString().padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; // the hour '0' should be '12'

        els.localTime.innerHTML = `${hours}:${minutes} ${ampm} <span class="timezone-label">LCL</span>`;
    }
}

async function fetchWeather(townName) {
    if (!townName) return;

    // Clear out old while loading
    els.weatherTemp.textContent = "...";
    els.weatherIcon.textContent = "☀️"; // default 

    try {
        // wttr.in gives simple formats: %t = temp (e.g. +14°C), %c = condition icon
        // We URI encode the town name for safe parameters
        const url = `https://wttr.in/${encodeURIComponent(townName)}?format=%t+%c`;
        const res = await fetch(url);
        if (!res.ok) throw new Error("Weather Error");

        let text = await res.text();
        text = text.trim();

        // Expected " +14°C 🌤️ "
        // Let's parse out the temp and the icon simply 
        const parts = text.split(" ");
        if (parts.length >= 2) {
            let tempString = parts[0].replace("+", ""); // Remove + if present
            let iconString = parts.slice(1).join(" ").trim();
            els.weatherTemp.textContent = tempString;
            els.weatherIcon.textContent = iconString || "☁️";
        } else {
            els.weatherTemp.textContent = text;
        }
    } catch (e) {
        console.warn("Could not fetch weather data:", e);
        els.weatherTemp.textContent = "--°C";
        els.weatherIcon.textContent = "☁️";
    }
}

async function handleSpin() {
    if (STATE.isSpinning) return;
    STATE.isSpinning = true;
    els.spinBtn.disabled = true;

    // Stop current audio slightly
    if (STATE.isPlaying) els.audioPlayer.pause();

    els.stationDisplay.classList.add('spinning');

    // Simulate spinning effect by rapidly changing names
    const spinDuration = 2000;
    const intervalTime = 100;
    let elapsed = 0;

    const spinInterval = setInterval(() => {
        const randomTemp = STATE.stations[Math.floor(Math.random() * STATE.stations.length)];
        els.stationName.textContent = randomTemp.name;

        elapsed += intervalTime;
        if (elapsed >= spinDuration) {
            clearInterval(spinInterval);
            els.stationDisplay.classList.remove('spinning');

            // Final Selection
            const finalStation = getRandomStation();
            selectStation(finalStation);

            // Auto-play on spin resolve
            els.audioPlayer.play().catch(console.error);
            STATE.isPlaying = true;

            STATE.isSpinning = false;
            els.spinBtn.disabled = false;
        }
    }, intervalTime);
}

function togglePlayPlayer() {
    if (STATE.isPlaying) {
        els.audioPlayer.pause();
        STATE.isPlaying = false;
    } else {
        els.audioPlayer.play().catch(e => {
            console.error("Audio playback failed", e);
        });
        STATE.isPlaying = true;
    }
}

function updateAudioUI(isPlaying, isWaiting) {
    if (isPlaying) {
        els.playIcon.style.display = 'none';
        els.pauseIcon.style.display = 'block';
        els.statusIndicator.className = 'status-indicator playing';
    } else if (isWaiting) {
        els.playIcon.style.display = 'none';
        els.pauseIcon.style.display = 'block';
        els.statusIndicator.className = 'status-indicator loading';
    } else {
        els.playIcon.style.display = 'block';
        els.pauseIcon.style.display = 'none';
        els.statusIndicator.className = 'status-indicator';
    }
}

// Start
document.addEventListener('DOMContentLoaded', init);
