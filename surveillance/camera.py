import cv2
from config import Config

class Camera:
    def __init__(self):
        self.cap = None
        self.camera_index = Config.CAMERA_INDEX

    def start(self):
        """Start the camera feed."""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise ValueError("Unable to open camera")
        # Future: implement streaming or frame capture

    def capture_frame(self):
        """Capture a single frame from the camera."""
        if self.cap is None:
            raise ValueError("Camera not started")
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Failed to capture frame")
        return frame

    def stop(self):
        """Stop the camera feed."""
        if self.cap:
            self.cap.release()
            self.cap = None

    # Future: add methods for streaming frames to web interface