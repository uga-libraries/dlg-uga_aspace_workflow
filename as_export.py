import json
import asnake.logging as logging

from secrets import *
from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError

# 1st step - user login to ASpace with creds

client = ASnakeClient(baseurl=as_api, username=as_un, password=as_pw)
# logging.setup_logging(level='DEBUG')
try:
    client.authorize()
except ASnakeAuthError as e:
    error_message = ''
    if ':' in str(e):
        error_divided = str(e).split(":")
        for line in error_divided:
            error_message += line + "\n"
    print(error_message)

# 2nd step - user inputs a spreadsheet of top containers with barcodes or top_container ASpace URI



# 3rd step - code takes spreadsheet, searches for top containers on ASpace

barcode = 32108050893687
repository = 4
search_tcs = json.loads(client.get(f'repositories/{repository}/top_containers/search',
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
for tc_uri in results:
    print(tc_uri)
    search_aos = client.get_paged(f'repositories/4/search', params={'q': f'{barcode}', 'type': ['archival_object']})
    ao_results = [result for result in search_aos]
    print(len(ao_results))  # This seems to grab all 27 associated archival objects
