"""
Key File Monitor

Displays the key filename selected in the Harris Key Loader R8B application.

Created  8/16/2025 - Paul Puhnaty
"""


from Banner import KeyMonitorBanner
from Spy import WindowWatcher


def main():
    """Entry point of the application."""

    app = App()
    app.startup()



class App:
    """Everything is handled from this class."""

    KEY_LOADER_TITLE = 'Key Loader R8B'
    OPEN_KEY_FILE_DIALOG_TITLE = 'Open a Distribituion Key File...'

    def __init__(self):
        """Configure the components of the application."""

        self.spy = WindowWatcher()

        key_loader_hwnd = self.spy.target_window(
            self.KEY_LOADER_TITLE,
            self.on_keyloader_startup,
            self.on_keyloader_shutdown
        )

        self.buffered_filename = "This is the selected key filename"

        self.spy.target_dialog(
            self.OPEN_KEY_FILE_DIALOG_TITLE,
            self.on_select_file_startup,
            self.on_select_file_shutdown,
            self.on_select_file_edit
        )

        self.window = KeyMonitorBanner(key_loader_hwnd)


    def startup(self):
        """Start the application."""

        self.spy.start()
        self.window.show()
        self.spy.stop()


    def on_keyloader_startup(self, hwnd):
        """Connect to the keyloader when it is started."""

        self.window.attach_to_window(hwnd)


    def on_keyloader_shutdown(self):
        """Close this app along with the sibling app."""

        self.window.close()


    def on_select_file_startup(self, hwnd):
        """Do nothing when the "Open" dialog appears."""

        pass


    def on_select_file_edit(self, filename):
        """Edit the buffered filename when the filename changes in the "Open" dialog."""

        self.buffered_filename = filename


    def on_select_file_shutdown(self):
        """Apply the buffered filename when the "Open" dialog closes."""

        self.window.set_filename(self.buffered_filename)



if __name__ == "__main__":
    main()
