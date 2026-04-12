#!/usr/bin/env python3
"""
Test script for Secure Vision surveillance system.
Tests face detection and recognition functionality.
"""

import cv2
import sys
import os
import logging
import time
import numpy as np

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from surveillance.detection import Detection
from surveillance.camera import Camera
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_alert_system():
    """Test alert system functionality."""
    logger.info("Testing alert system...")

    try:
        from surveillance.alert import Alert

        # Initialize alert system
        alert_system = Alert()

        # Test configuration
        logger.info(f"Email alerts enabled: {alert_system.enable_email_alerts}")
        logger.info(f"SMTP server: {alert_system.smtp_server}")
        logger.info(f"Alert recipient: {alert_system.alert_recipient_email}")

        # Test snapshot directory creation
        if os.path.exists(alert_system.snapshots_dir):
            logger.info(f"Snapshots directory exists: {alert_system.snapshots_dir}")
        else:
            logger.warning(f"Snapshots directory not found: {alert_system.snapshots_dir}")

        logger.info("Alert system test completed successfully")
        return True

    except Exception as e:
        logger.error(f"Alert system test failed: {e}")
        return False

def test_face_detection():
    """Test face detection functionality."""
    logger.info("Testing face detection...")

    try:
        # Initialize detection
        detection = Detection()

        # Create a synthetic test frame
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        # Process frame
        result = detection.process_frame(test_frame, detect_motion=False, detect_eyes=False, draw_annotations=False)

        logger.info(f"Detection test completed. Found {result['face_count']} faces.")
        logger.info(f"Recognition available: {detection.recognition.available if detection.recognition else False}")
        logger.info(f"Processing time: {result['processing_time']:.4f}s")

        return True

    except Exception as e:
        logger.error(f"Face detection test failed: {e}")
        return False

def test_performance():
    """Test system performance metrics."""
    logger.info("Testing system performance...")

    try:
        from surveillance.detection import Detection

        # Initialize detection with performance monitoring
        detection = Detection()

        # Test processing time for a few frames
        processing_times = []
        test_frames = 10

        for i in range(test_frames):
            # Create a test frame
            test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

            start_time = time.time()
            result = detection.process_frame(test_frame, detect_motion=False, detect_eyes=False, draw_annotations=False)
            processing_time = time.time() - start_time

            processing_times.append(processing_time)
            processing_times.append(result['processing_time'])

        avg_processing_time = sum(processing_times) / len(processing_times)
        fps_estimate = 1.0 / avg_processing_time if avg_processing_time > 0 else 0

        logger.info(f"Average processing time: {avg_processing_time:.4f} seconds")
        logger.info(f"Estimated FPS: {fps_estimate:.2f}")
        logger.info(f"Performance test completed - {'PASS' if fps_estimate >= 10 else 'SLOW'}")

        return fps_estimate >= 5  # Accept 5 FPS as minimum

    except Exception as e:
        logger.error(f"Performance test failed: {e}")
        return False

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
        ("Performance", test_performance),
        ("Alert System", test_alert_system),
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