from flask import Flask, render_template, request, jsonify
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

# Import surveillance modules here when implemented
# from surveillance import camera, detection, recognition, alert, logger

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_surveillance', methods=['POST'])
def start_surveillance():
    # Placeholder for starting surveillance
    # Future: integrate with camera and detection modules
    return jsonify({'status': 'Surveillance started'})

@app.route('/stop_surveillance', methods=['POST'])
def stop_surveillance():
    # Placeholder for stopping surveillance
    return jsonify({'status': 'Surveillance stopped'})

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])