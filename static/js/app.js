// Professional Surveillance Dashboard JavaScript

// Global state
const state = {
    isRunning: false,
    detectionEnabled: false,
    uptime: 0,
    statusCheckInterval: null,
    uptimeInterval: null,
    alertCheckInterval: null,
    lastAlertCount: 0,
    fullscreenMode: false,
    lastUpdate: new Date()
};

// DOM Elements
const videoFeed = document.getElementById('videoFeed');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const statusIndicator = document.getElementById('statusIndicator');
const feedStatus = document.getElementById('feedStatus');
const loadingSpinner = document.getElementById('loadingSpinner');
const autoRefreshCheckbox = document.getElementById('autoRefresh');

// Detection elements
const detectionToggleBtn = document.getElementById('detectionToggleBtn');
const detectFacesCheckbox = document.getElementById('detectFaces');
const detectEyesCheckbox = document.getElementById('detectEyes');
const drawAnnotationsCheckbox = document.getElementById('drawAnnotations');
const detectMotionCheckbox = document.getElementById('detectMotion');

// Status elements
const cameraStatus = document.getElementById('cameraStatus');
const aiStatus = document.getElementById('aiStatus');
const knownFacesCount = document.getElementById('knownFacesCount');
const facesDetected = document.getElementById('facesDetected');
const recognitionAccuracy = document.getElementById('recognitionAccuracy');
const eventsCount = document.getElementById('eventsCount');
const detectionStatus = document.getElementById('detectionStatus');
const recognitionStatus = document.getElementById('recognitionStatus');

// Stats elements
const fpsValue = document.getElementById('fpsValue');
const frameValue = document.getElementById('frameValue');
const uptimeValue = document.getElementById('uptimeValue');
const alertCount = document.getElementById('alertCount');
const lastUpdate = document.getElementById('lastUpdate');

// Table elements
const logsTableBody = document.getElementById('logsTableBody');

/**
 * Toggle fullscreen mode
 */
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().then(() => {
            state.fullscreenMode = true;
            showNotification('Entered fullscreen mode', 'info');
        }).catch(err => {
            console.error('Error entering fullscreen:', err);
        });
    } else {
        document.exitFullscreen().then(() => {
            state.fullscreenMode = false;
            showNotification('Exited fullscreen mode', 'info');
        }).catch(err => {
            console.error('Error exiting fullscreen:', err);
        });
    }
}

/**
 * Refresh all data
 */
function refreshData() {
    showNotification('Refreshing data...', 'info');

    // Refresh status
    updateStatus();

    // Refresh alerts and events
    checkAlerts();
    checkEvents();

    // Update last refresh time
    state.lastUpdate = new Date();
    updateLastUpdate();

    setTimeout(() => {
        showNotification('Data refreshed', 'success');
    }, 500);
}

/**
 * Clear all logs
 */
function clearLogs() {
    if (confirm('Are you sure you want to clear all logs? This action cannot be undone.')) {
        // Clear local display
        if (logsTableBody) {
            logsTableBody.innerHTML = `
                <tr class="no-logs-row">
                    <td colspan="4">
                        <i class="fas fa-inbox"></i>
                        <span>No events logged yet</span>
                    </td>
                </tr>
            `;
        }

        // Reset counters
        if (eventsCount) eventsCount.textContent = '0';
        if (alertCount) alertCount.textContent = '0';

        showNotification('Logs cleared', 'success');
    }
}

/**
 * Export logs to CSV
 */
function exportLogs() {
    const events = [];
    if (logsTableBody) {
        const rows = logsTableBody.querySelectorAll('tr');
        rows.forEach(row => {
            if (!row.classList.contains('no-logs-row')) {
                const cells = row.querySelectorAll('td');
                if (cells.length >= 4) {
                    events.push({
                        time: cells[0].textContent.trim(),
                        event: cells[1].textContent.trim(),
                        person: cells[2].textContent.trim(),
                        details: cells[3].textContent.trim()
                    });
                }
            }
        });
    }

    if (events.length === 0) {
        showNotification('No logs to export', 'warning');
        return;
    }

    // Create CSV content
    const csvContent = [
        ['Time', 'Event', 'Person', 'Details'],
        ...events.map(event => [event.time, event.event, event.person, event.details])
    ].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');

    // Download file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `secure-vision-logs-${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showNotification(`Exported ${events.length} log entries`, 'success');
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)}"></i>
        <span>${message}</span>
    `;

    // Add to page
    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => notification.classList.add('show'), 10);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

/**
 * Get notification icon based on type
 */
function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'warning': return 'exclamation-triangle';
        case 'error': return 'times-circle';
        case 'info':
        default: return 'info-circle';
    }
}

/**
 * Update last update time
 */
function updateLastUpdate() {
    if (lastUpdate) {
        lastUpdate.textContent = state.lastUpdate.toLocaleTimeString();
    }
}

/**
 * Toggle face detection
 */
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
            showNotification(`Face detection ${data.enabled ? 'enabled' : 'disabled'}`, 'success');
        } else {
            showNotification(data.status, 'error');
        }
    } catch (error) {
        console.error('Error toggling detection:', error);
        showNotification('Failed to toggle detection: ' + error.message, 'error');
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
        }
    } catch (error) {
        console.error('Error updating detection settings:', error);
    }
}

/**
 * Update detection UI
 */
function updateDetectionUI() {
    const detectionOptions = document.getElementById('detectionOptions');

    if (state.detectionEnabled) {
        if (detectionToggleBtn) {
            detectionToggleBtn.classList.add('active');
            detectionToggleBtn.innerHTML = '<i class="fas fa-eye"></i><span>Disable Detection</span>';
        }
        if (detectionOptions) detectionOptions.style.display = 'flex';

        if (detectionStatus) {
            detectionStatus.classList.add('active');
            detectionStatus.innerHTML = '<i class="fas fa-eye"></i><span>Detection: ACTIVE</span>';
        }
    } else {
        if (detectionToggleBtn) {
            detectionToggleBtn.classList.remove('active');
            detectionToggleBtn.innerHTML = '<i class="fas fa-eye"></i><span>Enable Detection</span>';
        }
        if (detectionOptions) detectionOptions.style.display = 'none';

        if (detectionStatus) {
            detectionStatus.classList.remove('active');
            detectionStatus.innerHTML = '<i class="fas fa-eye"></i><span>Detection: OFF</span>';
        }
    }
}

/**
 * Update status display
 */
async function updateStatus() {
    try {
        const response = await fetch('/camera_status');
        const data = await response.json();

        // Update camera status
        if (cameraStatus) {
            cameraStatus.textContent = data.is_active ? 'Active' : 'Offline';
            cameraStatus.className = data.is_active ? 'text-success' : 'text-danger';
        }

        // Update AI status
        if (aiStatus) {
            aiStatus.textContent = data.detection_enabled ? 'Active' : 'Inactive';
            aiStatus.className = data.detection_enabled ? 'text-success' : 'text-danger';
        }

        // Update known faces count
        if (knownFacesCount) {
            knownFacesCount.textContent = data.known_faces_count || '0';
        }

        // Update faces detected
        if (facesDetected) {
            facesDetected.textContent = data.faces_detected || '0';
        }

        // Update recognition accuracy
        if (recognitionAccuracy) {
            recognitionAccuracy.textContent = data.recognition_tolerance ?
                `${((1 - data.recognition_tolerance) * 100).toFixed(1)}%` : 'N/A';
        }

        // Update FPS
        if (fpsValue) {
            fpsValue.textContent = data.fps ? data.fps.toFixed(1) : '0';
        }

        // Update frame count
        if (frameValue) {
            frameValue.textContent = data.frame_count || '0';
        }

        // Update uptime
        if (uptimeValue) {
            const uptime = data.uptime || 0;
            const hours = Math.floor(uptime / 3600);
            const minutes = Math.floor((uptime % 3600) / 60);
            const seconds = uptime % 60;
            uptimeValue.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }

        // Update recognition status
        if (recognitionStatus) {
            const isActive = data.recognition_available && data.detection_enabled;
            recognitionStatus.classList.toggle('active', isActive);
            recognitionStatus.innerHTML = `<i class="fas fa-user-check"></i><span>Recognition: ${isActive ? 'ACTIVE' : 'OFF'}</span>`;
        }

    } catch (error) {
        console.error('Error updating status:', error);
    }
}

/**
 * Check for new alerts
 */
async function checkAlerts() {
    try {
        const response = await fetch('/alerts');
        const data = await response.json();

        if (data.alerts && data.alerts.length > 0) {
            const newAlerts = data.alerts.filter(alert => {
                return data.alerts.indexOf(alert) < 3; // Show last 3 alerts
            });

            if (newAlerts.length > state.lastAlertCount) {
                // Show popup alert for new unknown person detections
                const unknownAlerts = newAlerts.filter(alert => alert.type === 'unknown_person');
                if (unknownAlerts.length > 0) {
                    const latestAlert = unknownAlerts[unknownAlerts.length - 1];
                    showNotification(`🚨 Unknown person detected at ${latestAlert.timestamp}`, 'warning');
                }
                state.lastAlertCount = newAlerts.length;
            }

            // Update alerts display
            updateAlertsDisplay(data.alerts);

            // Update alert count
            if (alertCount) {
                alertCount.textContent = data.alerts.length;
            }
        } else {
            if (alertCount) {
                alertCount.textContent = '0';
            }
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

            // Update events count
            if (eventsCount) {
                eventsCount.textContent = data.events.length;
            }
        } else {
            if (eventsCount) {
                eventsCount.textContent = '0';
            }
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
        if (alertContainer) {
            alertContainer.innerHTML = `
                <div class="no-alerts">
                    <i class="fas fa-shield-alt"></i>
                    <span>No security alerts</span>
                </div>
            `;
        }
        return;
    }

    if (alertContainer) {
        alertContainer.innerHTML = '';

        // Show last 5 alerts
        const recentAlerts = alerts.slice(-5).reverse();

        recentAlerts.forEach(alert => {
            const alertItem = document.createElement('div');
            alertItem.className = `alert-item alert-${alert.type === 'unknown_person' ? 'warning' : 'info'}`;

            const time = new Date(alert.timestamp).toLocaleTimeString();
            alertItem.innerHTML = `
                <div class="alert-content">
                    <div class="alert-time">${time}</div>
                    <div class="alert-message">
                        ${alert.type === 'unknown_person' ? '🚨 Unknown person detected' : alert.type}
                    </div>
                </div>
            `;

            alertContainer.appendChild(alertItem);
        });
    }
}

/**
 * Update events display in the logs table
 */
function updateEventsDisplay(events) {
    if (!logsTableBody) return;

    if (!events || events.length === 0) {
        logsTableBody.innerHTML = `
            <tr class="no-logs-row">
                <td colspan="4">
                    <i class="fas fa-inbox"></i>
                    <span>No events logged yet</span>
                </td>
            </tr>
        `;
        return;
    }

    logsTableBody.innerHTML = '';

    // Show last 20 events
    const recentEvents = events.slice(0, 20);

    recentEvents.forEach(event => {
        const row = document.createElement('tr');
        row.className = `event-${event.event_type?.replace(/_/g, '-') || 'unknown'}`;

        const timestamp = event.timestamp ? new Date(event.timestamp).toLocaleString() : 'Unknown time';
        const eventType = event.event_type || 'Unknown event';
        const personName = event.person_name || 'Unknown';
        const alertStatus = event.alert_status || 'none';

        // Format event type for display
        const displayEventType = eventType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

        // Format details
        let details = '';
        if (event.details && typeof event.details === 'object') {
            const detailParts = [];
            if (event.details.confidence) detailParts.push(`Conf: ${(event.details.confidence * 100).toFixed(1)}%`);
            if (event.details.face_location) detailParts.push('Face detected');
            if (event.details.cooldown_seconds) detailParts.push(`Cooldown: ${event.details.cooldown_seconds}s`);
            details = detailParts.join(' | ');
        }

        row.innerHTML = `
            <td>${timestamp}</td>
            <td>${displayEventType}</td>
            <td>${personName}</td>
            <td>${details || 'No details'}</td>
        `;

        logsTableBody.appendChild(row);
    });
}

/**
 * Start surveillance
 */
async function startSurveillance() {
    try {
        if (startBtn) startBtn.disabled = true;
        if (loadingSpinner) loadingSpinner.style.display = 'flex';
        if (feedStatus) feedStatus.innerHTML = '<i class="fas fa-info-circle"></i><span>Initializing camera...</span>';

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
            showNotification('Surveillance system started', 'success');
            if (feedStatus) feedStatus.innerHTML = '<i class="fas fa-play-circle"></i><span>Live feed active</span>';
        } else {
            showNotification(data.status, 'error');
            if (feedStatus) feedStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i><span>Failed to start system</span>';
            if (loadingSpinner) loadingSpinner.style.display = 'none';
        }
    } catch (error) {
        console.error('Error starting surveillance:', error);
        showNotification('Failed to start surveillance: ' + error.message, 'error');
        if (feedStatus) feedStatus.innerHTML = '<i class="fas fa-times-circle"></i><span>Connection error</span>';
        if (startBtn) startBtn.disabled = false;
        if (loadingSpinner) loadingSpinner.style.display = 'none';
    }
}

/**
 * Stop surveillance
 */
async function stopSurveillance() {
    try {
        if (stopBtn) stopBtn.disabled = true;
        if (feedStatus) feedStatus.innerHTML = '<i class="fas fa-stop-circle"></i><span>Stopping system...</span>';

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
            showNotification('Surveillance system stopped', 'success');
            if (feedStatus) feedStatus.innerHTML = '<i class="fas fa-pause-circle"></i><span>System offline</span>';
            if (videoFeed) videoFeed.src = '';
        } else {
            showNotification(data.status, 'error');
        }
    } catch (error) {
        console.error('Error stopping surveillance:', error);
        showNotification('Failed to stop surveillance: ' + error.message, 'error');
    }
}

/**
 * Start video stream
 */
function startVideoStream() {
    // Add timestamp to force refresh and prevent caching
    if (videoFeed) {
        videoFeed.src = '/video_feed?t=' + Date.now();
        videoFeed.style.display = 'block';
    }
    if (loadingSpinner) loadingSpinner.style.display = 'none';
}

/**
 * Stop video stream
 */
function stopVideoStream() {
    if (videoFeed) videoFeed.style.display = 'none';
}

/**
 * Start status checks
 */
function startStatusChecks() {
    if (state.statusCheckInterval) {
        clearInterval(state.statusCheckInterval);
    }
    state.statusCheckInterval = setInterval(updateStatus, 2000); // Update every 2 seconds
    updateStatus(); // Update immediately
}

/**
 * Stop status checks
 */
function stopStatusChecks() {
    if (state.statusCheckInterval) {
        clearInterval(state.statusCheckInterval);
        state.statusCheckInterval = null;
    }
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

/**
 * Update UI elements
 */
function updateUI() {
    if (state.isRunning) {
        if (startBtn) startBtn.disabled = true;
        if (stopBtn) stopBtn.disabled = false;
        if (statusIndicator) {
            statusIndicator.classList.add('active');
            const statusText = statusIndicator.querySelector('.status-text');
            if (statusText) statusText.textContent = 'SYSTEM ACTIVE';
        }
    } else {
        if (startBtn) startBtn.disabled = false;
        if (stopBtn) stopBtn.disabled = true;
        if (statusIndicator) {
            statusIndicator.classList.remove('active');
            const statusText = statusIndicator.querySelector('.status-text');
            if (statusText) statusText.textContent = 'SYSTEM OFFLINE';
        }
    }
}

/**
 * Handle auto refresh checkbox
 */
if (autoRefreshCheckbox) {
    autoRefreshCheckbox.addEventListener('change', (e) => {
        if (e.target.checked && state.isRunning) {
            startVideoStream();
        }
    });
}

/**
 * Handle detection checkboxes
 */
if (detectFacesCheckbox) detectFacesCheckbox.addEventListener('change', updateDetectionSettings);
if (detectEyesCheckbox) detectEyesCheckbox.addEventListener('change', updateDetectionSettings);
if (drawAnnotationsCheckbox) drawAnnotationsCheckbox.addEventListener('change', updateDetectionSettings);
if (detectMotionCheckbox) detectMotionCheckbox.addEventListener('change', updateDetectionSettings);

/**
 * Initialize application
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('Secure Vision Dashboard initialized');
    updateUI();
    updateDetectionUI();
    updateLastUpdate();
    showNotification('Dashboard loaded successfully', 'success');
});