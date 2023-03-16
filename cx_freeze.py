import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {"packages": ["os"], "excludes": [], "includes": ["asnake", "cx_Freeze", "loguru", "openpyxl",
                                                                      "PySimpleGUI", "requests"]}

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="ASpace_DLG_Workflow",
    version="1.0",
    description="ArchivesSpace to DLG template workflow",
    options={"build_exe": build_exe_options},
    executables=[Executable("gui.py", base=base, targetName="ASpace_DLG_workflow_vRELEASEVERSIONNUMBERNODOTS.exe")])
