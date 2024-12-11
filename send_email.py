import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'eachen1010@gmail.com'
SENDER_PASSWORD = 'vmlsewqoyyrspeqq'
RECIPIENT_EMAIL = 'eachen1010@gmail.com'


def send_email(subject, body, receiver_email):
    # Create MIMEText object
    message = MIMEText(body)
    message['Subject'] = subject
    message['From'] = SENDER_EMAIL
    message['To'] = receiver_email

    # Connect to Gmail's SMTP server
    with smtplib.SMTP('smtp.gmail.com', 587) as server:  # Note the use of port 587 for STARTTLS
        server.ehlo()
        server.starttls()  # Secure the connection
        server.ehlo()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(message)  # Send the email

        print("Email sent successfully!")


