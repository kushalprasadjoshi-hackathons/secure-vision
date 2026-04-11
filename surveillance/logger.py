import logging
import json
import os
import sqlite3
from datetime import datetime
from config import Config

class Logger:
    def __init__(self, storage_type=None):
        """
        Initialize the event logger.

        Args:
            storage_type: 'json' or 'sqlite' for log storage (defaults to config setting)
        """
        self.logs_dir = Config.LOGS_DIR
        self.storage_type = storage_type or Config.LOG_STORAGE_TYPE
        self.db_path = os.path.join(self.logs_dir, 'events.db')

        # Create logs directory if it doesn't exist
        os.makedirs(self.logs_dir, exist_ok=True)

        # Setup logging configuration
        self.setup_logging()

        # Initialize storage
        if self.storage_type == 'sqlite':
            self.init_sqlite_db()

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

    def init_sqlite_db(self):
        """Initialize SQLite database and create events table."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        person_name TEXT,
                        event_type TEXT NOT NULL,
                        snapshot_path TEXT,
                        alert_status TEXT,
                        details TEXT,
                        created_at REAL
                    )
                ''')
                conn.commit()
            self.logger.info("SQLite database initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize SQLite database: {e}")
            # Fallback to JSON storage
            self.storage_type = 'json'

    def log_event(self, event_type, person_name=None, snapshot_path=None, alert_status=None, details=None):
        """
        Log an event with comprehensive information.

        Args:
            event_type: Type of event (e.g., 'face_detected', 'unknown_person', 'system_start')
            person_name: Name of the person (if recognized)
            snapshot_path: Path to snapshot image (if applicable)
            alert_status: Alert status ('triggered', 'cooldown', 'none')
            details: Additional details as dictionary
        """
        try:
            timestamp = datetime.now().isoformat()

            log_entry = {
                'timestamp': timestamp,
                'person_name': person_name,
                'event_type': event_type,
                'snapshot_path': snapshot_path,
                'alert_status': alert_status,
                'details': details or {}
            }

            # Log to standard logging
            log_message = f"Event: {event_type}"
            if person_name:
                log_message += f" | Person: {person_name}"
            if alert_status:
                log_message += f" | Alert: {alert_status}"
            self.logger.info(log_message)

            # Save to storage
            if self.storage_type == 'sqlite':
                self.save_to_sqlite(log_entry)
            else:
                self.save_to_json(log_entry)

        except Exception as e:
            self.logger.error(f"Failed to log event: {e}")

    def save_to_sqlite(self, log_entry):
        """Save log entry to SQLite database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO events (timestamp, person_name, event_type, snapshot_path, alert_status, details, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    log_entry['timestamp'],
                    log_entry['person_name'],
                    log_entry['event_type'],
                    log_entry['snapshot_path'],
                    log_entry['alert_status'],
                    json.dumps(log_entry['details']),
                    datetime.now().timestamp()
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to save log to SQLite: {e}")
            # Fallback to JSON
            self.save_to_json(log_entry)

    def save_to_json(self, log_entry):
        """Save log entry to JSON file."""
        try:
            log_file = os.path.join(self.logs_dir, f"events_{datetime.now().strftime('%Y-%m-%d')}.json")

            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []

            logs.append(log_entry)

            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Failed to save log to JSON: {e}")

    def get_events(self, limit=100, event_type=None, person_name=None, start_date=None, end_date=None):
        """
        Retrieve events from storage.

        Args:
            limit: Maximum number of events to return
            event_type: Filter by event type
            person_name: Filter by person name
            start_date: Filter events after this date (ISO format)
            end_date: Filter events before this date (ISO format)

        Returns:
            List of event dictionaries
        """
        try:
            if self.storage_type == 'sqlite':
                return self.get_events_sqlite(limit, event_type, person_name, start_date, end_date)
            else:
                return self.get_events_json(limit, event_type, person_name, start_date, end_date)
        except Exception as e:
            self.logger.error(f"Failed to retrieve events: {e}")
            return []

    def get_events_sqlite(self, limit, event_type, person_name, start_date, end_date):
        """Retrieve events from SQLite database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                query = "SELECT * FROM events WHERE 1=1"
                params = []

                if event_type:
                    query += " AND event_type = ?"
                    params.append(event_type)

                if person_name:
                    query += " AND person_name = ?"
                    params.append(person_name)

                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date)

                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date)

                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)

                cursor = conn.execute(query, params)
                rows = cursor.fetchall()

                events = []
                for row in rows:
                    event = dict(row)
                    event['details'] = json.loads(event['details']) if event['details'] else {}
                    events.append(event)

                return events

        except Exception as e:
            self.logger.error(f"Failed to retrieve events from SQLite: {e}")
            return []

    def get_events_json(self, limit, event_type, person_name, start_date, end_date):
        """Retrieve events from JSON files."""
        try:
            events = []
            # Get all JSON log files
            for filename in os.listdir(self.logs_dir):
                if filename.startswith('events_') and filename.endswith('.json'):
                    filepath = os.path.join(self.logs_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            file_events = json.load(f)
                            events.extend(file_events)
                    except Exception as e:
                        self.logger.error(f"Failed to read log file {filename}: {e}")

            # Filter events
            filtered_events = []
            for event in events:
                if event_type and event.get('event_type') != event_type:
                    continue
                if person_name and event.get('person_name') != person_name:
                    continue
                if start_date and event.get('timestamp', '') < start_date:
                    continue
                if end_date and event.get('timestamp', '') > end_date:
                    continue
                filtered_events.append(event)

            # Sort by timestamp descending and limit
            filtered_events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return filtered_events[:limit]

        except Exception as e:
            self.logger.error(f"Failed to retrieve events from JSON: {e}")
            return []

    def get_event_stats(self):
        """Get statistics about logged events."""
        try:
            events = self.get_events(limit=1000)  # Get recent events for stats

            stats = {
                'total_events': len(events),
                'event_types': {},
                'alert_status_counts': {},
                'person_counts': {},
                'recent_events': events[:10]  # Last 10 events
            }

            for event in events:
                # Count event types
                event_type = event.get('event_type', 'unknown')
                stats['event_types'][event_type] = stats['event_types'].get(event_type, 0) + 1

                # Count alert statuses
                alert_status = event.get('alert_status', 'none')
                stats['alert_status_counts'][alert_status] = stats['alert_status_counts'].get(alert_status, 0) + 1

                # Count persons
                person_name = event.get('person_name')
                if person_name:
                    stats['person_counts'][person_name] = stats['person_counts'].get(person_name, 0) + 1

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get event statistics: {e}")
            return {
                'total_events': 0,
                'event_types': {},
                'alert_status_counts': {},
                'person_counts': {},
                'recent_events': []
            }

    def get_recent_logs(self, limit=10):
        """Get recent log entries."""
        # Future: implement retrieving logs from database or files
        return []  # Placeholder