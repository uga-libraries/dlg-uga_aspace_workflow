from secrets import *
from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError

# aspace = ASpace(baseurl=as_api, username=as_un, password=as_pw)
client = ASnakeClient(baseurl=as_api, username=as_un, password=as_pw)
client.authorize()

# 1st step - user login to ASpace with creds

# 2nd step - user inputs a spreadsheet of top containers with barcodes or top_container ASpace URI
# search_tcs = client.get("repositories/4/top_containers/search", params={"q": f"barcode_u_sstr:{32108050893687}"})
# print(search_tcs.text)


# 3rd step - code takes spreadsheet, searches for top containers on ASpace

# 4th step - get archival objects associated with top containers - use collection ref (URI) to narrow searching for archival objects within collection
# use https://archivesspace.github.io/archivesspace/api/?shell#fetch-tree-information-for-the-top-level-resource-record - go through each archival object?


barcode = "32108050893687"
get_tc = client.get("/repositories/4/top_containers/45245")
print(get_tc.text)
