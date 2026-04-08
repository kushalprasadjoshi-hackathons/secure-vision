# Surveillance module
from .camera import Camera
from .detection import Detection
from .alert import Alert
from .logger import Logger

# Optional imports - face_recognition may not be available on all systems/Python versions
try:
    from .recognition import Recognition
except ImportError:
    Recognition = None

__all__ = ['Camera', 'Detection', 'Recognition', 'Alert', 'Logger']
