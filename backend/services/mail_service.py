import smtplib
from email.mime.text import MIMEText


def send_html_email(app, to_email: str, subject: str, html: str):
    host = app.config.get('SMTP_HOST')
    port = app.config.get('SMTP_PORT')
    sender = app.config.get('SMTP_SENDER')
    username = app.config.get('SMTP_USERNAME')
    password = app.config.get('SMTP_PASSWORD')
    use_tls = app.config.get('SMTP_USE_TLS', False)

    if not host or not port or not sender:
        raise ValueError('SMTP configuration is incomplete.')

    msg = MIMEText(html, 'html')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email

    with smtplib.SMTP(host, port, timeout=10) as server:
        if use_tls:
            server.starttls()
        if username and password:
            server.login(username, password)
        server.send_message(msg)