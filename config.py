import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = True
    DATABASE_URI = 'sqlite:///data/logs.db'
    KNOWN_FACES_DIR = 'data/known_faces'
    LOGS_DIR = 'data/logs'
    CAMERA_INDEX = 0  # Default camera index
    FACE_RECOGNITION_TOLERANCE = 0.6

    # Alert system settings
    ALERT_COOLDOWN_SECONDS = 30  # Minimum time between alerts
    SNAPSHOTS_DIR = os.path.join(LOGS_DIR, 'snapshots')
    ALERTS_LOG_FILE = os.path.join(LOGS_DIR, 'alerts.log')

    # Email alert settings (configure these for email alerts)
    ENABLE_EMAIL_ALERTS = False  # Set to True to enable email alerts
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    SENDER_EMAIL = 'your-email@gmail.com'
    SENDER_PASSWORD = 'your-app-password'  # Use app password for Gmail
    ALERT_RECIPIENT_EMAIL = 'admin@example.com'
    EMAIL_SUBJECT_TEMPLATE = 'Security Alert: Unknown Person Detected - {timestamp}'

    # Performance optimization settings
    MAX_FRAME_RATE = 15  # Maximum processing FPS (reduce CPU usage)
    FRAME_SKIP_FACTOR = 2  # Process every Nth frame for recognition (1 = every frame, 2 = every other frame)
    FACE_RECOGNITION_BATCH_SIZE = 5  # Maximum faces to process per frame
    DETECTION_SCALE_FACTOR = 1.3  # Higher = faster but less accurate detection
    DETECTION_MIN_NEIGHBORS = 3  # Lower = more detections but more false positives
    ENABLE_FACE_CACHE = True  # Cache face encodings in memory
    # Logging settings
    LOG_STORAGE_TYPE = 'sqlite'  # 'sqlite' or 'json'
    LOG_RETENTION_DAYS = 30  # Days to keep logs