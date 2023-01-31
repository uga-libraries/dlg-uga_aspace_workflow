import json
import requests
import urllib.parse
import asnake.logging as logging

from secrets import *
from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError


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
            self.client = ASnakeClient(baseurl=as_api, username=as_un, password=as_pw)
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

    def get_archobjs(self, tc_uri):
        """
        Gets the archival objects associated with a top container

        :param list tc_uri: list of the top container URI

        :return list ao_results: list of all archival objects associated with the top container
        """
        barcode = 32108050893687  # use these for unittests
        repository = 4  # use these for unittests
        ao_results = None
        search_aos = self.client.get_paged(f'repositories/{repository}/search', params={'q': f'{barcode}', 'type': ['archival_object']})
        print(type(search_aos), search_aos)
        # Above for testing purposes only, unless we have to use instead of filter_term query
        ao_results = [result for result in search_aos]
        print(len(ao_results))
        print(f'Length: {len(ao_results[0])}\n{ao_results[0]["id"]}\n\n')  # This seems to grab all 27 associated archival objects


        # for top_cont in tc_uri:
        #     print(tc_uri)  # /repositories/4/top_containers/45245
        #     encoded_uri = urllib.parse.quote(tc_uri, 'UTF-8')  # tried utf8
        #     print(encoded_uri)  # %2Frepositories%2F4%2Ftop_containers%2F45245
            # search_aos = self.client.get_paged(f'repositories/4/search',
            #                                    params={'filter_term[]': f'top_container_uri_u_sstr: {encoded_uri}',
            #                                            'type': ['archival_object']})
            # ao_results = [result for result in search_aos]
            # print(len(ao_results), ao_results[0])  # 322873 - it's grabbing all archival objects, filter_query returns 0
        return ao_results


# aspace_connection = ASpace(as_un, as_pw, as_api)
# aspace_connection.aspace_login()
# barcode = 32108050893687  # use these for unittests
# repository = 4  # use these for unittests
# tc_uri = aspace_connection.get_tcuri(barcode, repository)
# aspace_connection.get_archobjs(tc_uri)


class ArchivalObject:

    def __init__(self, archival_object):
        self.arch_obj = archival_object
        """str: Dictionary of archival object metadata"""
        self.title = ""
        """str: Title of the archival object"""
        self.creator = ""  # need to get this from get_resource_info()
        """str: Creator(s) of the collection, multiple separated by | |"""
        self.subject = ""  # need to get this from get_resource_info()
        """str: Subject terms for resource, multiple separated by | |"""
        self.description = ""
        """str: Description of the archival object, found in scope and content note"""
        self.date = ""
        """str: Date of the archival object, formatted YYYY-MM-DD, YYYY-MM, YYYY or YYYY/YYYY"""
        self.subject_spatial = ""  # need to get this from get_resource_info()
        """str: Subjects geographic/spatial of the resource, multiple separated by | |"""
        self.subject_medium = ""  # need to get this from get_resource_info()
        """str: Subjects medium/genre/format of the resource, multiple separated by | |"""
        self.extent = ""
        """str: Extent note of the archival object, if available"""
        self.language = ""  # need to get this from get_resource_info()
        """str: Language of material of the resource, usually eng"""
        self.citation = ""
        """str: Preferred citation of the resource"""
        self.subject_personal = ""  # need to get this from get_resource_info()
        """str: Subject person of the resource, multiple separated by | |"""

    def parse_archobj(self):

        self.title = ""  # TODO: could not have a title, search for title or date or both
        self.creator = ""  # need to get this from get_resource_info()
        self.subject = ""  # need to get this from get_resource_info()
        self.description = ""
        self.date = ""
        self.subject_spatial = ""  # need to get this from get_resource_info()
        self.subject_medium = ""  # need to get this from get_resource_info()
        self.extent = ""
        self.language = ""  # need to get this from get_resource_info()
        self.citation = ""
        self.subject_personal = ""  # need to get this from get_resource_info()

    def get_resource_info(self):
        pass
