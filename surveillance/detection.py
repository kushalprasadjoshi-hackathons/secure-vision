import cv2
import logging
import os
import time
import threading
from collections import deque
from surveillance.recognition import Recognition
from surveillance.alert import Alert
from surveillance.logger import Logger
from config import Config

logger = logging.getLogger(__name__)

class Detection:
    def __init__(self, scale_factor=None, min_neighbors=None, enable_recognition=True):
        """
        Initialize detection with optimized Haar Cascade classifiers and face recognition.

        Args:
            scale_factor: Scale factor for cascade classifier (default: from config)
            min_neighbors: Min neighbors for object detection (default: from config)
            enable_recognition: Enable face recognition (default: True)
        """
        # Use config values for optimization
        self.scale_factor = scale_factor or Config.DETECTION_SCALE_FACTOR
        self.min_neighbors = min_neighbors or Config.DETECTION_MIN_NEIGHBORS

        # Performance tracking
        self.frame_count = 0
        self.last_cleanup_time = time.time()
        self.processing_times = deque(maxlen=100)  # Track last 100 processing times

        # Load Haar Cascade classifiers
        cascade_path = cv2.data.haarcascades

        # Load face cascade
        face_cascade_path = os.path.join(cascade_path, 'haarcascade_frontalface_default.xml')
        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)

        if self.face_cascade.empty():
            logger.warning("Failed to load face cascade classifier")

        # Load eye cascade for optional eye detection within faces
        eye_cascade_path = os.path.join(cascade_path, 'haarcascade_eye.xml')
        self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

        if self.eye_cascade.empty():
            logger.warning("Failed to load eye cascade classifier")

        # Background subtractor for motion detection (optimized)
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=16, detectShadows=False)

        # Face recognition with optimization
        self.enable_recognition = enable_recognition
        self.recognition = Recognition() if enable_recognition else None

        # Alert system
        self.alert_system = Alert()

        # Event logger
        self.event_logger = Logger()

        # Detection stats
        self.faces_detected = 0
        self.last_recognition_frame = 0

        logger.info("Detection system initialized with performance optimizations")

    def detect_faces(self, frame, detect_eyes=False):
        """
        Detect faces in the frame using optimized Haar Cascade.

        Args:
            frame: Input frame (BGR)
            detect_eyes: Also detect eyes within faces (default: False)

        Returns:
            faces: List of face rectangles (x, y, w, h)
            eyes: List of eye rectangles if detect_eyes=True, else empty list
        """
        try:
            start_time = time.time()

            # Convert to grayscale for faster detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Equalize histogram for better detection (but skip if performance is critical)
            # gray = cv2.equalizeHist(gray)  # Commented out for speed

            # Detect faces with optimized parameters
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=self.scale_factor,
                minNeighbors=self.min_neighbors,
                minSize=(30, 30),  # Minimum face size
                maxSize=(300, 300),  # Reduced max size for speed
                flags=cv2.CASCADE_SCALE_IMAGE  # Optimized flag
            )

            self.faces_detected = len(faces)

            eyes = []
            if detect_eyes and len(faces) > 0 and len(faces) <= 3:  # Limit eye detection to avoid performance hit
                # Detect eyes within each face (limited to first 3 faces for performance)
                for (x, y, w, h) in faces[:3]:
                    roi_gray = gray[y:y+h, x:x+w]
                    detected_eyes = self.eye_cascade.detectMultiScale(
                        roi_gray,
                        scaleFactor=1.1,
                        minNeighbors=3,
                        minSize=(10, 10)
                    )
                    # Offset eyes to original frame coordinates
                    for (ex, ey, ew, eh) in detected_eyes[:2]:  # Limit eyes per face
                        eyes.append((x+ex, y+ey, ew, eh))

            # Track processing time
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)

            return faces, eyes

        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return [], []

    def draw_detections_with_recognition(self, frame, faces, recognized_names, eyes=None, draw_eyes=False):
        """
        Draw bounding boxes for detected faces with recognition labels.
        
        Args:
            frame: Input frame to draw on
            faces: List of face rectangles (x, y, w, h)
            recognized_names: List of recognized names corresponding to faces
            eyes: List of eye rectangles (x, y, w, h), optional
            draw_eyes: Whether to draw eye boxes (default: False)
            
        Returns:
            Processed frame with drawn bounding boxes and labels
        """
        try:
            frame_copy = frame.copy()
            
            # Draw face bounding boxes with recognition labels
            for i, (x, y, w, h) in enumerate(faces):
                # Choose color based on recognition
                name = recognized_names[i] if i < len(recognized_names) else "Unknown"
                
                if name == "Unknown":
                    color = (0, 0, 255)  # Red for unknown
                else:
                    color = (0, 255, 0)  # Green for recognized
                
                # Draw rectangle
                cv2.rectangle(
                    frame_copy,
                    (x, y),
                    (x + w, y + h),
                    color,
                    2  # Thickness
                )
                
                # Draw label with name
                label = f"{name}"
                cv2.putText(
                    frame_copy,
                    label,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2
                )
                
                # Optional: draw confidence circle at center
                cx, cy = x + w // 2, y + h // 2
                cv2.circle(frame_copy, (cx, cy), 2, color, -1)
            
            # Draw eye bounding boxes if requested
            if draw_eyes and eyes:
                for (x, y, w, h) in eyes:
                    cv2.rectangle(
                        frame_copy,
                        (x, y),
                        (x + w, y + h),
                        (255, 0, 0),  # Blue color for eyes
                        1  # Thinner line
                    )
            
            return frame_copy
            
        except Exception as e:
            logger.error(f"Error drawing detections with recognition: {e}")
            return frame

    def detect_motion(self, frame):
        """
        Detect motion in the frame using background subtraction.
        
        Args:
            frame: Input frame
            
        Returns:
            motion_detected: Boolean indicating if motion is present
        """
        try:
            fg_mask = self.background_subtractor.apply(frame)
            motion_threshold = 500  # Minimum pixels for motion
            motion_detected = cv2.countNonZero(fg_mask) > motion_threshold
            return motion_detected
        except Exception as e:
            logger.error(f"Error in motion detection: {e}")
            return False

    def process_frame(self, frame, detect_motion=False, detect_eyes=False, draw_annotations=True):
        """
        Optimized frame processing pipeline with face detection and recognition.

        Args:
            frame: Input frame
            detect_motion: Enable motion detection (default: False)
            detect_eyes: Enable eye detection (default: False)
            draw_annotations: Draw bounding boxes (default: True)

        Returns:
            dict: Contains processed_frame, faces, eyes, motion_detected, recognized_names
        """
        try:
            start_time = time.time()
            self.frame_count += 1

            # Memory cleanup (run every 5 minutes)
            if time.time() - self.last_cleanup_time > Config.MEMORY_CLEANUP_INTERVAL:
                self._cleanup_memory()
                self.last_cleanup_time = time.time()

            # Detect faces using optimized Haar Cascade
            faces, eyes = self.detect_faces(frame, detect_eyes=detect_eyes)

            # Recognize faces with frame skipping for performance
            recognized_names = []
            should_recognize = (
                self.enable_recognition and
                self.recognition and
                self.recognition.available and
                faces and
                (self.frame_count - self.last_recognition_frame) >= Config.FRAME_SKIP_FACTOR
            )

            if should_recognize:
                try:
                    # Limit number of faces to process for performance
                    faces_to_process = faces[:Config.FACE_RECOGNITION_BATCH_SIZE]

                    # Convert Haar Cascade format to face_recognition format
                    face_locations_fr = [(y, x + w, y + h, x) for (x, y, w, h) in faces_to_process]

                    recognized_names_batch, _ = self.recognition.recognize_faces(frame, face_locations_fr)

                    # Map back to all faces (unprocessed faces marked as "Unknown")
                    recognized_names = recognized_names_batch + ["Unknown"] * (len(faces) - len(faces_to_process))

                    self.last_recognition_frame = self.frame_count

                except Exception as e:
                    logger.error(f"Error in face recognition: {e}")
                    recognized_names = ["Unknown"] * len(faces)
            else:
                recognized_names = ["Unknown"] * len(faces)

            # Trigger alerts for unknown faces (limit frequency)
            if self.enable_recognition and recognized_names and self.frame_count % 5 == 0:  # Every 5th frame
                for i, name in enumerate(recognized_names):
                    if name == "Unknown":
                        face_location = faces[i] if i < len(faces) else None
                        self.alert_system.trigger_unknown_person_alert(frame, face_location)
                        break  # Only trigger one alert per frame to avoid spam

            # Detect motion if requested (optimized)
            motion = self.detect_motion(frame) if detect_motion else False

            # Draw annotations if requested
            if draw_annotations:
                processed_frame = self.draw_detections_with_recognition(
                    frame, faces, recognized_names, eyes=eyes, draw_eyes=detect_eyes
                )
            else:
                processed_frame = frame

            # Track processing time
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)

            return {
                'frame': processed_frame,
                'faces': faces,
                'eyes': eyes,
                'motion_detected': motion,
                'recognized_names': recognized_names,
                'processing_time': processing_time,
                'face_count': len(faces)
            }

        except Exception as e:
            logger.error(f"Error in frame processing: {e}")
            return {
                'frame': frame,
                'faces': [],
                'eyes': [],
                'motion_detected': False,
                'recognized_names': [],
                'processing_time': 0,
                'face_count': 0
            }

    def _cleanup_memory(self):
        """Perform memory cleanup to prevent memory leaks."""
        try:
            # Clear old processing times (keep only recent ones)
            if len(self.processing_times) > 50:
                # Keep only the most recent 50 entries
                self.processing_times = deque(list(self.processing_times)[-50:], maxlen=100)

            # Force garbage collection if available
            import gc
            gc.collect()

            logger.debug("Memory cleanup performed")
        except Exception as e:
            logger.error(f"Error during memory cleanup: {e}")

    def get_stats(self):
        """Get performance statistics."""
        try:
            avg_processing_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
            max_processing_time = max(self.processing_times) if self.processing_times else 0

            return {
                'faces_detected': self.faces_detected,
                'scale_factor': self.scale_factor,
                'min_neighbors': self.min_neighbors,
                'recognition_enabled': self.enable_recognition,
                'recognition_available': self.recognition.available if self.recognition else False,
                'known_faces_count': len(self.recognition.known_face_names) if self.recognition else 0,
                'recognition_tolerance': self.recognition.tolerance if self.recognition else 0,
                'recognition_count': self.recognition.recognition_count if self.recognition else 0,
                'avg_recognition_time': self.recognition.average_recognition_time if self.recognition else 0,
                'frame_count': self.frame_count,
                'avg_processing_time': avg_processing_time,
                'max_processing_time': max_processing_time,
                'processing_fps': 1.0 / avg_processing_time if avg_processing_time > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}