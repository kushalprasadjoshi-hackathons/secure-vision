import cv2
import threading
import logging
from config import Config
from collections import deque
import time
from surveillance.detection import Detection

logger = logging.getLogger(__name__)

class Camera:
    def __init__(self, buffer_size=1, enable_detection=True):
        self.cap = None
        self.camera_index = Config.CAMERA_INDEX
        self.is_running = False
        self.frame_buffer = deque(maxlen=buffer_size)
        self.lock = threading.Lock()
        self.thread = None
        self.fps = 30
        self.frame_count = 0
        self.start_time = None
        
        # Detection system
        self.enable_detection = enable_detection
        self.detection = Detection() if enable_detection else None
        self.detection_enabled = False  # Runtime toggle
        
        # Detection stats
        self.detection_stats = {
            'faces_detected': 0,
            'motion_detected': False,
            'last_detection_time': 0
        }

    def start(self):
        """Start the camera feed and capture thread."""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            # Set camera properties for optimization
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer for real-time performance
            
            if not self.cap.isOpened():
                raise ValueError("Unable to open camera device")
            
            self.is_running = True
            self.start_time = time.time()
            self.frame_count = 0
            
            # Start capture thread
            self.thread = threading.Thread(target=self._capture_frames, daemon=True)
            self.thread.start()
            logger.info(f"Camera started successfully on device {self.camera_index}")
            
        except Exception as e:
            logger.error(f"Failed to start camera: {e}")
            self.is_running = False
            if self.cap:
                self.cap.release()
            raise

    def start(self):
        """Start the camera feed and capture thread."""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            # Set camera properties for optimization
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer for real-time performance
            
            if not self.cap.isOpened():
                raise ValueError("Unable to open camera device")
            
            self.is_running = True
            self.start_time = time.time()
            self.frame_count = 0
            
            # Start capture thread
            self.thread = threading.Thread(target=self._capture_frames, daemon=True)
            self.thread.start()
            logger.info(f"Camera started successfully on device {self.camera_index}")
            
        except Exception as e:
            logger.error(f"Failed to start camera: {e}")
            self.is_running = False
            if self.cap:
                self.cap.release()
            raise

    def _capture_frames(self):
        """Continuously capture frames in a separate thread."""
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                
                if not ret:
                    logger.warning("Failed to capture frame from camera")
                    time.sleep(0.1)  # Brief pause before retry
                    continue
                
                # Optimize frame for streaming
                frame = cv2.resize(frame, (640, 480))
                
                # Store frame in buffer (thread-safe)
                # Detection processing is done in the streaming pipeline for better control
                with self.lock:
                    self.frame_buffer.append(frame)
                
                self.frame_count += 1
                
            except Exception as e:
                logger.error(f"Error in capture thread: {e}")
                time.sleep(0.1)

    def get_frame(self):
        """Get the latest frame from the buffer."""
        try:
            with self.lock:
                if len(self.frame_buffer) > 0:
                    return self.frame_buffer[-1]
            logger.warning("No frame available in buffer")
            return None
        except Exception as e:
            logger.error(f"Error retrieving frame: {e}")
            return None

    def encode_frame(self, frame, encode_param=None):
        """Encode frame to JPEG bytes for streaming."""
        try:
            if encode_param is None:
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
            
            ret, buffer = cv2.imencode('.jpg', frame, encode_param)
            if ret:
                return buffer.tobytes()
            else:
                logger.error("Failed to encode frame")
                return None
        except Exception as e:
            logger.error(f"Error encoding frame: {e}")
            return None

    def get_fps(self):
        """Get current FPS."""
        if self.start_time and self.frame_count > 0:
            elapsed = time.time() - self.start_time
            return self.frame_count / elapsed if elapsed > 0 else 0
        return 0

    def is_active(self):
        """Check if camera is active and capturing."""
        return self.is_running and self.thread and self.thread.is_alive()

    def stop(self):
        """Stop the camera feed and capture thread."""
        try:
            self.is_running = False
            
            if self.thread:
                self.thread.join(timeout=2)
            
            if self.cap:
                self.cap.release()
            
            logger.info("Camera stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping camera: {e}")
        finally:
            self.cap = None
            self.thread = None

    def release(self):
        """Release camera resources (alias for stop)."""
        self.stop()

    def enable_detection(self, enabled=True):
        """Enable or disable face detection."""
        if self.detection:
            self.detection_enabled = enabled
            logger.info(f"Face detection {'enabled' if enabled else 'disabled'}")
            return True
        else:
            logger.warning("Detection system not available")
            return False

    def is_detection_enabled(self):
        """Check if detection is enabled."""
        return self.detection_enabled and self.detection is not None

    def get_detection_stats(self):
        """Get current detection statistics."""
        if self.detection:
            stats = self.detection.get_stats()
            stats.update(self.detection_stats)
            return stats
        return self.detection_stats

    def get_status(self):
        """Get camera status information."""
        resolution = "Unknown"
        if self.cap and self.cap.isOpened():
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            resolution = f"{width}x{height}"
        
        return {
            'active': self.is_active(),
            'fps': self.get_fps(),
            'frame_count': self.frame_count,
            'detection_enabled': self.is_detection_enabled(),
            'resolution': resolution,
            'camera_index': self.camera_index
        }

    def set_detection_params(self, scale_factor=None, min_neighbors=None):
        """Update detection parameters."""
        if self.detection:
            if scale_factor is not None:
                self.detection.scale_factor = scale_factor
            if min_neighbors is not None:
                self.detection.min_neighbors = min_neighbors
            logger.info(f"Detection parameters updated: scale_factor={self.detection.scale_factor}, min_neighbors={self.detection.min_neighbors}")
            return True
        return False