# Secure Vision

An AI-based smart surveillance system built with Python, Flask, OpenCV, and face recognition technology.

## Features

- Real-time video surveillance
- Face detection and recognition
- Motion detection
- Alert system (email/SMS)
- Logging and monitoring
- Web-based interface

## Tech Stack

- **Backend**: Python, Flask
- **Computer Vision**: OpenCV, face-recognition
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/kushalprasadjoshi-hackathons/secure-vision.git
   cd secure-vision
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Email Alert Configuration

The system supports optional email alerts when unknown faces are detected. To enable email alerts:

1. **Configure Email Settings** in `config.py`:
   ```python
   # Email alert settings
   ENABLE_EMAIL_ALERTS = True  # Set to True to enable email alerts
   SMTP_SERVER = 'smtp.gmail.com'
   SMTP_PORT = 587
   SENDER_EMAIL = 'your-email@gmail.com'
   SENDER_PASSWORD = 'your-app-password'  # Use app password for Gmail
   ALERT_RECIPIENT_EMAIL = 'admin@example.com'
   ```

2. **Gmail Setup** (if using Gmail):
   - Enable 2-factor authentication on your Gmail account
   - Generate an App Password: https://support.google.com/accounts/answer/185833
   - Use the App Password as `SENDER_PASSWORD`

3. **Test Configuration**:
   ```bash
   python test_system.py
   ```

### Email Alert Features

- **Automatic Triggers**: Emails are sent when unknown faces are detected
- **Snapshot Attachments**: Each alert includes a snapshot image of the detected person
- **Detailed Information**: Email includes timestamp, face location, and confidence score
- **Failure-Safe**: System continues to work even if email sending fails
- **Configurable**: Easily enable/disable and reconfigure without code changes

### Security Notes

- Never commit real email credentials to version control
- Use environment variables for sensitive configuration in production:
  ```python
  SENDER_EMAIL = os.environ.get('ALERT_EMAIL')
  SENDER_PASSWORD = os.environ.get('ALERT_EMAIL_PASSWORD')
  ```

## Performance Optimizations

The system has been optimized for real-time performance with the following improvements:

### ⚡ **Frame Processing Optimizations**
- **Frame Rate Limiting**: Configurable maximum FPS (default: 15) to reduce CPU usage
- **Frame Skipping**: Face recognition processes every Nth frame (configurable)
- **Batch Processing**: Limits face recognition to 5 faces per frame maximum
- **Optimized Detection**: Higher scale factor (1.3) and min neighbors (3) for faster Haar cascades

### 🧠 **Memory Management**
- **Face Encoding Cache**: LRU cache for repeated face recognition results
- **Automatic Cleanup**: Memory cleanup every 5 minutes
- **Buffer Management**: Limited frame buffers to prevent memory bloat

### 🎯 **CPU Usage Reduction**
- **Detection Parameter Tuning**: Optimized Haar cascade parameters for speed
- **Reduced Jitters**: Face encoding uses fewer jitters for faster processing
- **Background Subtraction**: Optimized MOG2 with shadow detection disabled
- **Threading**: Proper rate limiting in capture threads

### 📊 **Performance Monitoring**
- **Real-time Stats**: `/performance_stats` endpoint for monitoring
- **Processing Metrics**: Average processing time and FPS tracking
- **Configurable Limits**: All performance parameters configurable in `config.py`

### 🔧 **Configuration Options**

```python
# Performance settings in config.py
MAX_FRAME_RATE = 15                    # Maximum processing FPS
FRAME_SKIP_FACTOR = 2                  # Process every Nth frame for recognition
FACE_RECOGNITION_BATCH_SIZE = 5        # Max faces per frame
DETECTION_SCALE_FACTOR = 1.3           # Higher = faster detection
DETECTION_MIN_NEIGHBORS = 3            # Lower = more detections
ENABLE_FACE_CACHE = True              # Cache recognition results
FACE_CACHE_MAX_SIZE = 100             # Max cached faces
```

### 📈 **Expected Performance**
- **Face Detection**: 20-30 FPS on modern hardware
- **Face Recognition**: 5-15 FPS with caching
- **Memory Usage**: ~200-400MB with typical usage
- **CPU Usage**: 30-60% during active detection
```
├── static/
│   ├── css/
│   └── js/                # Static assets
├── surveillance/
│   ├── camera.py          # Camera handling
│   ├── detection.py       # Object and motion detection
│   ├── recognition.py     # Face recognition
│   ├── alert.py           # Alert system
│   └── logger.py          # Logging functionality
├── data/
│   ├── known_faces/       # Stored face encodings
│   └── logs/              # Log files
└── utils/                 # Utility functions
```

## Usage

1. Start the Flask server
2. Open your browser to `http://localhost:5000`
3. Use the web interface to start/stop surveillance
4. Known faces can be added via the recognition module

## Contributing

Contributions are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

_Thank you!_