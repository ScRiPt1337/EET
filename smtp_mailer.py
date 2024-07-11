import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import ssl
import time
import csv
from datetime import datetime
import json

stop_sending_emails = False
email_hashes = {}

def send_email(send_from, subject, smtp_server, smtp_port, username, password, smtp_connection_type, delay, letter_type, attachment_path, message, random_id_length, mail_list_path, headers, tracking_enabled, tracker_url, tracker_hash, update_logs):
    global stop_sending_emails
    stop_sending_emails = False
    try:
        # Setup the server connection based on the connection type
        if smtp_connection_type == "SSL":
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
        elif smtp_connection_type == "TLS":
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls(context=ssl.create_default_context())
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
        
        server.login(username, password)

        # Read the mail list
        with open(mail_list_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if stop_sending_emails:
                    break
                send_to = row.get('email', '')
                msg = MIMEMultipart()
                msg['From'] = send_from
                msg['To'] = send_to
                msg['Subject'] = subject

                # Add headers
                for header_key, header_value in headers:
                    msg[header_key] = header_value

                # Format the message
                formatted_message = message.format(name=row.get('name', ''), position=row.get('position', ''), date=str(datetime.now()), random_id=get_random_id(random_id_length))
                
                email_hash = get_random_id(random_id_length)
                email_hashes[email_hash] = row

                # Add tracking pixel if enabled
                if tracking_enabled:
                    tracking_pixel = f'<img src="{tracker_url}?hash={tracker_hash}&id={email_hash}" width="1" height="1" />'
                    if letter_type == "HTML":
                        formatted_message += tracking_pixel
                    else:
                        formatted_message += f'\n[Tracking Pixel: {tracker_url}?hash={tracker_hash}&id={email_hash}]'

                # Attach the message
                if letter_type == "HTML":
                    msg.attach(MIMEText(formatted_message, 'html'))
                else:
                    msg.attach(MIMEText(formatted_message, 'plain'))

                # Attach the file if any
                if attachment_path:
                    with open(attachment_path, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename= {attachment_path}")
                        msg.attach(part)

                # Send the email
                server.sendmail(send_from, send_to, msg.as_string())

                # Log the success
                log_message = f"Email sent successfully to {send_to} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                update_logs(log_message)

                # Wait for the specified delay
                time.sleep(delay)

        server.quit()
        update_logs("All emails sent successfully")
    except Exception as e:
        update_logs(f"Failed to send email: {e}")
    finally:
        save_email_hashes()

def stop_sending():
    global stop_sending_emails
    stop_sending_emails = True

def get_random_id(length):
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def save_email_hashes():
    with open("email_hashes.json", "w") as file:
        json.dump(email_hashes, file)