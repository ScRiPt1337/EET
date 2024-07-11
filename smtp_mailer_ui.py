import dearpygui.dearpygui as dpg
from smtp_mailer import send_email, stop_sending
from utils import select_mail_list, select_attachment
# from tracking import open_tracking_popup, is_tracking_enabled, get_tracking_details
import json

headers = []
sending_emails = False
email_hashes = {}

def open_smtp_mailer(sender, app_data, user_data):
    if dpg.does_item_exist("smtp_mailer_window"):
        dpg.delete_item("smtp_mailer_window")
        
    with dpg.window(label="SMTP MAILER", modal=False, width=500, height=600, tag="smtp_mailer_window"):
        dpg.add_input_text(label="Send From", default_value="example@example.com", tag="send_from")
        dpg.add_input_text(label="Subject", tag="subject")
        dpg.add_input_text(label="SMTP Server", default_value="smtp.example.com", tag="smtp_server")
        dpg.add_input_text(label="SMTP Port", default_value="587", tag="smtp_port")
        dpg.add_input_text(label="Username", tag="username")
        dpg.add_input_text(label="Password", password=True, tag="password")
        dpg.add_combo(label="SMTP Connection Type", items=["None", "SSL", "TLS"], default_value="None", tag="smtp_connection_type")
        dpg.add_slider_int(label="Delay Between Messages (seconds)", min_value=0, max_value=60, default_value=0, tag="delay_slider")
        dpg.add_combo(label="Letter Type", items=["HTML", "Plain Text"], default_value="Plain Text", tag="letter_type")
        dpg.add_button(label="Choose Attachment", callback=select_attachment)
        dpg.add_input_text(label="Attachment Path", readonly=True, tag="attachment_path")
        
        dpg.add_input_text(label="Message", multiline=True, height=100, tag="message")
        dpg.add_button(label="Explain Placeholders", callback=explain_placeholders)
        
        dpg.add_input_text(label="Random ID Length", default_value="8", tag="random_id_length")
        dpg.add_button(label="Choose Mail List", callback=select_mail_list)
        dpg.add_input_text(label="Mail List Path", readonly=True, tag="mail_list_path")
        dpg.add_button(label="Set Headers", callback=open_set_header_popup)
        # dpg.add_button(label="Add Tracking", callback=open_tracking_popup)
        dpg.add_button(label="Send Mail", tag="send_button", callback=send_smtp_mail)
        dpg.add_button(label="Reset", callback=reset_smtp_mailer)

def explain_placeholders(sender, app_data, user_data):
    if dpg.does_item_exist("placeholder_popup"):
        dpg.delete_item("placeholder_popup")
        
    with dpg.window(label="Placeholder Explanation", modal=True, width=300, height=200, tag="placeholder_popup"):
        dpg.add_text("{name} - Will be replaced with the recipient's name in the letter from the mail list.")
        dpg.add_text("{position} - Will be replaced with the recipient's position in the letter from the mail list")
        dpg.add_text("{date} - Will be replaced with the current date.")
        dpg.add_text("{random_id} - Will be replaced with a random ID of specified length.")
        dpg.add_button(label="Close", callback=lambda: dpg.delete_item("placeholder_popup"))

def open_set_header_popup(sender, app_data, user_data):
    if dpg.does_item_exist("set_header_popup"):
        dpg.delete_item("set_header_popup")
        
    with dpg.window(label="Set Headers", modal=False, width=400, height=300, tag="set_header_popup"):
        for i in range(5):
            dpg.add_text(f"Header {i+1}")
            dpg.add_input_text(label="Key", tag=f"header_key_{i}")
            dpg.add_input_text(label="Value", tag=f"header_value_{i}")
        dpg.add_button(label="Save", callback=save_headers)
        dpg.add_button(label="Cancel", callback=lambda: dpg.delete_item("set_header_popup"))

def save_headers(sender, app_data, user_data):
    headers.clear()
    for i in range(5):
        key = dpg.get_value(f"header_key_{i}")
        value = dpg.get_value(f"header_value_{i}")
        if key and value:
            headers.append((key, value))
    print("Headers saved:", headers)
    dpg.delete_item("set_header_popup")

def send_smtp_mail(sender, app_data, user_data):
    global sending_emails
    if sending_emails:
        stop_sending()
        sending_emails = False
        dpg.set_item_label("send_button", "Send Mail")
        return

    send_from = dpg.get_value("send_from")
    send_to = dpg.get_value("send_to")
    subject = dpg.get_value("subject")
    smtp_server = dpg.get_value("smtp_server")
    smtp_port = dpg.get_value("smtp_port")
    username = dpg.get_value("username")
    password = dpg.get_value("password")
    smtp_connection_type = dpg.get_value("smtp_connection_type")
    delay = dpg.get_value("delay_slider")
    letter_type = dpg.get_value("letter_type")
    attachment_path = dpg.get_value("attachment_path")
    message = dpg.get_value("message")
    random_id_length = int(dpg.get_value("random_id_length"))
    mail_list_path = dpg.get_value("mail_list_path")

    # tracking_enabled = is_tracking_enabled()
    # tracker_url, tracker_hash = get_tracking_details() if tracking_enabled else (None, None)

    if dpg.does_item_exist("logs_popup"):
        dpg.delete_item("logs_popup")

    with dpg.window(label="Logs", modal=False, width=500, height=400, tag="logs_popup"):
        dpg.add_text("Sending emails...", tag="log_text")
        dpg.add_button(label="Close", callback=lambda: dpg.delete_item("logs_popup"))

    sending_emails = True
    dpg.set_item_label("send_button", "Stop")
    send_email(send_from, subject, smtp_server, smtp_port, username, password, smtp_connection_type, delay, letter_type, attachment_path, message, random_id_length, mail_list_path, headers, False, "tracker_url", "tracker_hash", update_logs)

def update_logs(log):
    if dpg.does_item_exist("log_text"):
        current_logs = dpg.get_value("log_text")
        dpg.set_value("log_text", current_logs + "\n" + log)

def reset_smtp_mailer(sender, app_data, user_data):
    dpg.set_value("send_from", "example@example.com")
    dpg.set_value("subject", "")
    dpg.set_value("smtp_server", "smtp.example.com")
    dpg.set_value("smtp_port", "587")
    dpg.set_value("username", "")
    dpg.set_value("password", "")
    dpg.set_value("smtp_connection_type", "None")
    dpg.set_value("delay_slider", 0)
    dpg.set_value("letter_type", "Plain Text")
    dpg.set_value("attachment_path", "")
    dpg.set_value("message", "")
    dpg.set_value("random_id_length", "8")
    dpg.set_value("mail_list_path", "")
    if dpg.does_item_exist("logs_popup"):
        dpg.delete_item("logs_popup")