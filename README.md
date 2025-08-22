# Key File Monitor

The Harris Key Loader R8B software does not display the currently selected encryption key distribution set on the loading page.
When dealing with multiple key sets, it is easy to mistakenly load the wrong key sets.
This application aims to address this issue by monitoring the currently selected key set file and displaying its name in another window.

## Developer Instructions

### Prerequisites

This software is intended to run only on Windows.

[Python](https://www.python.org/downloads/)
must be installed to run and build the program.
Make sure the Tkinter option is selected during setup.

Install the required packages:

`pip install -r requirements.txt`

### Testing

To run the application, execute the main script with python:

`python main.py`

### Release Build

Pyinstaller is used to create an executable that can be distributed easily.

`pyinstaller --onefile --windowed --icon=key_file_icon.ico -n keyfilemonitor main.py`

