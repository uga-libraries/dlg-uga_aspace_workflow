import json
import requests
import re
# from dateutil.parser import *
import urllib.parse
import asnake.logging as logging

from gui import logger
from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError

indicator_field_regex = re.compile(r"(^indicator_+\d)")
type_field_regex = re.compile(r"(^type_+\d)")


class ASpace:

    def __init__(self, username, password, api):
        """
        ArchivesSpace session using ASnake Client

        :param str username: username for ASpace user, acquired during GUI aspace_login
        :param str password: password for ASpace user, acquired during GUI aspace_login
        :param str api: API URL for ASpace instance, acquired during GUI aspace_login
        """

        self.username = username
        """str: ArchivesSpace username provided by user"""
        self.password = password
        """str: ArchivesSpace password provided by user"""
        self.api = api
        """str: ArchivesSpace API URL provided by user"""
        self.client = None
        """str: ArchivesSnake client as created through ASnakeClient"""
        self.repositories = None
        """dict: All repositories in an ArchivesSpace instance, key = name, value = repo ID #"""

    # 1st step - user login to ASpace with creds
    def test_api(self):
        """
        Tests if the connection to the API

        :returns str api_message: message indicating if an error occurred, empty string if no error
        """
        api_message = ''
        try:
            requests.get(self.api)
        except Exception as api_error:
            api_message = "Your API credentials were entered incorrectly.\nPlease try again.\n\n" + \
                            api_error.__str__()
        return api_message

    def aspace_login(self):
        """
        Logs in to ASnake Client, returns error message if occurs

        :return str error_message: error message is login error occurs, None if ok
        """

        # logging.setup_logging(level='DEBUG')
        error_message = None
        try:
            self.client = ASnakeClient(baseurl=self.api, username=self.username, password=self.password)
            self.client.authorize()
        except ASnakeAuthError as connection_error:
            error_message = 'Your username and/or password were entered\n incorrectly. Please try again.\n\n'
            if ':' in str(connection_error):
                error_divided = str(connection_error).split(":")
                for line in error_divided:
                    error_message += line + "\n"
            else:
                error_message = str(connection_error)
        return error_message

    def get_repos(self):
        """
        Gets and returns a dictionary of repositories in an ASpace instance {repo_name: repo_id}

        :return dict self.repositories: repositories in an ASpace instance {repo_name: repo_id}
        """
        self.repositories = {}
        repo_results = self.client.get('/repositories')
        repo_results_dec = json.loads(repo_results.content.decode())
        for result in repo_results_dec:
            uri_components = result["uri"].split("/")
            self.repositories[result["name"]] = int(uri_components[-1])
        return self.repositories

    # 2nd step - user inputs a spreadsheet of top containers with barcodes or top_container ASpace URI

    # 3rd step - code takes spreadsheet, searches for top containers on ASpace

    def get_tcuri(self, barcode, repository):
        """
        Gets the top container URI for a specific barcode in an ASpace repository

        :param int barcode: of the barcode of the top container to search for
        :param int repository: integer of the repository ID to search within the ASpace instance

        :return str uri_error: returns an error message if multiple or no results found, otherwise None
        :return list tc_uri: top container URI
        """
        uri_error = None
        search_tcs = json.loads(self.client.get(f'repositories/{repository}/top_containers/search',
                                                params={'q': f'barcode_u_sstr:{barcode}',
                                                        'type[]': '["top_container"]'}).text)
        tc_uri = [result['uri'] for result in search_tcs['response']['docs']]
        if len(tc_uri) > 1:
            uri_error = True
            tc_uri.insert(0, f'Multiple results found with same barcode: {barcode}')
        elif len(tc_uri) == 0:
            uri_error = True
            tc_uri.insert(0, f'No results found for: {barcode}')
        return uri_error, tc_uri

    # 4th step - get archival objects associated with top containers - use collection ref (URI) to narrow searching for archival objects within collection
    # use https://archivesspace.github.io/archivesspace/api/?shell#fetch-tree-information-for-the-top-level-resource-record - go through each archival object?

    def get_archobjs(self, barcode, repository):
        """
        Gets the archival objects associated with a top container

        :param list tc_uri: list of the top container URI

        :return list ao_results: list of all archival objects associated with the top container
        :return str archobjs_error: error message of search if occurred, empty string otherwise
        """
        # barcode = 32108050893687  # use these for unittests
        # repository = 4  # use these for unittests
        # ao_results = None
        archobjs_error = ""
        search_aos = self.client.get_paged(f'repositories/{repository}/search', params={'q': f'{barcode}', 'type': ['archival_object']})
        # print(type(search_aos), search_aos)
        # Above for testing purposes only, unless we have to use instead of filter_term query
        ao_results = [result for result in search_aos]
        if "error" in search_aos:
            print(f'Error when searching for barcode: {search_aos}')
            archobjs_error = "Error when searching for barcode: {search_aos}"
        # print(len(ao_results))
        # print(f'Length: {len(ao_results[0])}\n{ao_results[0]["id"]}\n\n')  # This seems to grab all 27 associated archival objects


        # for top_cont in tc_uri:
        #     # print(tc_uri)  # /repositories/4/top_containers/45245
        #     # encoded_uri = urllib.parse.quote(tc_uri, 'UTF-8')  # tried utf8
        #     # print(encoded_uri)  # %2Frepositories%2F4%2Ftop_containers%2F45245
        #     search_aos = self.client.get_paged(f'repositories/4/search',
        #                                        params={'filter_query[]': f'top_container_uri_u_sstr:{top_cont}',
        #                                                'type': ['archival_object']})
        #     print(search_aos)
        #     ao_results = [result for result in search_aos]
        #     print(len(ao_results))  # 322873 - it's grabbing all archival objects, filter_query returns 0
        return ao_results, archobjs_error


class ArchivalObject:

    resource_uri = ""
    """str: ArchivesSpace URI for the parent resource"""    # TODO: Split this info into another class "ResourceObject" with these class variable as instance variables
    resource_lang = ""
    """str: Language of materials for the parent resource record"""
    resource_citation = ""
    """str: Preferred citation note for the parent resource record"""
    resource_creator = ""
    """str: Agent with type Creator for the parent resource record"""
    resource_subpers = ""
    """str: Agent with type Subject for the parent resource record"""
    resource_subj = ""
    """str: Subject with type topical for the parent resource record"""
    resource_subjmed = ""
    """str: Subject with type genre_form for the parent resource record"""
    resource_subjspatial = ""
    """str: Subject with type geographic for the parent resource record"""

    def __init__(self, archival_object, dlg_id):
        """
        Archival object with specific fields for DLG workflow

        :param json archival_object: json object of the archival object
        :param str dlg_id: ID for DLG Collection ID column
        """
        self.arch_obj = archival_object
        """str: Dictionary of archival object metadata"""
        self.dlg_id = dlg_id
        """str: ID for DLG Collection ID column"""
        self.arch_obj_uri = ""
        """str: ArchivesSpace URI for the archival object"""
        self.title = ""
        """str: Title of the archival object"""
        self.creator = ArchivalObject.resource_creator
        """str: Creator(s) of the collection, multiple separated by ||"""
        self.subject = ArchivalObject.resource_subj
        """str: Subject terms for resource, multiple separated by ||"""
        self.description = ""
        """str: Description of the archival object, found in scope and content note"""
        self.date = ""
        """str: Date of the archival object, formatted YYYY-MM-DD, YYYY-MM, YYYY or YYYY/YYYY"""
        self.subject_spatial = ArchivalObject.resource_subjspatial
        """str: Subjects geographic/spatial of the resource, multiple separated by ||"""
        self.subject_medium = ArchivalObject.resource_subjmed
        """str: Subjects medium/genre/format of the resource, multiple separated by ||"""
        self.extent = ""
        """str: Extent note of the archival object, if available"""
        self.language = ArchivalObject.resource_lang
        """str: Language of material of the resource, usually eng"""
        self.citation = ArchivalObject.resource_citation
        """str: Preferred citation of the resource"""
        self.subject_personal = ArchivalObject.resource_subpers
        """str: Subject person of the resource, multiple separated by ||"""
        self.resource = ""
        """str: Resource record URI of the parent resource of the archival object"""
        self.box = ""
        """str: The top container type and indicator for the archival object"""
        self.child = ""
        """str: The container instance child type and indicator for the archival object"""
        self.grandchild = ""
        """str: The container instance grandchild type and indicator for the archival object"""
        self.record_id = ""
        """str: Combined dlg_id with box #, folder #, and item # when available"""

    def parse_archobj(self, asp_client):
        """
        Parses an archival object json record to assign instance variables

        :return None:
        """
        box_indicator = ""
        child_indicator = ""
        grandchild_indicator = ""
        json_info = json.loads(self.arch_obj["json"])

        # Get title
        for key, value in json_info.items():
            if key == "title":
                self.title = json_info["title"]
            # Get dates
            if key == "dates":
                begin = ""
                end = ""
                express_date = ""
                if json_info["dates"]:
                    for date in json_info["dates"]:
                        for date_field, date_value in date.items():  # TODO - need to change format: YYYY-MM-DD, YYYY-MM, YYYY or YYYY/YYYY
                            if date_field == "begin":
                                begin = date["begin"]
                            if date_field == "end":
                                end = date["end"]
                            if date_field == "expression":
                                express_date = date["expression"]  # TODO - stuck on how to normalize dates
                if begin and not end:
                    self.date = f'{begin}'
                elif not begin and end:
                    self.date = f'{end}'
                elif begin and end:
                    self.date = f'{begin}/{end}'
                elif express_date:
                    self.date = f'{express_date}'
            # Get notes
            if key == "notes":
                for note in json_info["notes"]:
                    if note["type"] == "scopecontent":
                        complete_note = ""
                        if "content" in note:
                            for note_component in note["content"]:
                                complete_note += f'{note_component} '
                        elif "subnotes" in note:
                            for subnote in note['subnotes']:
                                if "content" in subnote:
                                    complete_note += subnote["content"]
                        self.description = complete_note.strip()
                    if note["type"] == "prefercite":
                        complete_note = ""
                        for note_component in note["content"]:
                            complete_note += f'{note_component} '
                        self.citation = complete_note.strip()
                    if note["type"] == "extent":
                        complete_note = ""
                        for note_component in note["content"]:
                            complete_note += f'{note_component} '
                        self.extent = complete_note.strip()
            # Get Box, Child, Grandchild
            if key == "instances":
                for instance in json_info["instances"]:
                    if "sub_container" in instance:
                        for sc_field, sc_value in instance["sub_container"].items():
                            type_match = type_field_regex.match(sc_field)
                            indicator_match = indicator_field_regex.match(sc_field)
                            if indicator_match:
                                sc_indicator = instance["sub_container"][indicator_match.string]
                                if indicator_match.string[-1] == "2":
                                    child_indicator = sc_indicator
                                    if self.child:
                                        self.child += f' {child_indicator}'
                                elif indicator_match.string[-1] == "3":
                                    grandchild_indicator = sc_indicator
                                    if self.grandchild:
                                        self.grandchild += f' {grandchild_indicator}'
                            elif type_match:
                                type_indicator = instance["sub_container"][type_match.string]
                                if type_match.string[-1] == "2":
                                    self.child += sc_value + f' {child_indicator}'
                                if type_match.string[-1] == "3":
                                    self.grandchild += sc_value + f' {grandchild_indicator}'
                            elif sc_field == "top_container":
                                tc_type = ""
                                for tc_field, tc_value in instance["sub_container"]["top_container"]["_resolved"].items():
                                    if tc_field == "type":
                                        tc_type = tc_value
                                    elif tc_field == "indicator":
                                        box_indicator = tc_value
                                self.box = f'{tc_type} {box_indicator}'
            # Get resource URI
            if key == "resource":
                self.resource = json_info["resource"]["ref"]
                if json_info["resource"]["ref"] != ArchivalObject.resource_uri:
                    ArchivalObject.get_resource_info(self, asp_client)
            # Get archival object URI
            if key == "uri":
                self.arch_obj_uri = json_info["uri"]
        # Create record_id for DLG
        indicators = [box_indicator, child_indicator, grandchild_indicator]
        record_id_composite = f'{self.dlg_id}_'
        for indicator in indicators:
            if indicator:
                try:
                    int_indicator = int(indicator)
                except:
                    logger.info(f'TypeError with: {self.arch_obj_uri}\n{indicators}')
                    record_id_composite += f'{indicator}?-'
                else:
                    record_id_composite += f'{int_indicator:03}-'
                finally:
                    self.record_id = record_id_composite[:-1]

    def get_resource_info(self, asp_client):
        """
        Intakes an ASpace client and gets the resource info for an archival object and assigns instance variables

        :param asp_client: ArchivesSnake client as created through ASnakeClient

        :return None:
        """
        resource_info = asp_client.get(self.resource).json()

        # Set resource_uri
        ArchivalObject.resource_uri = resource_info["uri"]

        # Get Language of Materials
        ArchivalObject.resource_lang = self.language = resource_info["lang_materials"][0]["language_and_script"]["language"]

        for key, value in resource_info.items():
            # Get Preferred Citation note
            if "notes" == key:
                for note in resource_info["notes"]:
                    if "type" in note:
                        if note["type"] == "prefercite":
                            for subnote in note["subnotes"]:
                                ArchivalObject.resource_citation = self.citation = subnote["content"]
            # Get Creator, Subject Person
            if "linked_agents" == key:
                creators = ""
                personals = ""
                for linked_agent in resource_info["linked_agents"]:
                    if linked_agent["role"] == "creator":
                        agent_ref = linked_agent["ref"]
                        agent_json = asp_client.get(agent_ref, params={"resolve[]": True}).json()
                        creators += agent_json["title"] + "||"
                    if linked_agent["role"] == "subject":
                        person_ref = linked_agent["ref"]
                        person_json = asp_client.get(person_ref, params={"resolve[]": True}).json()
                        if "agent_type" in person_json:
                            if person_json["agent_type"] == "agent_person":
                                if "." in person_json["title"]:
                                    personals += person_json["title"].rstrip(".") + "||"
                                else:
                                    personals += person_json["title"] + "||"
                ArchivalObject.resource_creator = self.creator = creators[:-2]
                ArchivalObject.resource_subpers = self.subject_personal = personals[:-2]
            # Get Subjects
            if "subjects" == key:
                subjects = ""
                spatials = ""
                mediums = ""
                for subject in resource_info["subjects"]:
                    subject_ref = subject["ref"]
                    subject_json = asp_client.get(subject_ref, params={"resolve[]": True}).json()
                    for subject_field, subject_value in subject_json.items():
                        if subject_field == "terms":
                            if "term_type" in subject_json["terms"][0]:
                                if subject_json["terms"][0]["term_type"] == "genre_form":
                                    if "." in subject_json["title"]:
                                        mediums += subject_json["title"].rstrip(".") + "||"
                                    else:
                                        mediums += subject_json["title"] + "||"
                                if subject_json["terms"][0]["term_type"] == "topical":
                                    if "." in subject_json["title"]:
                                        subjects += subject_json["title"].rstrip(".") + "||"
                                    else:
                                        subjects += subject_json["title"] + "||"
                                if subject_json["terms"][0]["term_type"] == "geographic":
                                    if "." in subject_json["title"]:
                                        spatials += subject_json["title"].rstrip(".") + "||"
                                    else:
                                        spatials += subject_json["title"] + "||"
                ArchivalObject.resource_subj = self.subject = subjects[:-2]
                ArchivalObject.resource_subjspatial = self.subject_spatial = spatials[:-2]
                ArchivalObject.resource_subjmed = self.subject_medium = mediums[:-2]

