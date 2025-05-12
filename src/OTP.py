import smtplib
import random
from email.mime.text import MIMEText

# Configure your authorized Gmail account
EMAIL_ADDRESS = "researchsnake.com@gmail.com"
EMAIL_PASSWORD = "oelx quea zbdh jugv"  # Use App Password for security


def generate_otp():
    return str(random.randint(100000, 999999))  # 6-digit OTP


def send_otp_email(recipient_email):
    otp = generate_otp()
    subject = "Your OTP Code"
    body = f"Your OTP for verification is: {otp}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, recipient_email, msg.as_string())

    return otp
