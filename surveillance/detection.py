import cv2
from surveillance.camera import Camera

class Detection:
    def __init__(self):
        self.camera = Camera()
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2()

    def detect_motion(self, frame):
        """Detect motion in the frame."""
        # Apply background subtraction
        fg_mask = self.background_subtractor.apply(frame)
        # Future: implement more sophisticated motion detection
        # For now, return True if any motion detected
        return cv2.countNonZero(fg_mask) > 0

    def detect_objects(self, frame):
        """Detect objects in the frame using OpenCV."""
        # Placeholder for object detection
        # Future: integrate with YOLO or other models
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Simple edge detection as placeholder
        edges = cv2.Canny(gray, 100, 200)
        return edges

    # Future: add face detection using OpenCV or integrate with recognition