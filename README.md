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
   git clone https://github.com/kushalprasadjoshi-hackathons/secure-vision.git
   cd secure-vision
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Email Alert Configuration

The system supports optional email alerts when unknown faces are detected. To enable email alerts:

1. **Configure Email Settings** in `config.py`:
   ```python
   # Email alert settings
   ENABLE_EMAIL_ALERTS = True  # Set to True to enable email alerts
   SMTP_SERVER = 'smtp.gmail.com'
   SMTP_PORT = 587
   SENDER_EMAIL = 'your-email@gmail.com'
   SENDER_PASSWORD = 'your-app-password'  # Use app password for Gmail
   ALERT_RECIPIENT_EMAIL = 'admin@example.com'
   ```

2. **Gmail Setup** (if using Gmail):
   - Enable 2-factor authentication on your Gmail account
   - Generate an App Password: https://support.google.com/accounts/answer/185833
   - Use the App Password as `SENDER_PASSWORD`

3. **Test Configuration**:
   ```bash
   python test_system.py
   ```

### Email Alert Features

- **Automatic Triggers**: Emails are sent when unknown faces are detected
- **Snapshot Attachments**: Each alert includes a snapshot image of the detected person
- **Detailed Information**: Email includes timestamp, face location, and confidence score
- **Failure-Safe**: System continues to work even if email sending fails
- **Configurable**: Easily enable/disable and reconfigure without code changes

### Security Notes

- Never commit real email credentials to version control
- Use environment variables for sensitive configuration in production:
  ```python
  SENDER_EMAIL = os.environ.get('ALERT_EMAIL')
  SENDER_PASSWORD = os.environ.get('ALERT_EMAIL_PASSWORD')
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

Contributions are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

_Thank you!_