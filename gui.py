import aspace
import gc
import os
import PySimpleGUI as psg
import re
import spreadsheet
import sys
import threading
import time

from loguru import logger
from pathlib import Path

logger.remove()
logger.add(str(Path('logs', 'log_{time:YYYY-MM-DD}.log')),
           format="{time}-{level}: {message}")

id_field_regex = re.compile(r"(^id_+\d)")
collid_regex = re.compile(r"(?<=ms|ua).*")


def run_gui():
    """
    Handles the GUI operation as outlined by PySimpleGUI's guidelines.

    For an in-depth review on how this code is structured, see the wiki:
    https://github.com/uga-libraries/ASpace_Batch_Export-Cleanup-Upload/wiki/Code-Structure#run_gui

    # :param dict defaults: contains the data from defaults.json file, all data the user has specified as default

    :returns None:
    """
    defaults = psg.UserSettings()
    close_program, aspace_instance, repositories = get_aspace_login(defaults)

    if close_program is True:
        logger.info("User initiated closing program")
        sys.exit()

    layout = [[psg.Text("Choose your repository:", font=("Roboto", 12))],
              [psg.DropDown(list(repositories.keys()), readonly=True,
                            default_value=defaults["repo_default"], key="_REPO_SELECT_",),
               psg.Button(" SAVE ", key="_SAVE_REPO_")],
              [psg.FileBrowse(' Select Top Container File ',
                              file_types=(("CSV Files", "*.csv"),),),
               psg.InputText(key='_TC_FILE_')],
              [psg.FileBrowse(' Select ASpace>DLG Template ', file_types=(("Excel Files", "*.xlsx"),),),
               psg.InputText(default_text=defaults['_AS-DLG_FILE_'], key='_AS-DLG_FILE_')],
              [psg.Button(' START ', key='_WRITE_AOS_', disabled=False)],
              [psg.Output(size=(80, 18), key="_output_")],
              [psg.Button(" Open ASpace > DLG Template File ", key="_OPEN_AS-DLG_")]]

    main_window = psg.Window('ASpace > DLG Workflow', layout, resizable=True)
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
        if main_event == "_WRITE_AOS_":
            #  1: grab top container spreadsheet, parse it and return a list of barcodes
            #  2: take list of barcodes and feed them into aspace to get tc_uris or list of archival objects
            #  3: for loop through list of archival objects - instance of ArchivalObject pass to spreadsheet.py and
            #  write data - will have to make more calls to aspace to get resource level info.
            defaults["_AS-DLG_FILE_"] = main_values["_AS-DLG_FILE_"]
            ss_inst = spreadsheet.Spreadsheet
            barcodes = ss_inst.get_barcodes(main_values['_TC_FILE_'])
            for barcode in barcodes:
                # uri_error, tc_uri = aspace_instance.get_tcuri(barcode, repositories[main_values["_REPO_SELECT_"]])
                #
                # if uri_error is True:
                #     for message in tc_uri:
                #         print(message)
                # else:
                linked_objects, archobjs_error = aspace_instance.get_archobjs(barcode,
                                                                              repositories[main_values["_REPO_SELECT_"]])
                if archobjs_error:
                    print(archobjs_error)
                else:
                    row_num = 2
                    resource_links = {}
                    resource_ids = []  # TODO add to arch_obj instance - guan_id - NOTE - exclude ms, ua from beginning - ms1385a >> guan_1385a
                    selections = []
                    for linked_object in linked_objects:
                        combined_aspace_id = ""
                        print(linked_object)
                        parent_resource = aspace_instance.client.get(linked_object["resource"],
                                                                     params={"resolve[]": True}).json()
                        for key, value in parent_resource.items():
                            id_match = id_field_regex.match(key)
                            if id_match:
                                combined_aspace_id += value + "-"
                        combined_aspace_id = combined_aspace_id[:-1]
                        if combined_aspace_id not in resource_ids:
                            resource_ids.append(combined_aspace_id)
                        resource_links[combined_aspace_id] = linked_object
                    if len(resource_ids) > 1:
                        multres_layout = [[psg.Text("Choose which resource you want archival objects linked:")],
                                          [psg.Listbox(values=resource_ids, key="_RES-IDS_",
                                                       size=(30, 6))],
                                          [psg.Button(" SELECT ", key="_MULTRES-SELECT_")]]

                        multres_window = psg.Window('Select Resources', multres_layout, resizable=True)
                        logger.info('Select Resources window')
                        while True:
                            multres_event, multres_values = multres_window.Read()
                            if multres_event == 'Cancel' or multres_event is None or multres_event == "Exit":
                                logger.info("User initiated closing Select Resources window")
                                multres_window.close()
                                break
                            if multres_event == "_MULTRES-SELECT_":
                                selections = multres_values["_RES-IDS_"]
                                multres_window.close()
                                break
                    if selections:
                        for resource in selections:  # TODO - won't work if only 1
                            if resource in resource_links:
                                if collid_regex.match(resource):
                                    collnum = collid_regex.match(resource)
                                else:
                                    collnum = resource
                                dlg_id = f'guan_{collnum}'
                                arch_obj = aspace.ArchivalObject(resource_links[resource], dlg_id)
                                arch_obj.parse_archobj()
                                arch_obj.get_resource_info(aspace_instance.client)
                                # print(arch_obj.__dict__)
                                ss_inst.write_template(main_values["_AS-DLG_FILE_"], arch_obj, row_num)
                                row_num += 1
                                print("\n\n\n")
                    else:
                        for res_id, linked_object in resource_links.items():
                            if collid_regex.match(res_id):
                                collnum = collid_regex.match(res_id)
                            else:
                                collnum = res_id
                            dlg_id = f'guan_{collnum}'
                            arch_obj = aspace.ArchivalObject(resource_links[res_id], dlg_id)
                            arch_obj.parse_archobj()
                            arch_obj.get_resource_info(aspace_instance.client)
                            # print(arch_obj.__dict__)
                            ss_inst.write_template(main_values["_AS-DLG_FILE_"], arch_obj, row_num)
                            row_num += 1
                            print("\n\n\n")
            # pass


def get_aspace_login(defaults):
    """
    Gets a user's ArchiveSpace credentials.

    There are 3 components to it, the setup code, correct_creds while loop, and the window_asplog_active while loop. It
    uses ASnake.client to authenticate and stay connected to ArchivesSpace. Documentation for ASnake can be found here:
    https://archivesspace-labs.github.io/ArchivesSnake/html/index.html

    :param defaults: contains data from defaults.json file, all data the user has specified as default

    :returns bool close_program: if a user exits the popup, this will return true and end run_gui()
    :returns aspace_instance: an instance of the ASpace class, containing the ASnake client for accessing and connecting to the API
    :returns dict repositories: repositories in the ASpace instance, Name (key): repo_id_# (value)
    """
    aspace_instance = None
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
                aspace_instance = aspace.ASpace(username=values_log["_ASPACE_UNAME_"],
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
        return close_program, aspace_instance, repositories


def delete_log_files():  # unittest for this? how?
    """
    Deletes log file(s) found in logs folder if file(s) are older than 1 month.

    :returns None:
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


def start_thread(function, args, gui_window):  # TODO: implement threading so Windows doesn't try to kill the app
    """
    Starts a thread and disables buttons to prevent multiple requests/threads.

    :param function: the function to pass to the thread
    :param tuple args: the arguments to pass to the function with ending ,. Ex. (arg, arg, arg,)
    :param gui_window: the GUI window used by PySimpleGUI. Used to return an event

    :returns None:
    """
    logger.info(f'Starting thread: {function}')
    ead_thread = threading.Thread(target=function, args=args)
    ead_thread.start()
    gui_window[f'{"_WRITE_AOS_"}'].update(disabled=True)


if __name__ == "__main__":
    logger.info(f'GUI version info:\n{psg.get_versions()}')
    delete_log_files()
    run_gui()
