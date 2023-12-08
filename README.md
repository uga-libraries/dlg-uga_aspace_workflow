# DLG to ArchivesSpace Spreadsheet Generator

## Overview

This application takes an input of barcodes from top containers in ArchivesSpace, retrieves all the archival objects
associated with those barcodes, parses the information and writes to a DLG approved spreadsheet template (also provided
by the user in the application). This process is intended to make it easier for users to contribute metadata to DLG's 
online portal of digitally accessible historic images and cultural material by automatically pulling the data from
ArchivesSpace and into a spreadsheet that the user can send to the DLG, along with any other files.

## Getting Started

### Dependencies
- [PySimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI) - The GUI used
- [ArchivesSnake](https://github.com/archivesspace-labs/ArchivesSnake) - Library used for interacting with the ArchivesSpace API
- [loguru](https://pypi.org/project/loguru/) - Logging package
- [cx_Freeze](https://cx-freeze.readthedocs.io/en/latest/) - Generated the executable file
- [Inno](https://jrsoftware.org/isinfo.php) - Generated Windows installer

### Installation
1. Install Python 3 on your computer. You can install python using the following link:
https://www.python.org/downloads/
2. Download the repository via cloning to your local IDE or using GitHub's Code button and Download as ZIP
3. Set up a virtual environment and run `pip install requirements.txt` 
4. Make sure you have your ArchivesSpace Instance's API URL (plus port # ending, example: "https://localhost:8089, 
username, and password
5. Run the script `python3 gui.py`

#### For Windows Users
1. Go to [Releases](https://github.com/uga-libraries/dlg-uga_aspace_workflow/releases) and download the .exe file from 
the latest release.
2. Follow the on-screen instructions.
3. After installing, double-click the ASpace_DLG_Workflow icon to run the application.

#### For Mac Users
1. Install Python 3 on your computer. You can install python using the following link:
https://www.python.org/downloads/mac-osx/
2. Download the GitHub repo using the Code button in the top right corner of the repo, choose "Download ZIP", then unzip
the downloaded file.
3. Open your terminal and go to the unzipped folder. Run the command: `pip3 install -r requirements.txt`.
4. After installing requirements, run the command: `python3 gui.py`. This will start the program.

### Script Arguments
If you are running the app using python, run `python3 gui.py` from the repository directory.

### Testing
I'm still building unittests and the data for the tests is locally dependent. If you want to use the unittests, 
create a "test_data" directory and create "resource.json" and "archival_object.json" files using a JSON formatted 
resource and archival object from the ArchivesSpace API. Additionally, you'll need to swap the barcodes, repository 
numbers, and resource/archival object dependent tests to reflect the data you have. Yes, I need to fix this to be
universally acceptable.

## Workflow
1. Once the GUI is launched, login to your local ArchivesSpace instance with your ArchivesSpace credentials, including
your username, password, and API URL
2. Enter the barcodes or top container URIs in the left column, separated by newline (enter) of the archival objects
you want retrieved and parsed
3. Select your repository (click SAVE to remember this selection)
4. Select the ASpace>DLG Template file that will be used to copy to make the new spreadsheet. This will be saved.
5. Select START
6. The GUI may go unresponsive if there are a lot of archival objects. Let it run until the START button is active.
7. Select Open Output Folder to find the new spreadsheet

## Contributing
See the [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

## Versioning
Trying our best to adhere to [SemVer](https://semver.org/).

## License Information

This program is licensed under a Creative Commons Attribution Share Alike 4.0 International. Please see 
[LICENSE.txt](LICENSE.txt) for more information.

## Authors
- Corey Schmidt - Project Management Librarian/Archivist at the University of Georgia Libraries

## Acknowledgements
- Kevin Cottrell - GALILEO/Library Infrastructure Systems Architect at the University of Georgia Libraries
- Kat Stein - Director of the Hargrett Rare Book and Manuscript Library
- ArchivesSpace community
