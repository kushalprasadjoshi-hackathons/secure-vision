// Global state
const state = {
    isRunning: false,
    detectionEnabled: false,
    uptime: 0,
    statusCheckInterval: null,
    uptimeInterval: null
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
            } else {
                document.getElementById('detectionStatus').textContent = 'Disabled';
                document.getElementById('facesDetected').textContent = 'N/A';
                document.getElementById('detectionParams').textContent = 'N/A';
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