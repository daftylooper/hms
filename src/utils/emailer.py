import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

def send_email(subject, body, to_email):
    # Email server settings
    smtp_host = "smtp.gmail.com"  # You can replace this with your email provider's SMTP server
    smtp_port = 587  # Use 465 for SSL, 587 for TLS
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    # Create the email message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    # Attach the email body to the message
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to the SMTP server and send the email
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()  # Secure the connection using TLS
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

load_dotenv()
