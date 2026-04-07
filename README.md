# Secure Vision

An AI-based smart surveillance system built with Python, Flask, OpenCV, and face recognition technology.

## Features

- Real-time video surveillance
- Face detection and recognition
- Motion detection
- Alert system (email/SMS)
- Logging and monitoring
- Web-based interface

## Tech Stack

- **Backend**: Python, Flask
- **Computer Vision**: OpenCV, face-recognition
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/secure-vision.git
   cd secure-vision
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the application in `config.py`

4. Run the application:
   ```bash
   python app.py
   ```

## Project Structure

```
secure-vision/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── config.py              # Configuration settings
├── README.md              # Project documentation
├── templates/
│   └── index.html         # Main web interface
├── static/
│   ├── css/
│   └── js/                # Static assets
├── surveillance/
│   ├── camera.py          # Camera handling
│   ├── detection.py       # Object and motion detection
│   ├── recognition.py     # Face recognition
│   ├── alert.py           # Alert system
│   └── logger.py          # Logging functionality
├── data/
│   ├── known_faces/       # Stored face encodings
│   └── logs/              # Log files
└── utils/                 # Utility functions
```

## Usage

1. Start the Flask server
2. Open your browser to `http://localhost:5000`
3. Use the web interface to start/stop surveillance
4. Known faces can be added via the recognition module

## Contributing

Contributions are welcome! Please read the contributing guidelines before submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.