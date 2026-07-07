import os 
import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import re

from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL",EMAIL_ADDRESS)

SMTP_SERVER = os.getenv("SMTP_SERVER","smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT","587"))

if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise EnvironmentError(
        "EMAIL_ADDRESS and EMAIL_PASSWORD must be set in your .env file"
    )


def briefing_to_html(text: str) -> str:
    """Convert '- [Topic] summary' bullet lines into an HTML list with bold topic tags."""
    lines = [line.strip("- ").strip() for line in text.strip().split("\n") if line.strip()]

    items = []
    for line in lines:
        match = re.match(r"\[(.+?)\]\s*(.*)", line)
        if match:
            topic, rest = match.groups()
            items.append(
                f"<li style='margin-bottom:12px;'>"
                f"<span style='font-weight:bold; font-size:1.05em; color:#1a5276;'>{topic}</span> "
                f"— {rest}</li>"
            )
        else:
            items.append(f"<li style='margin-bottom:12px;'>{line}</li>")

    return f"<ul style='padding-left:20px; list-style-type:none;'>{''.join(items)}</ul>"


def send_briefing_email(briefing_text: str):

    today_str = datetime.now().strftime("%B %d, %Y")
    subject = f"DoomScroller Night Briefing - {today_str}"

    message = MIMEMultipart("alternative")
    message['From'] = EMAIL_ADDRESS
    message['To'] = RECIPIENT_EMAIL
    message['Subject'] = subject

    # Plain-text fallback for clients that don't render HTML
    message.attach(MIMEText(briefing_text, "plain", "utf-8"))

    # HTML version
    briefing_html = briefing_to_html(briefing_text)
    html_content = f"""\
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #222; max-width: 600px;">
    <h2 style="border-bottom: 2px solid #333; padding-bottom: 8px;">🌙 DoomScroller Night Briefing — {today_str}</h2>
    {briefing_html}
  </body>
</html>
"""
    message.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(message)

        print(f"Briefing emailed to {RECIPIENT_EMAIL}")
    except smtplib.SMTPAuthenticationError:
        raise RuntimeError(
            "SMTP authentication failed. If using Gmail, make sure you're using "
            "an App Password, not your regular account password"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to send briefing email: {e}")