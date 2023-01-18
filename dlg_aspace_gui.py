import PySimpleGUI as psg
import as_export as asx
import gc

from loguru import logger


def run_gui():
    defaults = psg.UserSettings()
    close_program, client, repositories = get_aspace_login(defaults, as_un, as_pw, as_api)  # Need to fill this out more

    layout = []

    main_window = psg.Window('DLG > ASpace Workflow', layout, resizable=True)
    logger.info('Initiate GUI window')
    while True:
        gc.collect()
        main_event, main_values = main_window.Read()
        if main_event == 'Cancel' or main_event is None or main_event == "Exit":
            logger.info("User initiated closing program")
            main_window.close()
            break


def get_aspace_login(as_un=None, as_pw=None, as_api=None, as_client=None, as_repos=None):
    if as_repos is None:
        repositories = {"Search Across Repositories (Sys Admin Only)": None}
    else:
        repositories = as_repos
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
            aspace_session = asx.ASpace(as_un, as_pw, as_api)
            aspace_client = aspace_session.aspace_login()
    return aspace_client