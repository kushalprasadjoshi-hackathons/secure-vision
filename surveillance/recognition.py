try:
    import face_recognition
except ImportError:
    face_recognition = None

import os
from config import Config
import pickle
import logging

logger = logging.getLogger(__name__)

class Recognition:
    def __init__(self):
        if face_recognition is None:
            logger.warning("face_recognition module not available. Install with: pip install face-recognition")
        
        self.known_faces = []
        self.known_names = []
        self.tolerance = Config.FACE_RECOGNITION_TOLERANCE
        self.load_known_faces()

    def load_known_faces(self):
        """Load known faces from the data/known_faces directory."""
        if face_recognition is None:
            logger.warning("Cannot load known faces - face_recognition not installed")
            return
        
        known_faces_dir = Config.KNOWN_FACES_DIR
        if not os.path.exists(known_faces_dir):
            return
            
        for filename in os.listdir(known_faces_dir):
            if filename.endswith('.pkl'):
                try:
                    with open(os.path.join(known_faces_dir, filename), 'rb') as f:
                        data = pickle.load(f)
                        self.known_faces.append(data['encoding'])
                        self.known_names.append(data['name'])
                except Exception as e:
                    logger.error(f"Error loading face file {filename}: {e}")

    def recognize_face(self, frame):
        """Recognize faces in the frame."""
        if face_recognition is None:
            logger.warning("Cannot recognize faces - face_recognition not installed")
            return [], []
        
        try:
            # Find face locations and encodings
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            recognized_names = []
            for face_encoding in face_encodings:
                # Compare with known faces
                matches = face_recognition.compare_faces(self.known_faces, face_encoding, tolerance=self.tolerance)
                name = "Unknown"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_names[first_match_index]

                recognized_names.append(name)

            return recognized_names, face_locations
        except Exception as e:
            logger.error(f"Error in face recognition: {e}")
            return [], []

    def add_known_face(self, image_path, name):
        """Add a new known face."""
        if face_recognition is None:
            logger.error("Cannot add face - face_recognition not installed")
            return False
        
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            
            if not encodings:
                logger.error("No face found in image")
                return False
            
            encoding = encodings[0]
            self.known_faces.append(encoding)
            self.known_names.append(name)
            
            # Save to file
            data = {'encoding': encoding, 'name': name}
            with open(os.path.join(Config.KNOWN_FACES_DIR, f"{name}.pkl"), 'wb') as f:
                pickle.dump(data, f)
            
            logger.info(f"Added known face: {name}")
            return True
        except Exception as e:
            logger.error(f"Error adding face: {e}")
            return False

    # Future: add methods for updating and removing known faces