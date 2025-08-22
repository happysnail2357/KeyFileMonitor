"""
Define the WindowWatcher class.

This class is responsible for monitoring the creation and destruction of
target windows. Also, it can monitor child components within a window. The
class runs its own message loop in a seperate thread to avoid hanging the main
message loop and window.
"""

import threading
import ctypes
import ctypes.wintypes
import pythoncom
import win32gui
import win32con
import win32api
from types import FunctionType
from time import sleep



class WindowWatcher:
    """Monitors window creation and destruction."""

    EVENT_OBJECT_CREATE = 0x8000
    EVENT_OBJECT_DESTROY = 0x8001
    EVENT_OBJECT_VALUECHANGE = 0x800E
    WINEVENT_OUTOFCONTEXT = 0


    class WindowInfo:
        """Holds info about a window."""

        def __init__(
            self,
            title: str,
            hwnd: int,
            on_create: FunctionType,
            on_destroy: FunctionType,
            on_edit=None
        ):
            """Contruct a WindowInfo."""

            self.title = title
            self.on_create = on_create
            self.on_destroy = on_destroy
            self.on_edit = on_edit
            self.hwnd = hwnd


    def __init__(self, daemon=True):
        """
        Initialize a window watcher.

        Args:
            daemon (bool): Run the window watcher thread as a daemon
                          (default True).
        """

        self.daemon = daemon

        self._window = None
        self._dialog = None
        self._edit_control = None

        self._window_thread = None
        self._dialog_thread = None
        self._window_thread_id = None
        self._dialog_thread_id = None

        self._window_event_proc = None
        self._window_event_hook = None
        self._dialog_event_hook = None

        self.running = False


        # Define the callback type used by the SetWinEventHook API
        self.WinEventProcType = ctypes.WINFUNCTYPE(
            None,
            ctypes.wintypes.HANDLE,
            ctypes.wintypes.DWORD,
            ctypes.wintypes.HWND,
            ctypes.wintypes.LONG,
            ctypes.wintypes.LONG,
            ctypes.wintypes.DWORD,
            ctypes.wintypes.DWORD
        )


    def start(self):
        """Start the window watcher thread."""

        self.running = True

        if not self._window_thread or not self._window_thread.is_alive():

            self._window_thread = threading.Thread(
                target=self._window_thread_main,
                daemon=self.daemon
            )
            self._window_thread.start()

        self._start_dialog_thread()

        print('Spy is starting')


    def stop(self):
        """Stop the window watcher thread."""

        self.running = False

        if self._window_event_hook:
            ctypes.windll.user32.UnhookWinEvent(self._window_event_hook)
            self._window_event_hook = None

        if self._dialog_event_hook:
            ctypes.windll.user32.UnhookWinEvent(self._dialog_event_hook)
            self._dialog_event_hook = None

        if self._window_thread_id and self._window_thread.is_alive():
            win32api.PostThreadMessage(
                self._window_thread_id, win32con.WM_QUIT, 0, 0
            )
            self._window_thread_id = None

        if self._dialog_thread_id and self._dialog_thread.is_alive():
            win32api.PostThreadMessage(
                self._dialog_thread_id, win32con.WM_QUIT, 0, 0
            )
            self._dialog_thread_id = None

        print('Spy is stopping')


    def target_window(
        self,
        title: str,
        on_create: FunctionType,
        on_destroy: FunctionType
    ) -> int:
        """
        Register a window for create and destroy events.

        Args:
            title (str): The title string of the target window.
            on_create (FunctionType): Function to call on window creation.
                                      Should accept a single integer as an
                                      argument, representing the window handle.
            on_destroy (FunctionType): Function to call on window destruction.

        Returns:
            int - handle to the window if present.
        """

        if self.running:
            raise Exception('Cannot register window while WindowWatcher is running')

        hwnd = win32gui.FindWindow(None, title)
        self._window = self.WindowInfo(title, hwnd, on_create, on_destroy)
        return hwnd


    def target_dialog(
        self,
        title: str,
        on_create: FunctionType,
        on_destroy: FunctionType,
        on_edit: FunctionType
    ) -> int:
        """
        Register a dialog window for create and destroy events.

        Args:
            title (str): The title string of the target dialog.
            on_create (FunctionType): Function to call on dialog creation.
                                      Should accept a single integer as an
                                      argument, representing the window handle.
            on_destroy (FunctionType): Function to call on dialog destruction.
            on_edit (FunctionType): Function to call on dialog edit field
                                    change.

        Returns:
            int - handle to the window if present.
        """

        if self.running:
            raise Exception('Cannot register dialog while WindowWatcher is running')

        hwnd = win32gui.FindWindow(None, title)
        self._dialog = self.WindowInfo(
            title, hwnd, on_create, on_destroy, on_edit
        )
        return hwnd


    def _window_thread_main(self):
        """Entry point of the window watcher thread."""

        self._window_thread_id = win32api.GetCurrentThreadId()

        self._window_event_proc = self.WinEventProcType(
            self._handle_event
        )

        self._window_event_hook = ctypes.windll.user32.SetWinEventHook(
            self.EVENT_OBJECT_CREATE,
            self.EVENT_OBJECT_DESTROY,
            0,
            self._window_event_proc,
            0,
            0,
            self.WINEVENT_OUTOFCONTEXT
        )

        self._dialog_event_hook = ctypes.windll.user32.SetWinEventHook(
            self.EVENT_OBJECT_VALUECHANGE,
            self.EVENT_OBJECT_VALUECHANGE,
            0,
            self._window_event_proc,
            0,
            0,
            self.WINEVENT_OUTOFCONTEXT
        )

        pythoncom.PumpMessages()


    def _dialog_thread_main(self):
        """Entry point of the dialog watcher thread."""

        self._dialog_thread_id = win32api.GetCurrentThreadId()
        print('Poll dialog - Start')
        while self.running:

            hwnd = win32gui.FindWindow('#32770', self._dialog.title)

            if hwnd != 0:
                print('Dialog created:', self._dialog.title, hwnd)

                self._dialog.hwnd = hwnd

                if self._dialog.on_create:
                    self._dialog.on_create(hwnd)

                combo_box_hwnd = win32gui.FindWindowEx(hwnd, None, 'ComboBoxEx32', None)
                combo_box_hwnd = win32gui.FindWindowEx(combo_box_hwnd, None, 'ComboBox', None)
                self._edit_control = win32gui.FindWindowEx(combo_box_hwnd, None, 'Edit', None)

                break

            sleep(0.1)

        print('Poll dialog - Stop')


    def _start_dialog_thread(self):
        """Like it says."""

        if not self._dialog_thread or not self._dialog_thread.is_alive():
            if self._window.hwnd != 0:
                self._dialog_thread = threading.Thread(
                    target=self._dialog_thread_main,
                    daemon=self.daemon
                )
                self._dialog_thread.start()


    def _handle_event(
        self,
        hWinEventHook,
        event,
        hwnd,
        idObject,
        idChild,
        dwEventThread,
        dwmsEventTime
    ):
        """Handle window create and destroy events."""

        if hwnd:
            if win32gui.IsWindow(hwnd) and idObject == win32con.OBJID_WINDOW:
                if event == self.EVENT_OBJECT_CREATE:
                    self._handle_window_creation(hwnd)

                elif event == self.EVENT_OBJECT_DESTROY:
                    self._handle_window_destruction(hwnd)

            elif event == self.EVENT_OBJECT_VALUECHANGE:
                self._handle_value_changed(hwnd)


    def _handle_window_creation(self, hwnd):
        """Check to see if a target window is created."""

        if self._window.hwnd != 0:
            return

        title = win32gui.GetWindowText(hwnd)

        if title == self._window.title:
            print('Window created:', title, hwnd)

            self._window.hwnd = hwnd

            if self._window.on_create:
                self._window.on_create(hwnd)

            self._start_dialog_thread()


    def _handle_window_destruction(self, hwnd):
        """Check to see if a target window is destroyed."""

        if self._dialog.hwnd == hwnd:
            print('Dialog destroyed:', self._dialog.title, hwnd)

            if self._dialog.on_destroy:
                self._dialog.on_destroy()

            self._edit_control = None
            self._dialog.hwnd = 0

            while win32gui.FindWindow('#32770', self._dialog.title):
                sleep(0.01)

            self._start_dialog_thread()

            return

        if self._window.hwnd != hwnd:
            return

        print('Window destroyed:', self._window.title, hwnd)

        self._window.hwnd = 0

        if self._window.on_destroy:
            self._window.on_destroy()


    def _handle_value_changed(self, hwnd):
        """Check if the edit control text has been modified."""

        if self._edit_control and hwnd == self._edit_control:
            buffer = ctypes.create_unicode_buffer(512)
            win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, 512, buffer)

            if self._dialog.on_edit:
                self._dialog.on_edit(buffer.value)
