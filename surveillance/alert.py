import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from config import Config

class Alert:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Future: configure email settings in config
        self.smtp_server = 'smtp.gmail.com'  # Example
        self.smtp_port = 587
        self.sender_email = 'your-email@gmail.com'
        self.sender_password = 'your-password'

    def send_email_alert(self, subject, message, recipient):
        """Send an email alert."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, recipient, text)
            server.quit()

            self.logger.info(f"Alert email sent to {recipient}")
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")

    def send_sms_alert(self, message, phone_number):
        """Send an SMS alert."""
        # Placeholder for SMS integration
        # Future: integrate with Twilio or similar service
        self.logger.info(f"SMS alert to {phone_number}: {message}")
        print(f"SMS alert: {message}")  # Placeholder

    def trigger_alert(self, alert_type, details):
        """Trigger an alert based on type."""
        if alert_type == 'intruder':
            subject = "Intruder Detected"
            message = f"An unknown person has been detected. Details: {details}"
            # Future: get recipient from config
            self.send_email_alert(subject, message, 'admin@example.com')
        elif alert_type == 'motion':
            # Future: implement motion alerts
            pass
        # Future: add more alert types