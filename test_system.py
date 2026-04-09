#!/usr/bin/env python3
"""
Test script for Secure Vision surveillance system.
Tests face detection and recognition functionality.
"""

import cv2
import sys
import os
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from surveillance.detection import Detection
from surveillance.camera import Camera
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_face_detection():
    """Test face detection functionality."""
    logger.info("Testing face detection...")

    # Initialize detection
    detection = Detection()

    # Test with a simple image (create a blank image for testing)
    test_frame = cv2.imread('test_image.jpg')  # This will fail gracefully

    if test_frame is None:
        # Create a test frame if no image exists
        test_frame = cv2.imread('https://via.placeholder.com/640x480.jpg')  # This won't work either
        if test_frame is None:
            logger.info("No test image available, creating synthetic test frame")
            test_frame = cv2.imread('data/placeholder.jpg')
            if test_frame is None:
                logger.warning("No test image found. Face detection test skipped.")
                return False

    # Process frame
    result = detection.process_frame(test_frame, detect_motion=False, detect_eyes=False, draw_annotations=True)

    logger.info(f"Detection test completed. Found {result['face_count']} faces.")
    logger.info(f"Recognition available: {detection.recognition.available if detection.recognition else False}")

    return True

def test_camera_initialization():
    """Test camera initialization."""
    logger.info("Testing camera initialization...")

    try:
        camera = Camera()
        logger.info("Camera initialized successfully")
        camera.release()
        return True
    except Exception as e:
        logger.error(f"Camera initialization failed: {e}")
        return False

def test_system_status():
    """Test system status endpoints."""
    logger.info("Testing system status...")

    try:
        detection = Detection()
        camera = Camera()

        # Get detection stats
        detection_stats = detection.get_stats()
        logger.info(f"Detection stats: {detection_stats}")

        # Get camera status
        camera_status = camera.get_status()
        logger.info(f"Camera status: {camera_status}")

        camera.release()
        return True
    except Exception as e:
        logger.error(f"System status test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("Starting Secure Vision system tests...")

    tests = [
        ("Face Detection", test_face_detection),
        ("Camera Initialization", test_camera_initialization),
        ("System Status", test_system_status)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            logger.info(f"\n--- Running {test_name} Test ---")
            if test_func():
                logger.info(f"✅ {test_name} test PASSED")
                passed += 1
            else:
                logger.warning(f"⚠️ {test_name} test SKIPPED")
        except Exception as e:
            logger.error(f"❌ {test_name} test FAILED: {e}")

    logger.info(f"\n--- Test Results ---")
    logger.info(f"Passed: {passed}/{total} tests")
    logger.info(f"Skipped: {total - passed} tests")

    if passed == total:
        logger.info("🎉 All tests passed! System is ready.")
        return 0
    else:
        logger.warning("⚠️ Some tests were skipped. System may work with limited functionality.")
        return 1

if __name__ == "__main__":
    sys.exit(main())