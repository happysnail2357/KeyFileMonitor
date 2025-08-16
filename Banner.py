"""Banner.py - handles the application window."""

import tkinter as tk
import win32gui


class KeyMonitorBanner:
    """
    Banner window class definition.

    Handles everything related to the application window.
    """

    def __init__(self, attach_to=0):
        """
        Contruct a window.

        Arguments:
        attach_to <int>: handle to the window this window will "stick" to
                         (default None).
        """

        self.__attached_hwnd = attach_to
        self.__root = tk.Tk()

        self.__root.title("Key File Monitor")

        # Size and position
        self.__init_geometry = True
        geometry_str = self.__calc_geometry()
        self.__root.geometry(geometry_str)
        self.__root.resizable(False, True)

        # UI variables
        self.__key_file = tk.StringVar(value="Keyfile.bin")

        # Build the UI
        self.__build_UI()



    def show(self):
        """
        Show and run the window.

        Note: Calling this method will block for the duration of window.
        """

        self.__root.mainloop()


    def __calc_geometry(self) -> str:
        """
        Calculate the size and position based on the "parent" window.

        Returns: <str>
        """

        if self.__attached_hwnd != 0:

            window_rect = win32gui.GetWindowRect(self.__attached_hwnd)

            left, top, right, bottom = window_rect
            width = right - left

            if self.__init_geometry:
                client_rect = win32gui.GetClientRect(self.__attached_hwnd)
                left_top = win32gui.ClientToScreen(self.__attached_hwnd, (0, 0))
                right_bottom = win32gui.ClientToScreen(self.__attached_hwnd, (client_rect[2], client_rect[3]))

                client_left, client_top = left_top
                client_right, client_bottom = right_bottom
                client_width = client_right - client_left

                self.__width_diff = width - client_width
                self.__top_diff = client_top - top

            calc_width = width - self.__width_diff
            calc_top = max(top - self.__top_diff - 100, 0)

            return f'{calc_width}x{100}+{left}+{calc_top}'

        else:
            return '500x100'


    def __build_UI(self):
        """Initialize the UI widgets for the window."""

        row = tk.Frame(self.__root)
        row.pack(padx=(30, 0), fill='x', expand=True)

        label = tk.Label(row, text='Key File: ', font=("Arial", 12))
        file_label = tk.Label(
            row,
            textvariable=self.__key_file,
            font=("Arial", 14, "bold")
        )

        label.pack(side='left')
        file_label.pack(side='left')


