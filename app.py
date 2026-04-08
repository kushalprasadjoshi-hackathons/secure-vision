from flask import Flask, render_template, request, jsonify, Response
from config import Config
import os
import logging
from surveillance.camera import Camera

app = Flask(__name__)
app.config.from_object(Config)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global camera instance
camera = None

def get_camera():
    """Get or create camera instance."""
    global camera
    if camera is None:
        camera = Camera()
    return camera

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
            return jsonify({'status': 'Surveillance started', 'success': True})
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

@app.route('/video_feed')
def video_feed():
    """Stream video feed as MJPEG."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    """Generate frames for streaming."""
    cam = get_camera()
    
    try:
        if not cam.is_active():
            cam.start()
    except Exception as e:
        logger.error(f"Failed to start camera for streaming: {e}")
        return
    
    while True:
        try:
            frame = cam.get_frame()
            
            if frame is None:
                continue
            
            # Encode frame to JPEG
            encoded = cam.encode_frame(frame)
            
            if encoded:
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n'
                    b'Content-Length: ' + str(len(encoded)).encode() + b'\r\n\r\n'
                    + encoded + b'\r\n'
                )
            
        except GeneratorExit:
            logger.info("Stream client disconnected")
            break
        except Exception as e:
            logger.error(f"Error in stream generation: {e}")
            continue

@app.route('/camera_status')
def camera_status():
    """Get camera status."""
    try:
        cam = get_camera()
        return jsonify({
            'is_active': cam.is_active(),
            'fps': round(cam.get_fps(), 2),
            'frame_count': cam.frame_count
        })
    except Exception as e:
        logger.error(f"Error getting camera status: {e}")
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