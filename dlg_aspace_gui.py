import as_export as asx
import gc
import os
import PySimpleGUI as psg
import time

from loguru import logger
from pathlib import Path

logger.remove()
logger.add(str(Path('logs', 'log_{time:YYYY-MM-DD}.log')),
           format="{time}-{level}: {message}")


def run_gui():
    defaults = psg.UserSettings()
    close_program, client, repositories = get_aspace_login(defaults)

    layout = [[psg.Text("Choose your repository:", font=("Roboto", 12))],
              [psg.DropDown(list(repositories.keys()), readonly=True,
                            default_value=defaults["repo_default"], key="_REPO_SELECT_",),
               psg.Button(" SAVE ", key="_SAVE_REPO_")],
              [psg.FileBrowse(' Select Top Container File ',
                              file_types=(("Excel Files", "*.xlsx"),),),
               psg.InputText(key='_DO_FILE_')],
              [psg.FileBrowse(' Select ASpace>DLG Template ', file_types=(("Excel Files", "*.xlsx"),),),
               psg.InputText(default_text=defaults['_AS-DLG_FILE_'], key='_AS-DLG_FILE_')],
              [psg.Button(' START ', key='_WRITE_AOS_', disabled=False)],
              [psg.Output(size=(80, 18), key="_output_")],
              [psg.Button(" Open ASpace > DLG Template File ", key="_OPEN_AS-DLG_")]]

    main_window = psg.Window('DLG > ASpace Workflow', layout, resizable=True)
    logger.info('Initiate GUI window')
    while True:
        gc.collect()
        main_event, main_values = main_window.Read()
        if main_event == 'Cancel' or main_event is None or main_event == "Exit":
            logger.info("User initiated closing program")
            main_window.close()
            break
        if main_event == "_SAVE_REPO_":
            defaults["repo_default"] = main_values["_REPO_SELECT_"]


def get_aspace_login(defaults):
    connect_client = None
    repositories = {}
    window_asplog_active = True
    correct_creds = False
    close_program = False
    while correct_creds is False:
        asplog_col1 = [[psg.Text("ArchivesSpace username:", font=("Roboto", 11))],
                       [psg.Text("ArchivesSpace password:", font=("Roboto", 11))],
                       [psg.Text("ArchivesSpace API URL:", font=("Roboto", 11))]]
        asplog_col2 = [[psg.InputText(focus=True, key="_ASPACE_UNAME_")],
                       [psg.InputText(password_char='*', key="_ASPACE_PWORD_")],
                       [psg.InputText(defaults["as_api"], key="_ASPACE_API_")]]
        layout_asplog = [
            [psg.Column(asplog_col1, key="_ASPLOG_COL1_", visible=True),
             psg.Column(asplog_col2, key="_ASPLOG_COL2_", visible=True)],
            [psg.Button(" Save and Continue ", bind_return_key=True, key="_SAVE_CLOSE_LOGIN_")]
        ]
        window_login = psg.Window("ArchivesSpace Login Credentials", layout_asplog)
        while window_asplog_active is True:
            event_log, values_log = window_login.Read()
            if event_log == "_SAVE_CLOSE_LOGIN_":
                aspace_instance = asx.ASpace(username=values_log["_ASPACE_UNAME_"],
                                             password=values_log["_ASPACE_PWORD_"],
                                             api=values_log["_ASPACE_API_"])
                api_message = aspace_instance.test_api()
                if api_message:
                    psg.Popup(api_message)
                else:
                    connect_client = aspace_instance.aspace_login()
                    if connect_client is not None:
                        psg.Popup(connect_client)
                    else:
                        repositories = aspace_instance.get_repos()
                        defaults["as_api"] = values_log["_ASPACE_API_"]
                        window_asplog_active = False
                        correct_creds = True
            if event_log is None or event_log == 'Cancel':
                window_login.close()
                window_asplog_active = False
                correct_creds = True
                close_program = True
                break
        window_login.close()
        return close_program, connect_client, repositories


def delete_log_files():  # unittest for this? how?
    """
    Deletes log file(s) found in logs folder if file(s) are older than 1 month.
    Returns:
        None
    """
    if os.path.isdir(Path(os.getcwd(), "logs")) is True:
        logsdir = str(Path(os.getcwd(), "logs"))
        for file in os.listdir(logsdir):
            logfile = Path(logsdir, file)
            file_time = os.path.getmtime(logfile)
            current_time = time.time()
            delete_time = current_time - 2630000  # This is for 1 month.
            if file_time <= delete_time:  # If a file is more than 1 month old, delete
                try:
                    os.remove(logfile)
                    logger.info(f'Removed logfile: {logfile}')
                except Exception as delete_log_error:
                    logger.error(f'Error deleting logfile {logfile}:\n{delete_log_error}')


if __name__ == "__main__":
    logger.info(f'GUI version info:\n{psg.get_versions()}')
    delete_log_files()
    run_gui()