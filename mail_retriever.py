import imaplib
import poplib
import email
from email.parser import BytesParser
from email.policy import default
import os

async def retrieve_emails(protocol, server, port, username, password, mailbox, use_ssl, display_emails, update_progress, save_directory):
    try:
        if protocol == "IMAP":
            if use_ssl:
                conn = imaplib.IMAP4_SSL(server, port)
            else:
                conn = imaplib.IMAP4(server, port)
            conn.login(username, password)
            conn.select(mailbox)
            typ, data = conn.search(None, 'ALL')
            email_ids = data[0].split()
            total_emails = len(email_ids)
            emails = []

            for i, email_id in enumerate(email_ids):
                typ, msg_data = conn.fetch(email_id, '(RFC822)')
                msg = BytesParser(policy=default).parsebytes(msg_data[0][1])
                emails.append(msg)
                update_progress(i + 1, total_emails)  # Update progress with current count and total

            
            conn.logout()
        
        elif protocol == "POP3":
            if use_ssl:
                conn = poplib.POP3_SSL(server, port)
            else:
                conn = poplib.POP3(server, port)
            conn.user(username)
            conn.pass_(password)
            email_ids, _ = conn.stat()
            emails = []

            for i in range(email_ids):
                typ, msg_data, octets = conn.retr(i + 1)
                msg = BytesParser(policy=default).parsebytes(b'\n'.join(msg_data))
                emails.append(msg)
                update_progress(i / email_ids)
            
            conn.quit()
        
        if save_directory:
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)
            for i, email in enumerate(emails):
                with open(os.path.join(save_directory, f'email_{i}.eml'), 'wb') as f:
                    f.write(email.as_bytes())

        display_emails(emails)

    except Exception as e:
        display_emails([], error=str(e))