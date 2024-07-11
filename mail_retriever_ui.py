import dearpygui.dearpygui as dpg
import asyncio
import os
import threading
from mail_retriever import retrieve_emails
import mailparser
import base64
import tempfile
import webbrowser

retrieving_emails = False
emails_cache = []  # To store emails for searching

def open_mail_retriever(retrieve_emails_func):
    print("Opening Mail Retriever...")  # Debug print
    if dpg.does_item_exist("mail_retriever_popup"):
        dpg.delete_item("mail_retriever_popup")

    with dpg.window(label="MAIL READER", modal=False, width=400, height=650, tag="mail_retriever_popup"):
        dpg.add_input_text(label="Server", tag="retriever_server")
        dpg.add_input_text(label="Port (e.g., 993 for IMAP, 995 for POP3)", tag="retriever_port", default_value="993")
        dpg.add_input_text(label="Username", tag="retriever_username")
        dpg.add_input_text(label="Password", password=True, tag="retriever_password")
        dpg.add_input_text(label="Mailbox Name (e.g., INBOX)", tag="mailbox_name", default_value="INBOX")
        dpg.add_input_text(label="Save Directory", tag="save_directory", default_value=os.path.join(os.getcwd(), "emails"))
        dpg.add_combo(label="Protocol", items=["IMAP", "POP3"], default_value="IMAP", tag="retriever_protocol")
        dpg.add_checkbox(label="Use SSL", tag="retriever_ssl", default_value=True)
        dpg.add_button(label="Start Retrieval", tag="retriever_button", callback=lambda: start_retriever(retrieve_emails_func))
        dpg.add_progress_bar(label="Progress", default_value=0, width=380, tag="progress_bar")
        dpg.add_text("", tag="log_text")
        dpg.add_text("Default Ports:\nIMAP: 143 (non-SSL), 993 (SSL)\nPOP3: 110 (non-SSL), 995 (SSL)", wrap=380)
    
    dpg.show_item("mail_retriever_popup")
    print("Mail Retriever UI created.")  # Debug print

def start_retriever(retrieve_emails_func):
    global retrieving_emails
    if retrieving_emails:
        stop_retriever()
        retrieving_emails = False
        dpg.set_item_label("retriever_button", "Start Retrieval")
        return

    print("Starting email retrieval...")  # Debug print
    asyncio.run(retrieve_emails_task(retrieve_emails_func))

async def retrieve_emails_task(retrieve_emails_func):
    global retrieving_emails
    server = dpg.get_value("retriever_server")
    port_value = dpg.get_value("retriever_port")
    if port_value is None:
        dpg.set_value("log_text", "Error: Port is not specified.")
        return
    port = int(port_value)
    username = dpg.get_value("retriever_username")
    password = dpg.get_value("retriever_password")
    mailbox = dpg.get_value("mailbox_name")
    save_directory = dpg.get_value("save_directory")
    protocol = dpg.get_value("retriever_protocol")
    use_ssl = dpg.get_value("retriever_ssl")

    dpg.set_value("log_text", "Retrieving emails...")
    print("Retrieving emails with settings:", server, port, username, password, mailbox, save_directory, protocol, use_ssl)  # Debug print

    retrieving_emails = True
    dpg.set_item_label("retriever_button", "Stop")

    try:
        await retrieve_emails_func(protocol, server, port, username, password, mailbox, use_ssl, display_emails, update_progress, save_directory)
    finally:
        retrieving_emails = False
        dpg.set_item_label("retriever_button", "Start Retrieval")

def stop_retriever():
    global retrieving_emails
    retrieving_emails = False
    print("Email retrieval stopped.")  # Debug print

def update_progress(current, total):
    if dpg.does_item_exist("progress_bar"):
        progress = current / total
        dpg.set_value("progress_bar", progress)
        if progress >= 1.0:
            dpg.set_value("log_text", "Emails retrieved successfully")
        print(f"Progress updated: {progress * 100:.2f}%")

def decode_payload(part):
    try:
        return part.get_payload(decode=True).decode('utf-8')
    except UnicodeDecodeError:
        try:
            return part.get_payload(decode=True).decode('latin1')
        except UnicodeDecodeError:
            return "Cannot decode content"

def display_emails(emails, error=None):
    global emails_cache
    emails_cache = emails  # Cache the emails for searching

    print("Displaying emails...")  # Debug print
    if error:
        dpg.set_value("log_text", f"Error: {error}")
    else:
        dpg.set_value("log_text", "Emails retrieved successfully")
    
    if dpg.does_item_exist("emails_window"):
        dpg.delete_item("emails_window")
    
    print("Creating emails window...")  # Debug print
    with dpg.window(label="Emails", modal=False, width=600, height=400, tag="emails_window"):
        dpg.add_input_text(label="Search", tag="email_search", callback=lambda sender, app_data, user_data: filter_emails())
        dpg.add_separator()
        with dpg.group(tag="emails_list"):
            render_emails(emails)

    dpg.show_item("emails_window")
    print("Emails window displayed.")  # Debug print

def filter_emails():
    search_query = dpg.get_value("email_search").lower()
    filtered_emails = [email for email in emails_cache if search_query in str(email).lower()]
    render_emails(filtered_emails)
    print(f"Filtered emails with query: {search_query}")  # Debug print

def render_emails(emails):
    if dpg.does_item_exist("emails_list"):
        dpg.delete_item("emails_list", children_only=True)
    
    for i, email in enumerate(emails):
        print(f"Email {i}: {email.get('subject', 'No Subject')}")  # Debug print
        if email is None:
            continue
        from_ = email.get('from', 'Unknown Sender')
        subject = email.get('subject', 'No Subject')
        
        with dpg.group(parent="emails_list"):
            dpg.add_text(f"From: {from_}")
            dpg.add_text(f"Subject: {subject}")
            
            if email.is_multipart():
                parts = [decode_payload(part) for part in email.walk() if part.get_payload(decode=True)]
                preview_text = "".join([part for part in parts if part])[:100] + "..."
            else:
                payload = decode_payload(email)
                preview_text = payload[:100] + "..." if payload else "No content"
            
            dpg.add_text(f"Preview: {preview_text}")
            if "password" in str(email).lower():
                dpg.add_text("FOUND PASSWORD", color=[255, 0, 0])
            dpg.add_button(label="View", callback=view_email_details_callback(email))
            dpg.add_separator()
    print("Emails rendered.")  # Debug print

def view_email_details_callback(email):
    def callback(sender, app_data):
        view_email_details(email)
    return callback

def view_email_details(email):
    if email is None:
        return
    if dpg.does_item_exist("email_details_popup"):
        dpg.delete_item("email_details_popup")
    
    with dpg.window(label="Email Details", modal=False, width=600, height=400, tag="email_details_popup"):
        from_ = email.get('from', 'Unknown Sender')
        to_ = email.get('to', 'Unknown Recipient')
        subject = email.get('subject', 'No Subject')

        dpg.add_text(f"From: {from_}")
        dpg.add_text(f"To: {to_}")
        dpg.add_text(f"Subject: {subject}")
        dpg.add_text("Headers:")
        for header, value in email.items():
            dpg.add_text(f"{header}: {value}")

        mail = mailparser.parse_from_bytes(email.as_bytes())

        for attachment in mail.attachments:
            print(attachment)
            dpg.add_text(f"Attachment: {attachment['filename']}")
            dpg.add_button(label=f"Save {attachment['filename']}", callback=lambda: save_attachment(attachment))

        if mail.text_html:
            dpg.add_button(label="Open HTML Content", callback=lambda: open_html_content(mail.text_html[0]))
        else:
            dpg.add_text("Content:")
            dpg.add_text(mail.body)
        dpg.add_button(label="Close", callback=lambda: dpg.delete_item("email_details_popup"))

    dpg.show_item("email_details_popup")

def save_attachment(attachment):
    attachment_dir = os.path.join(os.getcwd(), "attachments")
    os.makedirs(attachment_dir, exist_ok=True)
    filename = os.path.join(attachment_dir, attachment['filename'])
    payload = attachment['payload']
    binary = attachment['binary']
    if binary:
        payload = base64.b64decode(payload)
    with open(filename, 'wb') as file:
        file.write(payload)
    print(f"Attachment {filename} saved successfully.")

def open_html_content(html_content):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_file:
        temp_file.write(html_content.encode('utf-8'))
        temp_file_path = temp_file.name
    webbrowser.open(f"file://{temp_file_path}")

def update_logs(log):
    if dpg.does_item_exist("log_text"):
        current_logs = dpg.get_value("log_text")
        dpg.set_value("log_text", current_logs + "\n" + log)
