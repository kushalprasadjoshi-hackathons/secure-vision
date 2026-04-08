import cv2
import logging
import os

logger = logging.getLogger(__name__)

class Detection:
    def __init__(self, scale_factor=1.1, min_neighbors=5):
        """
        Initialize detection with Haar Cascade classifiers.
        
        Args:
            scale_factor: Scale factor for cascade classifier (default: 1.1)
            min_neighbors: Min neighbors for object detection (default: 5)
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
        
        # Detection stats
        self.faces_detected = 0
        logger.info("Detection system initialized with Haar Cascades")

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

    def draw_detections(self, frame, faces, eyes=None, draw_eyes=False):
        """
        Draw bounding boxes for detected faces and eyes on frame.
        
        Args:
            frame: Input frame to draw on
            faces: List of face rectangles (x, y, w, h)
            eyes: List of eye rectangles (x, y, w, h), optional
            draw_eyes: Whether to draw eye boxes (default: False)
            
        Returns:
            Processed frame with drawn bounding boxes
        """
        try:
            frame_copy = frame.copy()
            
            # Draw face bounding boxes
            for (x, y, w, h) in faces:
                # Draw rectangle
                cv2.rectangle(
                    frame_copy,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),  # Green color for faces
                    2  # Thickness
                )
                
                # Draw label
                cv2.putText(
                    frame_copy,
                    'Face',
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )
                
                # Optional: draw confidence circle at center
                cx, cy = x + w // 2, y + h // 2
                cv2.circle(frame_copy, (cx, cy), 2, (0, 255, 0), -1)
            
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
            logger.error(f"Error drawing detections: {e}")
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
        Complete frame processing pipeline.
        
        Args:
            frame: Input frame
            detect_motion: Enable motion detection (default: False)
            detect_eyes: Enable eye detection (default: False)
            draw_annotations: Draw bounding boxes (default: True)
            
        Returns:
            dict: Contains processed_frame,faces, eyes, motion_detected
        """
        try:
            # Detect faces and eyes
            faces, eyes = self.detect_faces(frame, detect_eyes=detect_eyes)
            
            # Detect motion if requested
            motion = self.detect_motion(frame) if detect_motion else False
            
            # Draw annotations if requested
            if draw_annotations:
                processed_frame = self.draw_detections(
                    frame,
                    faces,
                    eyes=eyes,
                    draw_eyes=detect_eyes
                )
            else:
                processed_frame = frame
            
            return {
                'frame': processed_frame,
                'faces': faces,
                'eyes': eyes,
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
                'motion_detected': False,
                'face_count': 0,
                'eye_count': 0
            }

    def get_stats(self):
        """Get detection statistics."""
        return {
            'faces_detected': self.faces_detected,
            'scale_factor': self.scale_factor,
            'min_neighbors': self.min_neighbors
        }