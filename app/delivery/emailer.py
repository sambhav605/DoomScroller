import os 
import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from dotenv import load_dotenv

load_dotenv

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL",EMAIL_ADDRESS)

SMTP_SERVER = os.getenv("SMTP_SERVER","smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT","587"))

if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise EnvironmentError(
        "EMAIL_ADDRESS and EMAIL_PASSWORD must be set in your .env file"
    )

def send_briefing_email(briefing_text:str):

    today_str = datetime.now().strftime("%B %d, %Y")
    subject = f"DoomScroller Night Briefing - {today_str}"

    message = MIMEMultipart()
    message['From'] = EMAIL_ADDRESS
    message['To'] = RECIPIENT_EMAIL
    message['Subject'] = subject
    message.attach(MIMEText(briefing_text,"plain","utf-8"))

    try:
        with smtplib.SMTP(SMTP_SERVER,SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
            server.send_message(message)

        print(f"Briefing emailed to {RECIPIENT_EMAIL}")
    except smtplib.SMTPAuthenticationError:
        raise RuntimeError(
            "SMTP authentication failed. If using Gmail, make sure you'rr using"
            "an App Password, not your regular account password"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to send briefing email:{e}")