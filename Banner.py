"""Banner.py - handles the application window."""

import tkinter as tk
from tkinter import filedialog
import win32gui
import win32con
from pathlib import Path
from datetime import datetime
import appdirs


class KeyMonitorBanner:
    """
    Banner window class definition.

    Handles everything related to the application window.
    """

    def __init__(self, attach_to=0):
        """
        Contruct a window.

        Args:
            attach_to (int): A handle to the "sibling" window (the key loader window)
                             (default 0).
        """

        self.root = tk.Tk()
        self.root.title("Key File Monitor")
        self.root.geometry('500x125')

        # This will update size and position
        self._update_window_handle(attach_to)

        # UI variables
        self._key_filename = tk.StringVar(value='')
        self._timestamp = tk.StringVar(value='--:-- --')

        # Colors
        self.background_color = '#F0F0F0'
        self.primary_color = '#00FF00'
        self.secondary_color = '#FF0000'

        # Build the UI
        self._build_UI()

        # Load settings
        self._primary_key = Path('')
        self._load_primary_key()


    def show(self):
        """
        Show and run the window.

        This method will not return until after the window is closed. Other
        tasks must be run in a background thread.
        """

        try:
            if self._sibling_hwnd != 0:
                win32gui.SetForegroundWindow(self._sibling_hwnd)

        except:
            pass

        self.root.mainloop()


    def close(self):
        """Close the window."""

        self.root.after(0, lambda: self.root.destroy())


    def attach_to_window(self, window_handle: int):
        """
        Set the "sibling" window.

        Args:
            window_handle (int): The handle to the desired window.
        """

        self.root.after(0, lambda: self._update_window_handle(window_handle))


    def set_filename(self, filename: str):
        """
        Display the key filename provided by the user.

        Args:
            filename (str): The name of the key file.
        """

        self.root.after(0, lambda: self._set_filename(filename))


    def _set_filename(self, filename):
        """
        Display the key filename provided by the user (Private).

        Args:
            filename (str): The name of the key file.
        """

        file = Path(filename)

        self._key_filename.set(file.name)
        self._timestamp.set(datetime.now().strftime('%I:%M %p'))

        self._set_border_color(file)


    def _set_border_color(self, file):
        """
        Set the border color based on the filename.

        Args:
            file (str, Path): The name of the key file.
        """

        if isinstance(file, str):
            file = Path(file)

        if not file.stem or not self._primary_key.stem:
            self.outer_frame.configure(background=self.background_color)

        elif file.stem.lower() == self._primary_key.stem.lower():
            self.outer_frame.configure(background=self.primary_color)

        else:
            self.outer_frame.configure(background=self.secondary_color)


    def _move_to_sibling(self):
        """Set the window position above the sibling window."""

        left, top, right, bottom = win32gui.GetWindowRect(self._sibling_hwnd)

        if left   < 0 \
        or top    < 0 \
        or right  < 0 \
        or bottom < 0:
            return

        height = 160
        new_top = max(top - height, 0)

        self.root.update_idletasks()
        hwnd = win32gui.FindWindow(None, 'Key File Monitor')

        if hwnd != 0:
            win32gui.SetWindowPos(
                hwnd, win32con.HWND_TOP, left, new_top, right - left, height,
                win32con.SWP_SHOWWINDOW
            )


    def _update_window_handle(self, hwnd: int):
        """
        Change the handle of the sibling window.

        Args:
            hwnd (int): The window handle
        """

        self._sibling_hwnd = hwnd

        if hwnd != 0:
            self._move_to_sibling()
            self.root.lift()


    def _build_UI(self):
        """Initialize the UI widgets for the window."""

        # This appears as the colored border
        self.outer_frame = tk.Frame(self.root, background=self.background_color)
        self.outer_frame.pack(fill="both", expand=True)

        # Everything else is inside this inner frame
        inner_frame = tk.Frame(self.outer_frame, background=self.background_color)
        inner_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # This holds everything in the center
        center = tk.Frame(inner_frame, background=self.background_color)
        center.pack(padx=(15, 15), fill='x', expand=True)

        # This is the container for the filename and timestamp labels
        fileinfo = tk.Frame(center, background=self.background_color)
        fileinfo.pack(fill='x', expand=True, side='left')

        # The settings button
        settings_button = tk.Button(
            center,
            text='Settings...',
            font=("Arial", 12),
            command=self._handle_open_settings
        )
        settings_button.pack(side='right')

        # These hold the labels side by side in their own rows
        file_row = tk.Frame(fileinfo, background=self.background_color)
        time_row = tk.Frame(fileinfo, background=self.background_color)
        file_row.pack(fill='x', expand=True)
        time_row.pack(fill='x', expand=True)

        # Filename labels
        label = tk.Label(file_row, text='Key File: ', font=("Arial", 14))
        file_label = tk.Label(
            file_row,
            textvariable=self._key_filename,
            font=("Arial", 18, "bold")
        )
        label.pack(side='left')
        file_label.pack(side='left')

        # Time labels
        label2 = tk.Label(time_row, text='Time:      ', font=("Arial", 14))
        timestamp = tk.Label(
            time_row,
            textvariable=self._timestamp,
            font=("Arial", 14)
        )
        label2.pack(side='left')
        timestamp.pack(side='left')


    def _handle_open_settings(self):
        """Handle the settings dialog when the settings button is clicked."""

        dlg = SettingsDialog(self.root, default=self._primary_key.name)

        if dlg.primary_key_value:
            self._primary_key = dlg.primary_key_value
            self._save_primary_key()
            self._set_border_color(self._key_filename.get())


    def _save_primary_key(self):
        """Save the primary key value to an AppData file."""

        path = Path(appdirs.user_data_dir('KeyFileMonitor')) / "primary.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._primary_key.name, encoding="utf-8")


    def _load_primary_key(self):
        """Load the primary key value from an AppData file."""

        path = Path(appdirs.user_data_dir('KeyFileMonitor')) / "primary.txt"

        if path.exists():
            value = path.read_text(encoding="utf-8")
            self._primary_key = Path(value)



class SettingsDialog:
    """
    A Tkinter dialog class for the Key File Monitor settings.

    Fields:
        primary_key_value (Path): The file to be used as the primary key.
    """

    def __init__(self, parent, title='Settings', default=''):
        """
        Build and run the dialog.

        Calling this constructor blocks until the dialog is closed.

        Args:
            parent (tkinter.Tk): The parent window for this dialog.
            title (str): The dialog title string (default 'Settings').
            default (str): The starting value for the primary key edit field
                           (default '').
        """

        # Return fields
        self.primary_key_value = None

        # Define the window
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry(f'400x150+{parent.winfo_x()}+{parent.winfo_y()}')
        self.top.resizable(width=True, height=False)

        # Make modal
        self.top.transient(parent)
        self.top.grab_set()

        # Build UI
        self._build_ui(default)

        # Make the main window wait for us
        parent.wait_window(self.top)


    def _build_ui(self, default):
        """Define the UI for this settings dialog."""

        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(0, weight=1)

        label = tk.Label(self.top, text="Primary Key", font=("Arial", 12, "bold"))
        label.grid(row=0, column=0, sticky="w", padx=20, pady=(30, 0))

        self._entry = tk.Entry(self.top, font=("Arial", 12))
        self._entry.insert(0, default)
        self._entry.grid(row=1, column=0, sticky="ew", padx=(20, 10))
        self._entry.bind("<Return>", lambda event: self.on_ok())
        self._entry.focus_set()

        Tooltip(label, "A green border will be displayed when this key file is selected.")
        Tooltip(self._entry, "A green border will be displayed when this key file is selected.")

        browse_button = tk.Button(self.top, text="Browse...", width=10, command=self._browse_file)
        browse_button.grid(row=1, column=1, padx=(0, 20))

        button_frame = tk.Frame(self.top)
        button_frame.grid(row=2, column=0, columnspan=2, sticky="e", padx=20, pady=(30, 15))

        tk.Button(button_frame, text="OK", width=10, command=self._on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", width=10, command=self._on_cancel).pack(side=tk.LEFT, padx=(5, 0))


    def _browse_file(self):
        """Trigger the Windows "Open" dialog."""

        filename = filedialog.askopenfilename(
            parent=self.top,
            title="Choose a primary key file"
        )

        if filename:
            file = Path(filename)
            self._entry.delete(0, tk.END)
            self._entry.insert(0, file.name)
            self._entry.focus_set()


    def _on_ok(self):
        """Exit the dialog and save changes."""

        self.primary_key_value = Path(self._entry.get())
        self.top.destroy()


    def _on_cancel(self):
        """Exit the dialog and don't save changes."""

        self.top.destroy()



class Tooltip:
    """A tooltip widget definition."""

    def __init__(self, parent, text, delay=500):
        """
        Initialize a Tooltip.

        Args:
            parent (tkinter.*): The parent widget that will trigger
                                the tooltip when hovered above.
            delay (int): The delay in milliseconds before the tooltip
                         will appear (default 500).
        """

        self.widget = parent
        self.text = text
        self.delay = delay
        self.tipwindow = None
        self.id = None

        parent.bind("<Enter>", self.schedule)
        parent.bind("<Leave>", self.unschedule)
        parent.bind("<ButtonPress>", self.unschedule)


    def schedule(self, event=None):
        """Schedule the tooltip to appear."""

        self.unschedule()
        self.id = self.widget.after(self.delay, self.show)


    def unschedule(self, event=None):
        """Cancel a scheduled tooltip appearance."""

        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

        self.hide()


    def show(self):
        """Show the tooltip."""

        if self.tipwindow or not self.text:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tipwindow = tw = tk.Toplevel(self.widget)

        # No border or titlebar
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text,
            background="lightyellow",
            relief="solid",
            borderwidth=1,
            font=("Arial", 9)
        )
        label.pack(ipadx=5, ipady=2)


    def hide(self):
        """Hide the tooltip."""

        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

