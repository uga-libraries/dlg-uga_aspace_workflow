import aspace
import gc
import os
import platform
import PySimpleGUI as psg
import re
import shutil
import spreadsheet
import subprocess
import sys
import threading
import time
import webbrowser

from loguru import logger
from pathlib import Path

id_combined_regex = re.compile(r'[\W_]+', re.UNICODE)

WRITE_AOS_THREAD = "-WAOS_THREAD-"
GET_AOS_THREAD = "-GAOS_THREAD-"  # would have to figure out how to return linked_objects, archobjs_error in thread

logger.remove()
logger.add(str(Path('logs', 'log_{time:YYYY-MM-DD}.log')),
           format="{time}-{level}: {message}")

id_field_regex = re.compile(r"(^id_+\d)")
collid_regex = re.compile(r"(?<=ms|ua).*|(?<=MS ).*")


@logger.catch
def run_gui():
    """
    Handles the GUI operation as outlined by PySimpleGUI's guidelines.

    For an in-depth review on how this code is structured, see the PySimpleGUI User Manual:
    https://www.pysimplegui.org/en/latest/#pysimplegui-users-manual

    # :param dict defaults: contains the data from defaults.json file, all data the user has specified as default

    :returns None:
    """
    # gc.disable()
    defaults = psg.UserSettings()
    close_program, aspace_instance, repositories = get_aspace_login(defaults)

    if close_program is True:
        logger.info("User initiated closing program")
        sys.exit()

    menu_opts = [['File',
                 ['Clear Output Folder',
                  '---',
                  'Change ASpace Login Credentials',
                  '---',
                  'Reset Defaults',
                  '---',
                  'Exit']
                  ],
                 ['Help',
                 ['User Manual',
                  'About']
                  ]
                 ]

    column1 = [[psg.Text("Enter Barcodes or Top Container URIs:", font=("Roboto", 12))],
               [psg.Multiline(key="_CONT_INPUT_", size=(37, 23), focus=True,
                              tooltip=' Enter top container barcodes or URIs here and separate either by comma or '
                                      'newline (enter) ')]]

    column2 = [[psg.Text("Choose your repository:", font=("Roboto", 12))],
               [psg.DropDown(list(repositories.keys()), readonly=True,
                             default_value=defaults["repo_default"], size=(50, 5), key="_REPO_SELECT_",
                             auto_size_text=True),
                psg.Push(),
                psg.Button(" SAVE ", key="_SAVE_REPO_")],
               [psg.FileBrowse(' Select ASpace>DLG Template ', file_types=(("Excel Files", "*.xlsx"),), ),
                psg.InputText(default_text=defaults['_AS-DLG_FILE_'], size=(33, 5), key='_AS-DLG_FILE_')],
               [psg.Button(' START ', key='_WRITE_AOS_', disabled=False),
                psg.Push(),
                psg.Button(" Open Output Folder ", key="_OPEN_AS-DLG_", disabled=False)],
               [psg.Output(size=(60, 17), key="_OUTPUT_")]]

    layout = [[psg.Menu(menu_opts)], [psg.Column(column1), psg.Column(column2)]]

    main_window = psg.Window('ASpace > DLG Workflow', layout, resizable=True)
    logger.info('Initiate GUI window')
    while True:
        # gc.collect()
        main_event, main_values = main_window.Read()
        if main_event == 'Cancel' or main_event is None or main_event == "Exit":
            logger.info("User initiated closing program")
            break
        if main_event == "_SAVE_REPO_":
            defaults["repo_default"] = main_values["_REPO_SELECT_"]
            logger.info(f'User saved repository default: {main_values["_REPO_SELECT_"]}')
        if main_event == "_WRITE_AOS_":
            if not main_values["_REPO_SELECT_"]:
                psg.Popup("WARNING!\nPlease select a repository")
                logger.warning("User did not select a repository")
            else:
                if os.path.exists(main_values["_AS-DLG_FILE_"]) is not True:
                    psg.Popup("WARNING!\nThe file you selected for the ASpace>DLG Template does not exist."
                              "\nTry selecting another file")
                    logger.error(f'ASpace>DLG Template error: User selected file that does not exist\n'
                                 f'{main_values["_AS-DLG_FILE_"]}')
                else:
                    try:
                        open(main_values["_AS-DLG_FILE_"], "r+")
                    except IOError as open_error:
                        logger.error(f'Could not open:\n{main_values["_AS-DLG_FILE_"]}\n{open_error}\n')
                        psg.Popup(f'Could not open:\n{main_values["_AS-DLG_FILE_"]}\n\n'
                                  f'Make sure to close the spreadsheet before continuing')
                    else:
                        try:
                            template_file = shutil.copy(main_values["_AS-DLG_FILE_"], str(Path(os.getcwd(),
                                                                                           "output_files")))
                        except OSError as e:
                            logger.info(f'Tried copying template file, error thrown: {e}')
                            template_file = str(Path(os.getcwd(), "output_files", Path(main_values["_AS-DLG_FILE_"]).name))
                        defaults["_AS-DLG_FILE_"] = template_file
                        ss_inst = spreadsheet.Spreadsheet
                        try:
                            barcodes = ss_inst.sort_input(main_values['_CONT_INPUT_'])
                        except Exception as sort_error:
                            logger.error(f'sort_input ERROR:\n{sort_error}')
                            print(f'sort_input ERROR:\n{sort_error}')
                        else:
                            row_num = 2  # 2 because 1 is header row
                            for barcode in barcodes:
                                # uri_error, tc_uri = aspace_instance.get_tcuri(barcode,
                                #                                               repositories[main_values["_REPO_SELECT_"]])
                                #
                                # if uri_error is True:
                                #     for message in tc_uri:
                                #         print(message)
                                # else:
                                linked_objects, archobjs_error = aspace_instance.get_archobjs(barcode, repositories[main_values["_REPO_SELECT_"]])
                                if archobjs_error:
                                    logger.error(f'get_archobjs ERROR: {archobjs_error}')
                                    print(archobjs_error)
                                else:
                                    resource_links, selections, cancel = parse_linked_objs(linked_objects,
                                                                                           aspace_instance)
                                    # args = (resource_links, selections, cancel, main_values, aspace_instance,
                                    #         linked_objects,
                                    #         row_num, ss_inst, main_window)
                                    row_num, collection_file = write_aos(resource_links, selections, cancel,
                                                                         main_values, aspace_instance, linked_objects,
                                                                         row_num, ss_inst, template_file, main_window)
                                    print(row_num)
                                    # start_thread(write_aos, args, main_window)  # TODO - when there are multiple barcodes, multiple threads are created and write over each other - causing the errors!
                                    # logger.info("WRITE_AOS_THREAD started")  # TODO - change GUI to take in raw input of barcodes or top container URIs like in ASpace batch exporter w/resource ids
                            logger.info(f'Finished {str(row_num - 2)} exports')
                            trailing_line = 56 - len(f'Finished {str(row_num - 2)} exports') - (len(str(row_num - 2)) - 1)
                            print("\n" + "-" * 40 + "Finished {} exports".format(str(row_num - 2)) + "-" * trailing_line + "\n")
        # if main_event in (WRITE_AOS_THREAD):
        #     main_window[f'{"_WRITE_AOS_"}'].update(disabled=False)
        #     main_window[f'{"_OPEN_AS-DLG_"}'].update(disabled=False)
        if main_event == "_OPEN_AS-DLG_":
            if os.path.exists(Path(os.getcwd(), "output_files")):
                open_file(str(Path(os.getcwd(), "output_files")))
            else:
                print("No folder found")
                logger.error(f'No output_files folder found - user initiated open folder')
        # ---------- MENU OPTIONS SECTION ------------
        # ------------------- FILE -------------------
        if main_event == "Clear Output Folder":
            clear_exports(str(Path(os.getcwd(), "output_files")))
        if main_event == "Change ASpace Login Credentials":
            get_aspace_login(defaults)
        if main_event == "Reset Defaults":
            reset_defaults = psg.PopupYesNo("You are about to reset your configurations. Are you sure? \n"
                                            "You will have to restart the program to see changes.")
            if reset_defaults == "Yes":
                logger.info("User initiated reseting defaults")
                defaults_dict = None
                try:
                    user_defaults = psg.UserSettings()
                    defaults_dict = user_defaults.load()
                    for setting in defaults_dict.keys():
                        defaults_dict[setting] = None
                    user_defaults.save()
                except Exception as e:
                    print(f'Error when resetting defaults: {e}\n{defaults_dict}')
                    logger.error(f'Error when resetting defaults: {e}\n{defaults_dict}')
                else:
                    print('User defaults reset successfully\n')
                    logger.info(f'User reset defaults: {defaults_dict}')
        # ------------------- HELP -------------------
        if main_event == "About":
            logger.info(f'User initiated About menu option')
            window_about_active = True
            layout_about = [
                [psg.Text("Created by Corey Schmidt for the University of Georgia Libraries\n\n"
                          "Version: DEVELOPMENT\n\n"
                          "To check for the latest versions, check the Github\n", font=("Roboto", 12))],
                [psg.OK(bind_return_key=True, key="_ABOUT_OK_"), psg.Button(" Check Github ", key="_CHECK_GITHUB_"),
                 psg.Button(" Check GUI Info ", key="_CHECK_PYPSG_")]
            ]
            window_about = psg.Window("About this program", layout_about)
            while window_about_active is True:
                event_about, values_about = window_about.Read()
                if event_about is None:
                    window_about.close()
                    window_about_active = False
                if event_about == "_CHECK_GITHUB_":
                    try:
                        webbrowser.open("https://github.com/uga-libraries/dlg-uga_aspace_workflow/releases",
                                        new=2)
                    except Exception as e:
                        print(f'Failed to open webbrowser: {e}')
                        logger.error(f'Failed to open webbrowser: {e}')
                if event_about == "_CHECK_PYPSG_":
                    try:
                        psg.popup_scrolled(psg.get_versions(), non_blocking=True, keep_on_top=True)
                    except Exception as e:
                        print(f'Failed to open PySimpleGUI versions popup: {e}')
                        logger.error(f'Failed to open PySimpleGUI versions popup: {e}')
                if event_about == "_ABOUT_OK_":
                    window_about.close()
                    window_about_active = False
        if main_event == "User Manual":
            try:
                webbrowser.open("https://github.com/uga-libraries/dlg-uga_aspace_workflow/wiki/User-Manual",
                                new=2)
            except Exception as e:
                print(f'Failed to open webbrowser: {e}')
                logger.error(f'Failed to open webbrowser: {e}')


def get_aspace_login(defaults):
    """
    Gets a user's ArchiveSpace credentials.

    There are 3 components to it, the setup code, correct_creds while loop, and the window_asplog_active while loop. It
    uses ASnake.client to authenticate and stay connected to ArchivesSpace. Documentation for ASnake can be found here:
    https://archivesspace-labs.github.io/ArchivesSnake/html/index.html

    :param defaults: contains data from defaults.json file, all data the user has specified as default

    :returns bool close_program: if a user exits the popup, this will return true and end run_gui()
    :returns aspace_instance: an instance of the ASpace class, containing the ASnake client for accessing and connecting
     to the API
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
                    logger.error(api_message)
                else:
                    connect_client = aspace_instance.aspace_login()
                    if connect_client is not None:
                        psg.Popup(connect_client)
                        logger.error(connect_client)
                    else:
                        repositories = aspace_instance.get_repos()
                        defaults["as_api"] = values_log["_ASPACE_API_"]
                        window_asplog_active = False
            if event_log is None or event_log == 'Cancel':
                window_login.close()
                close_program = True
                break
        window_login.close()
        return close_program, aspace_instance, repositories


def write_aos(resource_links, selections, cancel, main_values, aspace_instance, linked_objects, row_num, ss_inst,
              template_file, gui_window):
    """
    Parses provided spreadsheet for barcodes, searches them in ASpace, parses returned archival objects, and writes to
    user provided spreadsheet template

    :param dict resource_links: key = resource ID, value = list of linked archival objects for that resource
    :param list selections: list containing one resource selected by the user to add archival objects to the spreadsheet
    :param bool cancel: cancel the selection window if user exits out of selection popup
    :param main_values: PySimpleGUI main window values
    :param aspace_instance: Instance of the ASpace class, used for making requests to the API
    :param list linked_objects: list of all archival objects associated with the top container
    :param int row_num: row counter - keeps track of which row to write to
    :param ss_inst: openpyxl Sheet instance of the current sheet a user is writing to
    :param str template_file: path to the template file to copy and rename to collection file
    :param gui_window: PySimpleGUI's window class instance, used for tracking threads

    :return int row_num: row counter - keeps track of which row to write to
    :return str collection_file: filepath for output file generated from template
    """
    collection_file = ""
    if cancel is not True:
        if selections:
            for resource in selections:
                if resource in resource_links:
                    row_num, collection_file = get_archres(resource, ss_inst, row_num, aspace_instance, main_values,
                                                           resource_links[resource], template_file)
        else:
            for res_id, linked_object in resource_links.items():
                row_num, collection_file = get_archres(res_id, ss_inst, row_num, aspace_instance, main_values,
                                                       linked_objects, template_file)
    else:
        logger.info(f'User cancelled resource selection {resource_links.keys()}')
    # gui_window.write_event_value('-WAOS_THREAD-', (threading.current_thread().name,))
    return row_num, collection_file


def parse_linked_objs(linked_objects, aspace_instance):
    """
    Parses a returned list of linked archival objects to create resource ids, dict with resource_id key and archival
    object JSON as value, and selections if a user needs to select a specific resource record

    :param list linked_objects: list of JSON dictionaries of all linked archival objects associated with a top container
    :param aspace_instance: instance of the ASpace class, used for client requests

    :return dict resource_links: key = resource ID, value = list of linked archival objects for that resource
    :return list selections: should be a list with 1 string of the resource ID a user selects with select_resource()
    :return bool cancel: If user exits select_resource() GUI window, set to True to not write archival objects
    """
    resource_links = {}
    resource_ids = []
    selections = []
    cancel = None
    for linked_object in linked_objects:
        combined_aspace_id = ""
        parent_resource = aspace_instance.client.get(linked_object["resource"],
                                                     params={"resolve[]": True}).json()
        for resource_field, resource_value in parent_resource.items():
            id_match = id_field_regex.match(resource_field)
            if id_match:
                combined_aspace_id += resource_value + "-"
        combined_aspace_id = combined_aspace_id[:-1]
        if combined_aspace_id not in resource_ids:
            resource_ids.append(combined_aspace_id)
            resource_links[combined_aspace_id] = [linked_object]
        else:
            resource_links[combined_aspace_id].append(linked_object)
    if len(resource_ids) > 1:
        selections, cancel = select_resource(resource_ids)
    return resource_links, selections, cancel


def select_resource(resource_ids):
    """
    GUI window for a user to select from multiple resources associated with a top container

    :param list resource_ids: resource ids for user to select ex. ms1238a

    :return list selections: resource id selected by the user
    :return bool cancel: if a user wants to cancel selection, cancel = True
    """
    selections = []
    cancel = None
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
            cancel = True
            multres_window.close()
            break
        if multres_event == "_MULTRES-SELECT_":
            selections = multres_values["_RES-IDS_"]
            multres_window.close()
            break
    return selections, cancel


def get_archres(res_id, ss_inst, row_num, aspace_instance, main_values, linked_objects, template_file):
    """
    Creates an ArchivalObject and Resource instances and writes data to the user provided template spreadsheet

    :param str res_id: resource identifier
    :param ss_inst: instance of the openpyxl spreadsheet for the user provided template spreadsheet to write to
    :param int row_num: row number counter to track how many rows have been written to
    :param aspace_instance: instance of ArchivesSpace from aspace.py
    :param dict main_values: main window GUI values
    :param list linked_objects: archival object json strings linked to the associated barcode
    :param str template_file: path to the template file to copy, rename, and remove

    :return int row_num: row number counter to track how many rows have been written to
    :return str collection_file: filepath for output file generated from template
    """
    if collid_regex.findall(res_id):
        clean_collnum = id_combined_regex.sub('', collid_regex.findall(res_id)[0])
    else:
        clean_collnum = id_combined_regex.sub('', res_id)
    dlg_id = f'guan_{clean_collnum}'
    resource_obj = aspace.ResourceObject()
    collection_file = ""
    for linked_object in linked_objects:
        arch_obj = aspace.ArchivalObject(linked_object, dlg_id)
        resource_obj = arch_obj.parse_archobj(aspace_instance.client, resource_obj)
        if not collection_file:
            collection_file = template_file.replace(Path(template_file).stem, arch_obj.dlg_id)
            if not os.path.exists(collection_file):
                os.rename(template_file, collection_file)
            else:
                if os.path.exists(template_file):
                    os.remove(template_file)
        try:
            ss_inst.write_template(collection_file, arch_obj, resource_obj, row_num,
                                   main_values["_REPO_SELECT_"])
        except Exception as e:
            print(f'Error writing data to spreadsheet: {e}\n'
                  f'Archival Object URI: {arch_obj.arch_obj_uri}\n')
            logger.error(f'Error writing data to spreadsheet: {e}\n'
                         f'Archival Object URI: {arch_obj.arch_obj_uri}\n')
        row_num += 1
        logger.info(f'{arch_obj.record_id} added\n')
        print(f'{arch_obj.record_id} added\n')
    return row_num, collection_file


def open_file(filepath):
    """
    Takes a filepath and opens the folder according to Windows, Mac, or Linux.

    :param str filepath: the filepath of the folder/directory a user wants to open
    """
    logger.info(f'Fetching filepath: {filepath}')
    if platform.system() == "Windows":
        os.startfile(filepath)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", filepath])
    else:
        subprocess.Popen(["xdg-open", filepath])


def delete_log_files():  # unittest for this? how?
    """
    Deletes log file(s) found in logs folder if file(s) are older than 1 month.
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


def clear_exports(folder_path):
    """
    Takes user input to open specified directory for exported files.

    Args:
        folder_path (str): the key to the folder path found in the defaults.json file, ex. _OUTPUT_DIR_

    Returns:
        None
    """
    logger.info(f'Clearing output directory: {folder_path}')
    clean_files = os.listdir(folder_path)
    try:
        if len(clean_files) > 0:
            file_count = 0
            for file in clean_files:
                file_count += 1
                full_path = str(Path(folder_path, file))
                if not os.path.isdir(full_path):
                    os.remove(full_path)
                else:
                    file_count -= 1
                    print(f'Could not remove item: {file} from {folder_path}')
                    logger.info(f'Could not remove item: {file} from {folder_path}')
            print(f'Deleted {str(file_count)} files in {folder_path}')
            logger.info(f'Deleted {file_count} files in {folder_path}')
        else:
            print(f'No files in {folder_path}\n')
    except Exception as e:
        print(f'Error deleting files from {folder_path}\n' + str(e))
        logger.error(f'Error deleting files from {folder_path}: {e}')


def start_thread(function, args, gui_window):
    """
    Starts a thread and disables buttons to prevent multiple requests/threads.

    :param function: the function to pass to the thread
    :param tuple args: the arguments to pass to the function with ending ,. Ex. (arg, arg, arg,)
    :param gui_window: the GUI window used by PySimpleGUI. Used to return an event
    """
    logger.info(f'Starting thread: {function}')
    ead_thread = threading.Thread(target=function, args=args)
    ead_thread.start()
    gui_window[f'{"_WRITE_AOS_"}'].update(disabled=True)
    gui_window[f'{"_OPEN_AS-DLG_"}'].update(disabled=True)


def setup_files():
    """
    Checks for directories in the current directory the GUI or .exe is located and tries to open defaults.json
    Returns:
        json_data (dict): contains data from defaults.json for user's default settings
    """
    logger.info(f'Checking setup files...')
    current_directory = os.getcwd()
    if not os.path.exists(Path(current_directory, "output_files")):
        print("\nNo output_files folder found, creating new one...", end='', flush=True)
        current_directory = os.getcwd()
        folder = "output_files"
        source_path = os.path.join(current_directory, folder)
        os.mkdir(source_path)
        print("{} folder created\n".format(folder))


if __name__ == "__main__":
    logger.info(f'GUI version info:\n{"Version Number: DEVELOPMENT"}\n{psg.get_versions()}')
    delete_log_files()
    setup_files()
    run_gui()
