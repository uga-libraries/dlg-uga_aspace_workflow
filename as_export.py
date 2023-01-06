import json
import asnake.logging as logging

from secrets import *
from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError


class ASpace:

    def __init__(self, username, password, api):
        self.username = username
        """str: ArchivesSpace username provided by user"""
        self.password = password
        """str: ArchivesSpace password provided by user"""
        self.api = api
        """str: ArchivesSpace API URL provided by user"""
        self.client = None
        """str: ArchivesSnake client as created through ASnakeClient"""

    # 1st step - user login to ASpace with creds

    def aspace_login(self):

        # logging.setup_logging(level='DEBUG')
        try:
            self.client = ASnakeClient(baseurl=as_api, username=as_un, password=as_pw)
            self.client.authorize()
            status = 200
        except ASnakeAuthError as e:
            print(e)
            error_message = ''
            if ':' in str(e):
                error_divided = str(e).split(":")
                status = int(error_divided[1])
                for line in error_divided:
                    error_message += line + "\n"
            print(error_message)
        return status

    # 2nd step - user inputs a spreadsheet of top containers with barcodes or top_container ASpace URI

    # 3rd step - code takes spreadsheet, searches for top containers on ASpace

    def get_tcuri(self):
        barcode = 32108050893687
        repository = 4
        search_tcs = json.loads(self.client.get(f'repositories/{repository}/top_containers/search',
                                                params={'q': f'barcode_u_sstr:{barcode}',
                                                        'type[]': '["top_container"]'}).text)
        tc_json = json.loads(search_tcs['response']['docs'][0]['json'])
        print(tc_json['collection'])
        results = [result['uri'] for result in search_tcs['response']['docs']]
        if len(results) > 1:
            print('Multiple results found with same barcode')
            print(results)
        elif len(results) == 0:
            print(f'No results found for {barcode}')
        else:
            print(results)

    # 4th step - get archival objects associated with top containers - use collection ref (URI) to narrow searching for archival objects within collection
    # use https://archivesspace.github.io/archivesspace/api/?shell#fetch-tree-information-for-the-top-level-resource-record - go through each archival object?

    def get_archobjs(self, barcode, repository):
        barcode = 32108050893687  # use these for unittests
        repository = 4  # use these for unittests
        search_aos = self.client.get_paged(f'repositories/{repository}/search', params={'q': f'{barcode}', 'type': ['archival_object']})
        ao_results = [result for result in search_aos]
        print(len(ao_results), ao_results)  # This seems to grab all 27 associated archival objects
