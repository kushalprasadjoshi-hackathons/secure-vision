import cv2
import logging
import os
from surveillance.recognition import Recognition

logger = logging.getLogger(__name__)

class Detection:
    def __init__(self, scale_factor=1.1, min_neighbors=5, enable_recognition=True):
        """
        Initialize detection with Haar Cascade classifiers and face recognition.
        
        Args:
            scale_factor: Scale factor for cascade classifier (default: 1.1)
            min_neighbors: Min neighbors for object detection (default: 5)
            enable_recognition: Enable face recognition (default: True)
        """
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        
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
        
        # Background subtractor for motion detection
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2()
        
        # Face recognition
        self.enable_recognition = enable_recognition
        self.recognition = Recognition() if enable_recognition else None
        
        # Detection stats
        self.faces_detected = 0
        logger.info("Detection system initialized with Haar Cascades and face recognition")

    def detect_faces(self, frame, detect_eyes=False):
        """
        Detect faces in the frame using Haar Cascade.
        
        Args:
            frame: Input frame (BGR)
            detect_eyes: Also detect eyes within faces (default: False)
            
        Returns:
            faces: List of face rectangles (x, y, w, h)
            eyes: List of eye rectangles if detect_eyes=True, else empty list
        """
        try:
            # Convert to grayscale for faster detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Equalize histogram for better detection
            gray = cv2.equalizeHist(gray)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=self.scale_factor,
                minNeighbors=self.min_neighbors,
                minSize=(30, 30),  # Minimum face size
                maxSize=(400, 400)  # Maximum face size
            )
            
            self.faces_detected = len(faces)
            
            eyes = []
            if detect_eyes and len(faces) > 0:
                # Detect eyes within each face
                for (x, y, w, h) in faces:
                    roi_gray = gray[y:y+h, x:x+w]
                    detected_eyes = self.eye_cascade.detectMultiScale(roi_gray)
                    # Offset eyes to original frame coordinates
                    for (ex, ey, ew, eh) in detected_eyes:
                        eyes.append((x+ex, y+ey, ew, eh))
            
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
        Complete frame processing pipeline with face detection and recognition.
        
        Args:
            frame: Input frame
            detect_motion: Enable motion detection (default: False)
            detect_eyes: Enable eye detection (default: False)
            draw_annotations: Draw bounding boxes (default: True)
            
        Returns:
            dict: Contains processed_frame, faces, eyes, motion_detected, recognized_names
        """
        try:
            # Detect faces using Haar Cascade
            faces, eyes = self.detect_faces(frame, detect_eyes=detect_eyes)
            
            # Recognize faces if recognition is enabled
            recognized_names = []
            if self.enable_recognition and self.recognition and self.recognition.available and faces:
                try:
                    # Convert Haar Cascade format to face_recognition format
                    # Haar Cascade returns (x, y, w, h), face_recognition expects (top, right, bottom, left)
                    face_locations_fr = [(y, x + w, y + h, x) for (x, y, w, h) in faces]
                    
                    recognized_names, _ = self.recognition.recognize_faces(frame, face_locations_fr)
                except Exception as e:
                    logger.error(f"Error in face recognition: {e}")
                    recognized_names = ["Unknown"] * len(faces)
            else:
                recognized_names = ["Unknown"] * len(faces)
            
            # Detect motion if requested
            motion = self.detect_motion(frame) if detect_motion else False
            
            # Draw annotations if requested
            if draw_annotations:
                processed_frame = self.draw_detections_with_recognition(
                    frame, faces, recognized_names, eyes=eyes, draw_eyes=detect_eyes
                )
            else:
                processed_frame = frame
            
            return {
                'frame': processed_frame,
                'faces': faces,
                'eyes': eyes,
                'recognized_names': recognized_names,
                'motion_detected': motion,
                'face_count': len(faces),
                'eye_count': len(eyes)
            }
            
        except Exception as e:
            logger.error(f"Error in frame processing: {e}")
            return {
                'frame': frame,
                'faces': [],
                'eyes': [],
                'recognized_names': [],
                'motion_detected': False,
                'face_count': 0,
                'eye_count': 0
            }

    def get_stats(self):
        """Get detection and recognition statistics."""
        stats = {
            'faces_detected': self.faces_detected,
            'scale_factor': self.scale_factor,
            'min_neighbors': self.min_neighbors,
            'recognition_enabled': self.enable_recognition
        }
        
        if self.recognition:
            recognition_stats = self.recognition.get_stats()
            stats.update({
                'recognition_available': recognition_stats.get('available', False),
                'known_faces_count': recognition_stats.get('known_faces_count', 0),
                'recognition_tolerance': recognition_stats.get('tolerance', 0.6),
                'recognition_count': recognition_stats.get('recognition_count', 0),
                'avg_recognition_time': recognition_stats.get('average_recognition_time', 0)
            })
        
        return stats