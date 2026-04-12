from flask import Flask, render_template, request, jsonify, Response
from config import Config
import os
import logging
from surveillance.camera import Camera
from surveillance.detection import Detection

app = Flask(__name__)
app.config.from_object(Config)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
camera = None
detector = None

# Detection settings
detection_settings = {
    'enabled': False,
    'detect_faces': True,
    'detect_eyes': False,
    'draw_annotations': True,
    'detect_motion': False
}

def get_camera():
    """Get or create camera instance."""
    global camera
    if camera is None:
        camera = Camera()
    return camera

def get_detector():
    """Get or create detector instance."""
    global detector
    if detector is None:
        detector = Detection(scale_factor=1.1, min_neighbors=5)
    return detector

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_surveillance', methods=['POST'])
def start_surveillance():
    """Start the surveillance system."""
    try:
        cam = get_camera()
        if not cam.is_active():
            cam.start()
            # Enable detection by default
            cam.enable_detection(True)
            return jsonify({'status': 'Surveillance started with face detection', 'success': True})
        return jsonify({'status': 'Surveillance already running', 'success': True})
    except Exception as e:
        logger.error(f"Error starting surveillance: {e}")
        return jsonify({'status': f'Error: {str(e)}', 'success': False}), 500

@app.route('/stop_surveillance', methods=['POST'])
def stop_surveillance():
    """Stop the surveillance system."""
    try:
        cam = get_camera()
        if cam.is_active():
            cam.stop()
            return jsonify({'status': 'Surveillance stopped', 'success': True})
        return jsonify({'status': 'Surveillance already stopped', 'success': True})
    except Exception as e:
        logger.error(f"Error stopping surveillance: {e}")
        return jsonify({'status': f'Error: {str(e)}', 'success': False}), 500

@app.route('/detection/toggle', methods=['POST'])
def toggle_detection():
    """Toggle face detection on/off."""
    try:
        enabled = request.json.get('enabled', not detection_settings['enabled'])
        detection_settings['enabled'] = enabled
        
        if enabled:
            get_detector()  # Initialize detector
            logger.info("Face detection enabled")
        
        return jsonify({
            'status': 'Face detection ' + ('enabled' if enabled else 'disabled'),
            'enabled': enabled,
            'success': True
        })
    except Exception as e:
        logger.error(f"Error toggling detection: {e}")
        return jsonify({'status': f'Error: {str(e)}', 'success': False}), 500

@app.route('/detection/settings', methods=['GET', 'POST'])
def detection_settings_endpoint():
    """Get or update detection settings."""
    try:
        if request.method == 'POST':
            data = request.json or {}
            
            # Update settings
            if 'detect_faces' in data:
                detection_settings['detect_faces'] = data['detect_faces']
            if 'detect_eyes' in data:
                detection_settings['detect_eyes'] = data['detect_eyes']
            if 'draw_annotations' in data:
                detection_settings['draw_annotations'] = data['draw_annotations']
            if 'detect_motion' in data:
                detection_settings['detect_motion'] = data['detect_motion']
            
            logger.info(f"Detection settings updated: {detection_settings}")
            return jsonify({'status': 'Settings updated', 'settings': detection_settings, 'success': True})
        
        return jsonify(detection_settings)
    except Exception as e:
        logger.error(f"Error updating detection settings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/detection/stats')
def detection_stats():
    """Get detection statistics."""
    try:
        if not detection_settings['enabled']:
            return jsonify({'error': 'Detection not enabled'}), 400
        
        detector = get_detector()
        stats = detector.get_stats()
        
        return jsonify({
            'enabled': detection_settings['enabled'],
            'stats': stats,
            'settings': detection_settings
        })
    except Exception as e:
        logger.error(f"Error getting detection stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/video_feed')
def video_feed():
    """Stream video feed as MJPEG."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    """Generate frames for streaming with optimized processing."""
    cam = get_camera()
    detector = None
    last_processing_time = 0
    frame_interval = 1.0 / Config.MAX_FRAME_RATE  # Respect config frame rate limit

    try:
        if not cam.is_active():
            cam.start()
    except Exception as e:
        logger.error(f"Failed to start camera for streaming: {e}")
        return

    if detection_settings['enabled']:
        detector = get_detector()

    while True:
        try:
            current_time = time.time()

            # Rate limiting for processing
            if current_time - last_processing_time < frame_interval:
                time.sleep(0.001)  # Prevent busy waiting
                continue

            frame = cam.get_frame()

            if frame is None:
                continue

            # Apply face detection if enabled (optimized)
            if detector and detection_settings['enabled'] and detection_settings['detect_faces']:
                try:
                    result = detector.process_frame(
                        frame,
                        detect_motion=detection_settings['detect_motion'],
                        detect_eyes=detection_settings['detect_eyes'],
                        draw_annotations=detection_settings['draw_annotations']
                    )
                    frame = result['frame']
                except Exception as e:
                    logger.error(f"Error processing frame with detection: {e}")

            # Encode frame to JPEG with optimized quality
            encoded = cam.encode_frame(frame)

            if encoded:
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n'
                    b'Content-Length: ' + str(len(encoded)).encode() + b'\r\n\r\n'
                    + encoded + b'\r\n'
                )

            last_processing_time = current_time

        except GeneratorExit:
            logger.info("Stream client disconnected")
            break
        except Exception as e:
            logger.error(f"Error in stream generation: {e}")
            time.sleep(0.01)  # Brief pause on error

@app.route('/performance_stats')
def performance_stats():
    """Get performance statistics."""
    try:
        cam = get_camera()
        detector = get_detector()

        stats = {
            'camera': {
                'active': cam.is_active(),
                'fps': cam.get_fps(),
                'frame_count': cam.frame_count,
                'resolution': '640x480'
            },
            'detection': detector.get_stats() if detector else {},
            'config': {
                'max_frame_rate': Config.MAX_FRAME_RATE,
                'frame_skip_factor': Config.FRAME_SKIP_FACTOR,
                'face_recognition_batch_size': Config.FACE_RECOGNITION_BATCH_SIZE
            }
        }

        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting performance stats: {e}")
        return jsonify({'error': str(e)}), 500
        status_data = {
            'is_active': cam.is_active(),
            'fps': round(cam.get_fps(), 2),
            'frame_count': cam.frame_count,
            'detection_enabled': detection_settings['enabled']
        }
        
        # Add detection stats if enabled
        if detection_settings['enabled']:
            detector = get_detector()
            if detector:
                detection_stats = detector.get_stats()
                status_data.update({
                    'faces_detected': detection_stats.get('faces_detected', 0),
                    'scale_factor': detection_stats.get('scale_factor', 1.1),
                    'min_neighbors': detection_stats.get('min_neighbors', 5),
                    'recognition_enabled': detection_stats.get('recognition_enabled', False),
                    'recognition_available': detection_stats.get('recognition_available', False),
                    'known_faces_count': detection_stats.get('known_faces_count', 0),
                    'recognition_tolerance': detection_stats.get('recognition_tolerance', 0.6)
                })
        
        return jsonify(status_data)
    except Exception as e:
        logger.error(f"Error getting camera status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/alerts')
def get_alerts():
    """Get recent alerts."""
    try:
        detector = get_detector()
        if detector and hasattr(detector, 'alert_system'):
            alerts = detector.alert_system.get_recent_alerts(limit=10)
            return jsonify({'alerts': alerts})
        return jsonify({'alerts': []})
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/events')
def get_events():
    """Get recent events."""
    try:
        detector = get_detector()
        if detector and hasattr(detector, 'event_logger'):
            events = detector.event_logger.get_events(limit=20)
            return jsonify({'events': events})
        return jsonify({'events': []})
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/events/stats')
def get_event_stats():
    """Get event statistics."""
    try:
        detector = get_detector()
        if detector and hasattr(detector, 'event_logger'):
            stats = detector.event_logger.get_event_stats()
            return jsonify(stats)
        return jsonify({
            'total_events': 0,
            'event_types': {},
            'alert_status_counts': {},
            'person_counts': {},
            'recent_events': []
        })
    except Exception as e:
        logger.error(f"Error getting event stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    try:
        app.run(debug=app.config['DEBUG'])
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        if camera and camera.is_active():
            camera.stop()
    except Exception as e:
        logger.error(f"Application error: {e}")
        if camera and camera.is_active():
            camera.stop()