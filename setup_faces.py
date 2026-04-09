#!/usr/bin/env python3
"""
Face Recognition Setup Utility
Adds sample faces to the recognition system for testing.
"""

import os
import sys
import cv2
import numpy as np
from surveillance.recognition import Recognition

def create_sample_face_image(name, width=200, height=200):
    """Create a simple sample face image for testing."""
    # Create a blank image
    image = np.zeros((height, width, 3), dtype=np.uint8)

    # Add some basic face-like features
    # Face outline
    cv2.ellipse(image, (width//2, height//2), (60, 80), 0, 0, 360, (200, 180, 150), -1)

    # Eyes
    cv2.circle(image, (width//2 - 25, height//2 - 20), 8, (255, 255, 255), -1)
    cv2.circle(image, (width//2 + 25, height//2 - 20), 8, (255, 255, 255), -1)
    cv2.circle(image, (width//2 - 25, height//2 - 20), 4, (0, 0, 0), -1)
    cv2.circle(image, (width//2 + 25, height//2 - 20), 4, (0, 0, 0), -1)

    # Nose
    cv2.ellipse(image, (width//2, height//2 + 10), (3, 8), 0, 0, 360, (180, 160, 130), -1)

    # Mouth
    cv2.ellipse(image, (width//2, height//2 + 30), (15, 5), 0, 0, 360, (150, 100, 100), -1)

    return image

def setup_sample_faces():
    """Add sample faces to the recognition system."""
    print("Setting up sample faces for testing...")

    # Initialize recognition
    recognition = Recognition()

    if not recognition.available:
        print("ERROR: Face recognition not available. Please install face-recognition library.")
        return False

    # Create sample faces
    sample_faces = [
        ("Alice", "alice.jpg"),
        ("Bob", "bob.jpg"),
        ("Charlie", "charlie.jpg")
    ]

    known_faces_dir = "data/known_faces"
    os.makedirs(known_faces_dir, exist_ok=True)

    for name, filename in sample_faces:
        filepath = os.path.join(known_faces_dir, filename)

        # Create sample image
        image = create_sample_face_image(name)

        # Save image
        cv2.imwrite(filepath, image)
        print(f"Created sample face image: {filepath}")

        # Add to recognition system
        success = recognition.add_known_face_from_image(filepath, name)
        if success:
            print(f"✓ Added {name} to recognition database")
        else:
            print(f"✗ Failed to add {name}")

    print(f"\nSetup complete! {len(recognition.get_known_faces())} faces in database:")
    for face_name in recognition.get_known_faces():
        print(f"  - {face_name}")

    return True

if __name__ == "__main__":
    try:
        success = setup_sample_faces()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)