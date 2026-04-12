import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from config import Config
import os
import cv2
import time
from datetime import datetime
from surveillance.logger import Logger

class Alert:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Alert configuration
        self.alert_cooldown = Config.ALERT_COOLDOWN_SECONDS  # seconds between duplicate alerts
        self.last_alert_time = 0
        self.snapshots_dir = Config.SNAPSHOTS_DIR
        self.alerts_log_file = Config.ALERTS_LOG_FILE

        # Create snapshots directory if it doesn't exist
        os.makedirs(self.snapshots_dir, exist_ok=True)

        # Email settings
        self.enable_email_alerts = Config.ENABLE_EMAIL_ALERTS
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.sender_email = Config.SENDER_EMAIL
        self.sender_password = Config.SENDER_PASSWORD
        self.alert_recipient_email = Config.ALERT_RECIPIENT_EMAIL
        self.email_subject_template = Config.EMAIL_SUBJECT_TEMPLATE

        # Initialize event logger
        self.event_logger = Logger()

        self.logger.info("Alert system initialized")

    def trigger_unknown_person_alert(self, frame, face_location=None, confidence=None):
        """
        Trigger alert for unknown person detection.

        Args:
            frame: Current video frame
            face_location: Tuple (x, y, w, h) of detected face
            confidence: Recognition confidence (optional)
        """
        current_time = time.time()

        # Check cooldown to avoid duplicate alerts
        if current_time - self.last_alert_time < self.alert_cooldown:
            self.logger.debug("Alert cooldown active, skipping duplicate alert")
            return

        self.last_alert_time = current_time

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save snapshot
        snapshot_path = self._save_snapshot(frame, timestamp)

        # Send email alert if enabled
        if self.enable_email_alerts and snapshot_path:
            try:
                self._send_email_alert_with_snapshot(alert_details, snapshot_path)
            except Exception as e:
                self.logger.error(f"Failed to send email alert: {e}")
                # Continue with other alert methods even if email fails

        # Create alert details
        alert_details = {
            'timestamp': timestamp,
            'type': 'unknown_person',
            'snapshot_path': snapshot_path,
            'face_location': face_location,
            'confidence': confidence
        }

        # Print terminal alert
        self._print_terminal_alert(alert_details)

        # Log alert to file
        self._log_alert(alert_details)

        # Log event using the event logger
        self.event_logger.log_event(
            event_type='unknown_person_detected',
            person_name='Unknown',
            snapshot_path=snapshot_path,
            alert_status='triggered',
            details={
                'face_location': face_location,
                'confidence': confidence,
                'cooldown_seconds': self.alert_cooldown
            }
        )

        # Trigger dashboard popup (this will be handled by the web app)
        # For now, we'll rely on the web app polling or WebSocket integration

        self.logger.info(f"Unknown person alert triggered at {timestamp}")

    def _save_snapshot(self, frame, timestamp):
        """Save snapshot image of the alert."""
        try:
            # Create filename with timestamp
            filename = f"alert_{timestamp.replace(' ', '_').replace(':', '-')}.jpg"
            filepath = os.path.join(self.snapshots_dir, filename)

            # Save the frame as JPEG
            cv2.imwrite(filepath, frame)

            self.logger.info(f"Snapshot saved: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Failed to save snapshot: {e}")
            return None

    def _print_terminal_alert(self, alert_details):
        """Print alert to terminal with timestamp."""
        timestamp = alert_details['timestamp']
        print(f"\n🚨 ALERT: Unknown person detected at {timestamp}")
        if alert_details['snapshot_path']:
            print(f"📸 Snapshot saved: {alert_details['snapshot_path']}")
        if alert_details['face_location']:
            x, y, w, h = alert_details['face_location']
            print(f"📍 Face location: ({x}, {y}, {w}, {h})")
        if alert_details['confidence'] is not None:
            print(".2f")
        print("-" * 50)

    def _log_alert(self, alert_details):
        """Log alert to file."""
        try:
            with open(self.alerts_log_file, 'a') as f:
                log_entry = f"{alert_details['timestamp']}|{alert_details['type']}"
                if alert_details['snapshot_path']:
                    log_entry += f"|{alert_details['snapshot_path']}"
                if alert_details['face_location']:
                    log_entry += f"|{alert_details['face_location']}"
                if alert_details['confidence'] is not None:
                    log_entry += ".3f"
                log_entry += "\n"
                f.write(log_entry)
        except Exception as e:
            self.logger.error(f"Failed to log alert: {e}")

    def get_recent_alerts(self, limit=10):
        """Get recent alerts from log file."""
        try:
            if not os.path.exists(self.alerts_log_file):
                return []

            alerts = []
            with open(self.alerts_log_file, 'r') as f:
                lines = f.readlines()[-limit:]  # Get last N lines

            for line in lines:
                parts = line.strip().split('|')
                if len(parts) >= 2:
                    alert = {
                        'timestamp': parts[0],
                        'type': parts[1],
                        'snapshot_path': parts[2] if len(parts) > 2 else None,
                        'face_location': eval(parts[3]) if len(parts) > 3 and parts[3] != 'None' else None,
                        'confidence': float(parts[4]) if len(parts) > 4 and parts[4] != 'None' else None
                    }
                    alerts.append(alert)

            return alerts

        except Exception as e:
            self.logger.error(f"Failed to read alerts log: {e}")
            return []

    def _send_email_alert_with_snapshot(self, alert_details, snapshot_path):
        """Send an email alert with snapshot attachment."""
        try:
            from email.mime.image import MIMEImage

            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.alert_recipient_email

            # Format subject with timestamp
            timestamp = alert_details['timestamp']
            subject = self.email_subject_template.format(timestamp=timestamp)
            msg['Subject'] = subject

            # Create message body
            body_parts = [
                f"Security Alert: Unknown person detected",
                f"Time: {timestamp}",
            ]

            if alert_details['face_location']:
                x, y, w, h = alert_details['face_location']
                body_parts.append(f"Face Location: ({x}, {y}, {w}, {h})")

            if alert_details['confidence'] is not None:
                body_parts.append(f"Recognition Confidence: {alert_details['confidence']:.2f}")

            body_parts.extend([
                "",
                "A snapshot has been attached to this email.",
                "",
                "This is an automated alert from your security system."
            ])

            message_body = "\n".join(body_parts)
            msg.attach(MIMEText(message_body, 'plain'))

            # Attach snapshot
            if os.path.exists(snapshot_path):
                with open(snapshot_path, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(snapshot_path))
                    msg.attach(img)
            else:
                self.logger.warning(f"Snapshot file not found for email attachment: {snapshot_path}")

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, self.alert_recipient_email, text)
            server.quit()

            self.logger.info(f"Email alert sent successfully to {self.alert_recipient_email}")

        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(f"SMTP authentication failed: {e}")
            raise
        except smtplib.SMTPConnectError as e:
            self.logger.error(f"SMTP connection failed: {e}")
            raise
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error sending email alert: {e}")
            raise

    def _send_basic_email_alert(self, subject, message):
        """Send a basic email alert without attachment."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.alert_recipient_email
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, self.alert_recipient_email, text)
            server.quit()

            self.logger.info(f"Basic email alert sent successfully to {self.alert_recipient_email}")

        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(f"SMTP authentication failed: {e}")
            raise
        except smtplib.SMTPConnectError as e:
            self.logger.error(f"SMTP connection failed: {e}")
            raise
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error sending basic email alert: {e}")
            raise

    def send_sms_alert(self, message, phone_number):
        """Send an SMS alert."""
        # Placeholder for SMS integration
        # Future: integrate with Twilio or similar service
        self.logger.info(f"SMS alert to {phone_number}: {message}")
        print(f"SMS alert: {message}")  # Placeholder

    def trigger_alert(self, alert_type, details):
        """Trigger an alert based on type."""
        if alert_type == 'intruder':
            if self.enable_email_alerts:
                try:
                    # Create basic alert details for email
                    alert_details = {
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'type': 'intruder',
                        'face_location': details.get('face_location'),
                        'confidence': details.get('confidence')
                    }

                    subject = f"Security Alert: Intruder Detected - {alert_details['timestamp']}"
                    message = f"An intruder has been detected. Details: {details}"

                    # Send email without attachment for now
                    self._send_basic_email_alert(subject, message)
                except Exception as e:
                    self.logger.error(f"Failed to send intruder email alert: {e}")
        elif alert_type == 'unknown_person':
            # This is handled by trigger_unknown_person_alert
            pass
        elif alert_type == 'motion':
            # Future: implement motion alerts
            pass
        # Future: add more alert types