import os
import certifi
import dearpygui.dearpygui as dpg
from smtp_mailer_ui import open_smtp_mailer
from mail_retriever_ui import open_mail_retriever
from mail_retriever import retrieve_emails
# from owa_mailer_ui import open_owa_mailer
# from owa_retriver_ui import open_owa_retriever
import urllib3

urllib3.disable_warnings()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

def open_owa_mailer():
    pass

def open_owa_retriever():
    pass

def main():
    dpg.create_context()

    with dpg.window(label="CONTROL ROOM", width=500, height=300,no_close=True):
        dpg.add_button(label="SMTP MAILER", callback=open_smtp_mailer)
        dpg.add_button(label="Mail READER", callback=lambda: open_mail_retriever(retrieve_emails))
        dpg.add_button(label="OWA Mailer (2FA BYPASS) (Private)", callback=open_owa_mailer)
        dpg.add_button(label="OWA Retriever (2FA BYPASS)(Private)", callback=open_owa_retriever)

    dpg.create_viewport(title='Email Enumeration Tool', width=600, height=400)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()