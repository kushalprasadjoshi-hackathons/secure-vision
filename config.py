import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = True
    DATABASE_URI = 'sqlite:///data/logs.db'
    KNOWN_FACES_DIR = 'data/known_faces'
    LOGS_DIR = 'data/logs'
    CAMERA_INDEX = 0  # Default camera index
    FACE_RECOGNITION_TOLERANCE = 0.6