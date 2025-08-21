"""Banner.py - handles the application window."""

import tkinter as tk
import win32gui
from pathlib import Path
from datetime import datetime
from Config import KeyInfo


class KeyMonitorBanner:
    """
    Banner window class definition.

    Handles everything related to the application window.
    """

    def __init__(self, attach_to=0):
        """
        Contruct a window.

        Args:
            attach_to (int): handle to the window this window will "stick" to
                             (default None).
        """

        self.root = tk.Tk()
        self.root.title("Key File Monitor")

        # This will update size and position
        self._update_window_handle(attach_to)

        # UI variables
        self._key_filename = tk.StringVar(value='')
        self._timestamp = tk.StringVar(value='')

        # Colors
        self.background_color = '#F0F0F0'
        self.primary_color = '#00FF00'
        self.secondary_color = '#FF0000'

        # Build the UI
        self._build_UI()

        self._primary_key = ''



    def show(self):
        """
        Show and run the window.

        This method will not return until after the window is closed. Other
        tasks must be run in a background thread.

        Returns:
            None.
        """

        try:
            if self._attached_hwnd != 0:
                win32gui.SetForegroundWindow(self._attached_hwnd)

        except:
            pass

        self.root.mainloop()


    def close(self):
        """
        Close the window.

        Returns:
            None.
        """

        self.root.after(0, lambda: self.root.destroy())


    def attach_to_window(self, window_handle: int):
        """
        Set the window to which this window will "stick" to.

        Args:
            window_handle (int): The handle to the desired window.

        Returns:
            None.
        """

        self.root.after(0, lambda: self._update_window_handle(window_handle))


    def set_file_name(self, filename: str):
        """
        Display the given key filename.

        Args:
            filename (str): The name of the key file.

        Returns:
            None.
        """

        self.root.after(0, lambda: self._set_file_name(filename))


    def _set_file_name(self, filename):
        """Set the filename by calling this method in `root.after()`."""

        file = Path(filename)

        self._key_filename.set(file.name)
        self._timestamp.set(datetime.now().strftime('%I:%M %p'))

        color = self._key_info.get_key_color(file.stem)

        if file.stem.lower() == self.primary_key.lower():
            self.outer_frame.configure(background=self.primary_color)

        else:
            self.outer_frame.configure(background=self.secondary_color)


    def _calc_geometry(self, init=False) -> str:
        """
        Calculate the size and position based on the sibling window.

        Args:
            init (bool): Make adjustments to the window size to account for
                         window styling. Must be used the first time after
                         attaching to a window (default False).

        Returns:
            str.
        """

        window_rect = win32gui.GetWindowRect(self._attached_hwnd)

        left, top, right, bottom = window_rect
        width = right - left

        if init:
            client_rect = win32gui.GetClientRect(self._attached_hwnd)
            left_top = win32gui.ClientToScreen(self._attached_hwnd, (0, 0))
            right_bottom = win32gui.ClientToScreen(self._attached_hwnd, (client_rect[2], client_rect[3]))

            client_left, client_top = left_top
            client_right, client_bottom = right_bottom
            client_width = client_right - client_left

            self._width_diff = width - client_width
            self._top_diff = client_top - top

            self._init_geometry = False

        calc_width = width - self._width_diff
        calc_top = max(top - self._top_diff - 100, 0)

        return f'{calc_width}x{100}+{left}+{calc_top}'


    def _update_window_handle(self, hwnd: int):
        """
        Change the handle of the sibling window.

        Args:
            hwnd (int): The window handle

        Returns:
            None.
        """

        self._attached_hwnd = hwnd

        if hwnd != 0:
            geometry_str = self._calc_geometry(init=True)
            self.root.geometry(geometry_str)
            self.root.lift()

        else:
            self.root.geometry('500x100')


    def _build_UI(self):
        """Initialize the UI widgets for the window."""

        self.outer_frame = tk.Frame(self.root, background=self.background_color)
        self.outer_frame.pack(fill="both", expand=True)

        inner_frame = tk.Frame(self.outer_frame, background=self.background_color)
        inner_frame.pack(fill="both", expand=True, padx=15, pady=15)

        row = tk.Frame(inner_frame, background=self.background_color)
        row.pack(padx=(15, 15), fill='x', expand=True)

        label = tk.Label(row, text='Key File: ', font=("Arial", 14))
        file_label = tk.Label(
            row,
            textvariable=self._key_filename,
            font=("Arial", 18, "bold")
        )
        timestamp = tk.Label(row, textvariable=self._timestamp, font=("Arial", 14))

        label.pack(side='left')
        file_label.pack(side='left')
        timestamp.pack(side='right')

