import logging
import json
import os
from datetime import datetime
from config import Config

class Logger:
    def __init__(self):
        self.logs_dir = Config.LOGS_DIR
        os.makedirs(self.logs_dir, exist_ok=True)
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.logs_dir, 'surveillance.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('SecureVision')

    def log_event(self, event_type, details):
        """Log an event."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details
        }
        self.logger.info(json.dumps(log_entry))
        # Also save to JSON file
        self.save_to_json(log_entry)

    def save_to_json(self, log_entry):
        """Save log entry to JSON file."""
        log_file = os.path.join(self.logs_dir, f"{datetime.now().strftime('%Y-%m-%d')}.json")
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            logs.append(log_entry)
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save log to JSON: {e}")

    def get_recent_logs(self, limit=10):
        """Get recent log entries."""
        # Future: implement retrieving logs from database or files
        return []  # Placeholder