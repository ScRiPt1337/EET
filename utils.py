import dearpygui.dearpygui as dpg

set_value_mail_list = None
set_value_attachment_path = None
def select_mail_list(sender, app_data, user_data,caller=None):
    global set_value_mail_list
    if caller == "smtp":
        set_value_mail_list = "mail_list_path"
    else:
        set_value_mail_list = "mail_list_path_owa"
    dpg.show_item("mail_list_file_dialog_id")

def select_attachment(sender, app_data, user_data,caller=None):
    global set_value_attachment_path
    if caller == "smtp":
        set_value_attachment_path = "attachment_path"
    else:
        set_value_attachment_path = "attachment_path_owa"
    dpg.show_item("attachment_file_dialog_id")

dpg.create_context()

with dpg.file_dialog(directory_selector=False, show=False, callback=lambda s, a, u: dpg.set_value(set_value_mail_list, a['file_path_name']), id="mail_list_file_dialog_id", modal=False):
    dpg.add_file_extension(".csv", color=(255, 0, 0, 255))
    dpg.add_file_extension(".*")

with dpg.file_dialog(directory_selector=False, show=False, callback=lambda s, a, u: dpg.set_value(set_value_attachment_path, a['file_path_name']), id="attachment_file_dialog_id", modal=False):
    dpg.add_file_extension(".*")
    dpg.add_file_extension(".txt", color=(0, 255, 0, 255))
    dpg.add_file_extension(".pdf", color=(0, 255, 0, 255))
    dpg.add_file_extension(".docx", color=(0, 255, 0, 255))
    dpg.add_file_extension(".xlsx", color=(0, 255, 0, 255))
    dpg.add_file_extension(".png", color=(0, 255, 0, 255))
    dpg.add_file_extension(".jpg", color=(0, 255, 0, 255))
    dpg.add_file_extension(".zip", color=(0, 255, 0, 255))