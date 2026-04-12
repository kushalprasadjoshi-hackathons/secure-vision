try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    face_recognition = None
    FACE_RECOGNITION_AVAILABLE = False

import os
import numpy as np
from config import Config
import pickle
import logging
import time
from collections import OrderedDict

logger = logging.getLogger(__name__)

class Recognition:
    def __init__(self):
        self.available = FACE_RECOGNITION_AVAILABLE

        if not self.available:
            logger.warning("face_recognition module not available. Install with: pip install dlib face-recognition")
            logger.info("System will work with face detection only (no recognition)")
            self.known_face_encodings = []
            self.known_face_names = []
            self.tolerance = Config.FACE_RECOGNITION_TOLERANCE

            # Initialize performance tracking attributes
            self.last_recognition_time = 0
            self.recognition_count = 0
            self.average_recognition_time = 0
            return

        self.known_face_encodings = []
        self.known_face_names = []
        self.tolerance = Config.FACE_RECOGNITION_TOLERANCE

        # Performance tracking
        self.last_recognition_time = 0
        self.recognition_count = 0
        self.average_recognition_time = 0

        # Face recognition cache for performance
        self.enable_cache = Config.ENABLE_FACE_CACHE
        self.cache_max_size = Config.FACE_CACHE_MAX_SIZE
        self.face_cache = OrderedDict()  # LRU cache for face encodings

        # Load known faces on initialization
        self.load_known_faces()

        logger.info(f"Face recognition initialized with {len(self.known_face_names)} known faces")

    def load_known_faces(self):
        """Load and encode known faces from data/known_faces directory."""
        if not self.available:
            logger.info("Face recognition not available - skipping face loading")
            return

        known_faces_dir = Config.KNOWN_FACES_DIR
        if not os.path.exists(known_faces_dir):
            os.makedirs(known_faces_dir, exist_ok=True)
            logger.info(f"Created known faces directory: {known_faces_dir}")
            return

        # Clear existing data
        self.known_face_encodings = []
        self.known_face_names = []

        # Load from pickle files (cached encodings)
        pickle_files = [f for f in os.listdir(known_faces_dir) if f.endswith('.pkl')]
        for filename in pickle_files:
            try:
                filepath = os.path.join(known_faces_dir, filename)
                with open(filepath, 'rb') as f:
                    data = pickle.load(f)
                    if 'encoding' in data and 'name' in data:
                        self.known_face_encodings.append(data['encoding'])
                        self.known_face_names.append(data['name'])
                        logger.debug(f"Loaded cached face: {data['name']}")
            except Exception as e:
                logger.error(f"Error loading cached face {filename}: {e}")

        # Load from image files and create encodings
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = [f for f in os.listdir(known_faces_dir)
                      if any(f.lower().endswith(ext) for ext in image_extensions)]

        for filename in image_files:
            name = os.path.splitext(filename)[0]  # Use filename as name
            if name in self.known_face_names:
                continue  # Skip if already loaded from cache

            try:
                filepath = os.path.join(known_faces_dir, filename)
                self.add_known_face_from_image(filepath, name)
                logger.info(f"Encoded and cached face: {name}")
            except Exception as e:
                logger.error(f"Error processing image {filename}: {e}")

        logger.info(f"Loaded {len(self.known_face_names)} known faces")

    def add_known_face_from_image(self, image_path, name):
        """Add a known face from an image file."""
        if not self.available:
            return False

        try:
            # Load image
            image = face_recognition.load_image_file(image_path)

            # Find face encodings
            face_encodings = face_recognition.face_encodings(image)

            if not face_encodings:
                logger.warning(f"No faces found in image: {image_path}")
                return False

            if len(face_encodings) > 1:
                logger.warning(f"Multiple faces found in {image_path}, using first one")

            # Use the first face encoding
            encoding = face_encodings[0]

            # Add to known faces
            self.known_face_encodings.append(encoding)
            self.known_face_names.append(name)

            # Cache to pickle file
            cache_data = {
                'encoding': encoding,
                'name': name,
                'image_path': image_path,
                'created_at': time.time()
            }

            cache_filename = f"{name}.pkl"
            cache_path = os.path.join(Config.KNOWN_FACES_DIR, cache_filename)
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)

            logger.info(f"Added known face: {name}")
            return True

        except Exception as e:
            logger.error(f"Error adding face from image {image_path}: {e}")
            return False

    def recognize_faces(self, frame, face_locations=None):
        """
        Recognize faces in the frame.

        Args:
            frame: Input frame (BGR)
            face_locations: Optional pre-computed face locations

        Returns:
            list: Recognized names corresponding to face locations
            list: Face locations if not provided
        """
        if not self.available:
            logger.warning("Face recognition not available")
            return [], []

        if not self.known_face_encodings:
            logger.debug("No known faces to compare against")
            return ["Unknown"] * len(face_locations) if face_locations else [], face_locations or []

        try:
            start_time = time.time()

            # Find face locations if not provided
            if face_locations is None:
                face_locations = face_recognition.face_locations(frame)

            if not face_locations:
                return [], []

            # Get face encodings for all faces (optimized for performance)
            face_encodings = face_recognition.face_encodings(frame, face_locations, num_jitters=1)  # Reduced jitters for speed

            if not face_encodings:
                logger.debug("No face encodings found")
                return ["Unknown"] * len(face_locations), face_locations

            # Recognize each face with caching
            recognized_names = []
            for face_encoding in face_encodings:
                name = self._recognize_single_face_cached(face_encoding)
                recognized_names.append(name)

            # Update performance metrics
            recognition_time = time.time() - start_time
            self.recognition_count += 1
            self.last_recognition_time = recognition_time
            self.average_recognition_time = (
                (self.average_recognition_time * (self.recognition_count - 1)) + recognition_time
            ) / self.recognition_count

            return recognized_names, face_locations

        except Exception as e:
            logger.error(f"Error in face recognition: {e}")
            return ["Unknown"] * len(face_locations) if face_locations else [], face_locations or []

    def _recognize_single_face(self, face_encoding):
        """Recognize a single face encoding."""
        try:
            # Compare with known faces
            distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

            # Find best match
            best_match_index = np.argmin(distances)
            best_distance = distances[best_match_index]

            # Check if match is within tolerance
            if best_distance <= self.tolerance:
                name = self.known_face_names[best_match_index]
                logger.debug(f"Recognized: {name} (distance: {best_distance:.3f})")
                return name
            else:
                logger.debug(f"Unknown face (best distance: {best_distance:.3f})")
                return "Unknown"

        except Exception as e:
            logger.error(f"Error recognizing single face: {e}")
            return "Unknown"

    def _recognize_single_face_cached(self, face_encoding):
        """Recognize a single face encoding with caching for performance."""
        if not self.enable_cache:
            return self._recognize_single_face(face_encoding)

        try:
            # Create cache key from face encoding (use first 10 values for uniqueness)
            cache_key = tuple(face_encoding[:10])

            # Check cache first
            if cache_key in self.face_cache:
                cached_result = self.face_cache[cache_key]
                # Move to end (most recently used)
                self.face_cache.move_to_end(cache_key)
                return cached_result

            # Not in cache, compute recognition
            result = self._recognize_single_face(face_encoding)

            # Add to cache (with LRU eviction)
            if len(self.face_cache) >= self.cache_max_size:
                # Remove least recently used
                self.face_cache.popitem(last=False)

            self.face_cache[cache_key] = result
            self.face_cache.move_to_end(cache_key)

            return result

        except Exception as e:
            logger.error(f"Error in cached face recognition: {e}")
            return self._recognize_single_face(face_encoding)  # Fallback to non-cached

    def add_known_face(self, image_path, name):
        """Add a new known face from image path."""
        return self.add_known_face_from_image(image_path, name)

    def remove_known_face(self, name):
        """Remove a known face by name."""
        try:
            if name in self.known_face_names:
                index = self.known_face_names.index(name)
                self.known_face_encodings.pop(index)
                self.known_face_names.pop(index)

                # Remove cache file
                cache_path = os.path.join(Config.KNOWN_FACES_DIR, f"{name}.pkl")
                if os.path.exists(cache_path):
                    os.remove(cache_path)

                logger.info(f"Removed known face: {name}")
                return True
            else:
                logger.warning(f"Face not found: {name}")
                return False
        except Exception as e:
            logger.error(f"Error removing face {name}: {e}")
            return False

    def get_known_faces(self):
        """Get list of known face names."""
        return self.known_face_names.copy()

    def get_stats(self):
        """Get recognition statistics."""
        return {
            'available': self.available,
            'known_faces_count': len(self.known_face_names),
            'tolerance': self.tolerance,
            'recognition_count': self.recognition_count,
            'last_recognition_time': self.last_recognition_time,
            'average_recognition_time': self.average_recognition_time
        }

    def reload_known_faces(self):
        """Reload all known faces from disk."""
        logger.info("Reloading known faces...")
        self.load_known_faces()
        logger.info(f"Reloaded {len(self.known_face_names)} known faces")