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
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    SENDER_EMAIL = 'your-email@gmail.com'
    SENDER_PASSWORD = 'your-password'
    ALERT_RECIPIENT_EMAIL = 'admin@example.com'

    # Logging settings
    LOG_STORAGE_TYPE = 'sqlite'  # 'sqlite' or 'json'
    LOG_RETENTION_DAYS = 30  # Days to keep logs