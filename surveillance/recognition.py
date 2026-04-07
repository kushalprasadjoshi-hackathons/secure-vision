import face_recognition
import os
from config import Config
import pickle

class Recognition:
    def __init__(self):
        self.known_faces = []
        self.known_names = []
        self.tolerance = Config.FACE_RECOGNITION_TOLERANCE
        self.load_known_faces()

    def load_known_faces(self):
        """Load known faces from the data/known_faces directory."""
        known_faces_dir = Config.KNOWN_FACES_DIR
        for filename in os.listdir(known_faces_dir):
            if filename.endswith('.pkl'):
                with open(os.path.join(known_faces_dir, filename), 'rb') as f:
                    data = pickle.load(f)
                    self.known_faces.append(data['encoding'])
                    self.known_names.append(data['name'])

    def recognize_face(self, frame):
        """Recognize faces in the frame."""
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

    def add_known_face(self, image_path, name):
        """Add a new known face."""
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)[0]
        self.known_faces.append(encoding)
        self.known_names.append(name)
        # Save to file
        data = {'encoding': encoding, 'name': name}
        with open(os.path.join(Config.KNOWN_FACES_DIR, f"{name}.pkl"), 'wb') as f:
            pickle.dump(data, f)

    # Future: add methods for updating and removing known faces