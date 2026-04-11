// Global state
const state = {
    isRunning: false,
    detectionEnabled: false,
    uptime: 0,
    statusCheckInterval: null,
    uptimeInterval: null,
    alertCheckInterval: null,
    lastAlertCount: 0
};

// DOM Elements
const videoFeed = document.getElementById('videoFeed');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const statusIndicator = document.getElementById('statusIndicator');
const feedStatus = document.getElementById('feedStatus');
const loadingSpinner = document.getElementById('loadingSpinner');
const autoRefreshCheckbox = document.getElementById('autoRefresh');
const statusDot = statusIndicator?.querySelector('.status-dot');
const statusText = statusIndicator?.querySelector('.status-text');

// Detection elements
const detectionToggleBtn = document.getElementById('detectionToggleBtn');
const detectFacesCheckbox = document.getElementById('detectFaces');
const detectEyesCheckbox = document.getElementById('detectEyes');
const drawAnnotationsCheckbox = document.getElementById('drawAnnotations');
const detectMotionCheckbox = document.getElementById('detectMotion');

/**
 * Check for new alerts
 */
async function checkAlerts() {
    try {
        const response = await fetch('/alerts');
        const data = await response.json();

        if (data.alerts && data.alerts.length > 0) {
            const newAlerts = data.alerts.filter(alert => {
                // Simple check for new alerts (in production, use timestamps)
                return data.alerts.indexOf(alert) < 3; // Show last 3 alerts
            });

            if (newAlerts.length > state.lastAlertCount) {
                // Show popup alert for new unknown person detections
                const unknownAlerts = newAlerts.filter(alert => alert.type === 'unknown_person');
                if (unknownAlerts.length > 0) {
                    const latestAlert = unknownAlerts[unknownAlerts.length - 1];
                    showAlert(`🚨 Unknown person detected at ${latestAlert.timestamp}`, 'warning');
                    addLog(`Unknown person detected at ${latestAlert.timestamp}`, 'warning');
                }
                state.lastAlertCount = newAlerts.length;
            }

            // Update alerts display
            updateAlertsDisplay(data.alerts);
        }
    } catch (error) {
        console.error('Error checking alerts:', error);
    }
}

/**
 * Check for new events and update logs
 */
async function checkEvents() {
    try {
        const response = await fetch('/events');
        const data = await response.json();

        if (data.events && data.events.length > 0) {
            updateEventsDisplay(data.events);
        }
    } catch (error) {
        console.error('Error checking events:', error);
    }
}

/**
 * Update alerts display in the dashboard
 */
function updateAlertsDisplay(alerts) {
    const alertContainer = document.getElementById('alertContainer');

    if (!alerts || alerts.length === 0) {
        alertContainer.innerHTML = '<p class="no-alerts">No alerts</p>';
        return;
    }

    alertContainer.innerHTML = '';

    // Show last 5 alerts
    const recentAlerts = alerts.slice(-5).reverse();

    recentAlerts.forEach(alert => {
        const alertItem = document.createElement('div');
        alertItem.className = `alert-item alert-${alert.type === 'unknown_person' ? 'warning' : 'info'}`;

        const time = new Date(alert.timestamp).toLocaleTimeString();
        alertItem.innerHTML = `
            <div class="alert-time">${time}</div>
            <div class="alert-message">
                ${alert.type === 'unknown_person' ? '🚨 Unknown person detected' : alert.type}
            </div>
        `;

        alertContainer.appendChild(alertItem);
    });
}

/**
 * Update events display in the logs section
 */
function updateEventsDisplay(events) {
    const logsContainer = document.getElementById('logsContainer');

    if (!events || events.length === 0) {
        logsContainer.innerHTML = '<p class="no-logs">No activity logged</p>';
        return;
    }

    logsContainer.innerHTML = '';

    // Show last 20 events
    const recentEvents = events.slice(0, 20);

    recentEvents.forEach(event => {
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';

        const timestamp = event.timestamp ? new Date(event.timestamp).toLocaleString() : 'Unknown time';
        const personName = event.person_name || 'Unknown';
        const eventType = event.event_type || 'Unknown event';
        const alertStatus = event.alert_status || 'none';

        let icon = '📝';
        if (eventType === 'person_recognized') icon = '👤';
        else if (eventType === 'unknown_person_detected') icon = '🚨';
        else if (eventType === 'system_start') icon = '▶️';
        else if (eventType === 'system_stop') icon = '⏹️';

        logEntry.innerHTML = `
            <div class="log-time">${timestamp}</div>
            <div class="log-content">
                <span class="log-icon">${icon}</span>
                <span class="log-message">
                    ${eventType.replace('_', ' ')} - ${personName}
                    ${alertStatus !== 'none' ? ` (${alertStatus})` : ''}
                </span>
            </div>
        `;

        logsContainer.appendChild(logEntry);
    });
}

/**
 * Update alerts display in the dashboard
 */
function updateAlertsDisplay(alerts) {
    const alertContainer = document.getElementById('alertContainer');

    if (!alerts || alerts.length === 0) {
        alertContainer.innerHTML = '<p class="no-alerts">No alerts</p>';
        return;
    }

    alertContainer.innerHTML = '';

    // Show last 5 alerts
    const recentAlerts = alerts.slice(-5).reverse();

    recentAlerts.forEach(alert => {
        const alertItem = document.createElement('div');
        alertItem.className = `alert-item alert-${alert.type === 'unknown_person' ? 'warning' : 'info'}`;

        const time = new Date(alert.timestamp).toLocaleTimeString();
        alertItem.innerHTML = `
            <div class="alert-time">${time}</div>
            <div class="alert-message">
                ${alert.type === 'unknown_person' ? '🚨 Unknown person detected' : alert.type}
            </div>
        `;

        alertContainer.appendChild(alertItem);
    });
}

/**
 * Start alert checking
 */
function startAlertChecking() {
    if (state.alertCheckInterval) {
        clearInterval(state.alertCheckInterval);
    }
    state.alertCheckInterval = setInterval(() => {
        checkAlerts();
        checkEvents();
    }, 5000); // Check every 5 seconds
    checkAlerts(); // Check immediately
    checkEvents(); // Check immediately
}

/**
 * Stop alert checking
 */
function stopAlertChecking() {
    if (state.alertCheckInterval) {
        clearInterval(state.alertCheckInterval);
        state.alertCheckInterval = null;
    }
}
async function toggleDetection() {
    try {
        const newState = !state.detectionEnabled;
        
        const response = await fetch('/detection/toggle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ enabled: newState })
        });

        const data = await response.json();

        if (data.success) {
            state.detectionEnabled = data.enabled;
            updateDetectionUI();
            addLog(`Face detection ${data.enabled ? 'enabled' : 'disabled'}`, 'info');
        } else {
            showAlert(data.status, 'error');
        }
    } catch (error) {
        console.error('Error toggling detection:', error);
        showAlert('Failed to toggle detection: ' + error.message, 'error');
    }
}

/**
 * Update detection settings
 */
async function updateDetectionSettings() {
    try {
        const settings = {
            detect_faces: detectFacesCheckbox?.checked ?? true,
            detect_eyes: detectEyesCheckbox?.checked ?? false,
            draw_annotations: drawAnnotationsCheckbox?.checked ?? true,
            detect_motion: detectMotionCheckbox?.checked ?? false
        };

        const response = await fetch('/detection/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(settings)
        });

        const data = await response.json();

        if (data.success) {
            console.log('Detection settings updated');
            addLog('Detection settings updated', 'info');
        }
    } catch (error) {
        console.error('Error updating detection settings:', error);
    }
}

/**
 * Update detection UI
 */
function updateDetectionUI() {
    const detectionOptions = document.querySelector('.detection-options');
    const detectionStats = document.querySelector('.detection-stats');
    
    if (state.detectionEnabled) {
        detectionToggleBtn?.classList.add('active');
        detectionToggleBtn.textContent = '🔍 Disable';
        if (detectionOptions) detectionOptions.style.display = 'block';
        if (detectionStats) detectionStats.style.display = 'block';
        addLog('Detection options visible', 'info');
    } else {
        detectionToggleBtn?.classList.remove('active');
        detectionToggleBtn.textContent = '🔍 Enable';
        if (detectionOptions) detectionOptions.style.display = 'none';
        if (detectionStats) detectionStats.style.display = 'none';
    }
}

/**
 * Start surveillance
 */
async function startSurveillance() {
    try {
        startBtn.disabled = true;
        loadingSpinner.style.display = 'block';
        feedStatus.textContent = 'Starting...';

        const response = await fetch('/start_surveillance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            state.isRunning = true;
            updateUI();
            startVideoStream();
            startStatusChecks();
            startAlertChecking();
            addLog('Surveillance started', 'info');
            feedStatus.textContent = 'Live Feed Active';
        } else {
            showAlert(data.status, 'error');
            feedStatus.textContent = 'Failed to start';
            loadingSpinner.style.display = 'none';
        }
    } catch (error) {
        console.error('Error starting surveillance:', error);
        showAlert('Failed to start surveillance: ' + error.message, 'error');
        feedStatus.textContent = 'Connection error';
        startBtn.disabled = false;
        loadingSpinner.style.display = 'none';
    }
}

/**
 * Stop surveillance
 */
async function stopSurveillance() {
    try {
        stopBtn.disabled = true;
        feedStatus.textContent = 'Stopping...';

        const response = await fetch('/stop_surveillance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            state.isRunning = false;
            updateUI();
            stopVideoStream();
            stopStatusChecks();
            stopAlertChecking();
            addLog('Surveillance stopped', 'info');
            feedStatus.textContent = 'Offline';
            videoFeed.src = '';
        } else {
            showAlert(data.status, 'error');
        }
    } catch (error) {
        console.error('Error stopping surveillance:', error);
        showAlert('Failed to stop surveillance: ' + error.message, 'error');
    }
}

/**
 * Start video stream
 */
function startVideoStream() {
    // Add timestamp to force refresh and prevent caching
    videoFeed.src = '/video_feed?t=' + Date.now();
    videoFeed.style.display = 'block';
    loadingSpinner.style.display = 'none';
}

/**
 * Stop video stream
 */
function stopVideoStream() {
    videoFeed.src = '';
}

/**
 * Start periodic status checks
 */
function startStatusChecks() {
    // Update status every 500ms
    state.statusCheckInterval = setInterval(updateStatus, 500);
    
    // Start uptime counter
    state.uptime = 0;
    state.uptimeInterval = setInterval(() => {
        state.uptime++;
        updateUptimeDisplay();
    }, 1000);
}

/**
 * Stop status checks
 */
function stopStatusChecks() {
    if (state.statusCheckInterval) {
        clearInterval(state.statusCheckInterval);
        state.statusCheckInterval = null;
    }
    if (state.uptimeInterval) {
        clearInterval(state.uptimeInterval);
        state.uptimeInterval = null;
    }
}

/**
 * Update camera status from API
 */
async function updateStatus() {
    try {
        const response = await fetch('/camera_status');
        const data = await response.json();

        if (data.is_active) {
            document.getElementById('cameraStatus').textContent = 'Online';
            document.getElementById('statusFPS').textContent = data.fps.toFixed(2);
            document.getElementById('statusFrames').textContent = data.frame_count;
            
            // Update detection stats
            if (data.detection_enabled) {
                document.getElementById('detectionStatus').textContent = 'Enabled';
                document.getElementById('facesDetected').textContent = data.faces_detected || 0;
                document.getElementById('detectionParams').textContent = 
                    `Scale: ${data.scale_factor || 1.1}, Neighbors: ${data.min_neighbors || 5}`;
                
                // Update recognition stats
                if (data.recognition_enabled && data.recognition_available) {
                    document.getElementById('recognitionStatus').textContent = 'Enabled';
                    document.getElementById('knownFacesCount').textContent = data.known_faces_count || 0;
                    document.getElementById('recognitionTolerance').textContent = data.recognition_tolerance || 0.6;
                } else {
                    document.getElementById('recognitionStatus').textContent = 'Disabled';
                    document.getElementById('knownFacesCount').textContent = 'N/A';
                    document.getElementById('recognitionTolerance').textContent = 'N/A';
                }
            } else {
                document.getElementById('detectionStatus').textContent = 'Disabled';
                document.getElementById('facesDetected').textContent = 'N/A';
                document.getElementById('detectionParams').textContent = 'N/A';
                document.getElementById('recognitionStatus').textContent = 'N/A';
                document.getElementById('knownFacesCount').textContent = 'N/A';
                document.getElementById('recognitionTolerance').textContent = 'N/A';
            }
            
            updateStatusIndicator(true);
        } else {
            document.getElementById('cameraStatus').textContent = 'Offline';
            document.getElementById('detectionStatus').textContent = 'Offline';
            document.getElementById('facesDetected').textContent = 'N/A';
            document.getElementById('detectionParams').textContent = 'N/A';
            updateStatusIndicator(false);
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

/**
 * Update uptime display
 */
function updateUptimeDisplay() {
    const hours = Math.floor(state.uptime / 3600);
    const minutes = Math.floor((state.uptime % 3600) / 60);
    const seconds = state.uptime % 60;
    
    const uptimeStr = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    document.getElementById('statusUptime').textContent = uptimeStr;
}

/**
 * Update UI based on state
 */
function updateUI() {
    if (state.isRunning) {
        startBtn.disabled = true;
        stopBtn.disabled = false;
        statusDot?.classList.add('active');
        statusText.textContent = 'Online';
    } else {
        startBtn.disabled = false;
        stopBtn.disabled = true;
        statusDot?.classList.remove('active');
        statusText.textContent = 'Offline';
        document.getElementById('cameraStatus').textContent = 'Offline';
        document.getElementById('statusFPS').textContent = '0.00';
        document.getElementById('statusFrames').textContent = '0';
        document.getElementById('statusUptime').textContent = '00:00:00';
    }
}

/**
 * Update status indicator
 */
function updateStatusIndicator(isActive) {
    if (isActive) {
        statusDot?.classList.add('active');
    } else {
        statusDot?.classList.remove('active');
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    const alertItem = document.createElement('div');
    alertItem.className = `alert-item alert-${type}`;
    alertItem.textContent = message;
    
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alertItem);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertContainer.contains(alertItem)) {
            alertContainer.innerHTML = '<p class="no-alerts">No alerts</p>';
        }
    }, 5000);
}

/**
 * Add log entry
 */
function addLog(message, type = 'info') {
    const logsContainer = document.getElementById('logsContainer');
    
    if (logsContainer.querySelector('.no-logs')) {
        logsContainer.innerHTML = '';
    }
    
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    
    logEntry.innerHTML = `
        <div class="log-time">${timeStr}</div>
        <div>${message}</div>
    `;
    
    logsContainer.insertBefore(logEntry, logsContainer.firstChild);
    
    // Keep only last 20 logs
    const logs = logsContainer.querySelectorAll('.log-entry');
    if (logs.length > 20) {
        logs[logs.length - 1].remove();
    }
}

/**
 * Handle auto refresh checkbox
 */
autoRefreshCheckbox?.addEventListener('change', (e) => {
    if (e.target.checked && state.isRunning) {
        startVideoStream();
    }
});

/**
 * Handle detection checkboxes
 */
detectFacesCheckbox?.addEventListener('change', updateDetectionSettings);
detectEyesCheckbox?.addEventListener('change', updateDetectionSettings);
drawAnnotationsCheckbox?.addEventListener('change', updateDetectionSettings);
detectMotionCheckbox?.addEventListener('change', updateDetectionSettings);

/**
 * Initialize application
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('Secure Vision Dashboard initialized');
    updateUI();
    loadDetectionSettings();
    addLog('Dashboard loaded', 'info');
});

/**
 * Load current detection settings
 */
async function loadDetectionSettings() {
    try {
        const response = await fetch('/detection/settings');
        const settings = await response.json();
        
        // Update UI with current settings
        updateDetectionUI(settings.enabled);
        
        // Update checkboxes
        document.getElementById('detectEyes').checked = settings.detect_eyes || false;
        document.getElementById('detectMotion').checked = settings.detect_motion || false;
        document.getElementById('drawAnnotations').checked = settings.draw_annotations !== false;
        
    } catch (error) {
        console.error('Error loading detection settings:', error);
    }
}

/**
 * Cleanup on page unload
 */
window.addEventListener('beforeunload', () => {
    if (state.isRunning) {
        stopSurveillance();
    }
});