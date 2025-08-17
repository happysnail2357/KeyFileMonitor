"""
Define the WindowWatcher class.

This class is responsible for monitoring the creation and destruction of
target windows. Also, it can monitor child components within a window. The
class runs its own message loop in a seperate thread to avoid hanging the main
message loop and window.
"""

import threading
import ctypes
import pythoncom
import win32gui
import win32con
import win32api
from types import FunctionType



class WindowWatcher:
    """Monitors window creation and destruction."""

    EVENT_OBJECT_CREATE = 0x8000
    EVENT_OBJECT_DESTROY = 0x8001
    EVENT_SYSTEM_DIALOGSTART = 0x8010
    EVENT_SYSTEM_DIALOGEND   = 0x8011
    WINEVENT_OUTOFCONTEXT = 0

    class WindowInfo:
        """Holds info about a window."""

        def __init__(
            self,
            title: str,
            hwnd: int,
            on_create: FunctionType,
            on_destroy: FunctionType
        ):
            """Contruct a WindowInfo."""

            self.title = title
            self.on_create = on_create
            self.on_destroy = on_destroy
            self.hwnd = hwnd


    def __init__(self, daemon=True):
        """
        Initialize a window watcher.

        Args:
            daemon (bool): Run the window watcher thread as a daemon
                          (default True).
        """

        self.daemon = daemon

        self._lock = threading.Lock()
        self._waiting_to_create = []
        self._waiting_to_destroy = []

        self._create_window_hook = None
        self._destroy_window_hook = None
        self._create_window_event_proc = None
        self._destroy_window_event_proc = None
        self._thread_id = None
        self._thread = None
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

        if self._thread and self._thread.is_alive():
            return

        self._thread = threading.Thread(
            target=self._thread_main,
            daemon=self.daemon
        )
        self._thread.start()

        print('Spy is starting')


    def stop(self):
        """Stop the window watcher thread."""

        if self._create_window_hook:
            ctypes.windll.user32.UnhookWinEvent(self._create_window_hook)
            self._create_window_hook = None

        if self._destroy_window_hook:
            ctypes.windll.user32.UnhookWinEvent(self._destroy_window_hook)
            self._destroy_window_hook = None

        if self._thread_id:
            win32api.PostThreadMessage(self._thread_id, win32con.WM_QUIT, 0, 0)
            self._thread_id = None

        print('Spy is stopping')


    def look_for_window(
        self,
        title: str,
        on_create: FunctionType,
        on_destroy: FunctionType
    ) -> int:
        """
        Add a window to the list of windows waiting to be created.

        Args:
            title (str): The title string of the target window.
            on_create (FunctionType): Function to call on window creation.
                                      Should accept a single integer as an
                                      argument, representing the window handle.
            on_destroy (FunctionType): Function to call on window destruction.

        Returns:
            int - handle to the window if present.
        """

        hwnd = win32gui.FindWindow(None, title)
        new_window_info = self.WindowInfo(title, hwnd, on_create, on_destroy)

        self._lock.acquire() # Enter critical section

        if hwnd == 0:
            self._waiting_to_create.append(new_window_info)

        else:
            self._waiting_to_destroy.append(new_window_info)


        self._lock.release() # Exit critical section

        return hwnd


    def _thread_main(self):
        """Entry point of the window watcher thread."""

        self._thread_id = win32api.GetCurrentThreadId()

        self._create_window_event_proc = self.WinEventProcType(
            self._handle_window_creation
        )
        self._destroy_window_event_proc = self.WinEventProcType(
            self._handle_window_destruction
        )

        self._create_window_hook = ctypes.windll.user32.SetWinEventHook(
            self.EVENT_OBJECT_CREATE,
            self.EVENT_OBJECT_CREATE,
            0,
            self._create_window_event_proc,
            0,
            0,
            self.WINEVENT_OUTOFCONTEXT
        )
        self._destroy_window_hook = ctypes.windll.user32.SetWinEventHook(
            self.EVENT_OBJECT_DESTROY,
            self.EVENT_OBJECT_DESTROY,
            0,
            self._destroy_window_event_proc,
            0,
            0,
            self.WINEVENT_OUTOFCONTEXT
        )

        self.running = True
        pythoncom.PumpMessages()
        self.running = False


    def _handle_window_creation(
        self,
        hWinEventHook,
        event,
        hwnd,
        idObject,
        idChild,
        dwEventThread,
        dwmsEventTime
    ):
        """Check to see if a target window is created."""

        if hwnd \
        and win32gui.IsWindow(hwnd) \
        and idObject == win32con.OBJID_WINDOW:
            title = win32gui.GetWindowText(hwnd)

            self._lock.acquire()

            for wininfo in self._waiting_to_create:
                if title == wininfo.title:
                    print('Window created:', title, hwnd)

                    self._waiting_to_create.remove(wininfo)

                    wininfo.hwnd = hwnd

                    self._waiting_to_destroy.append(wininfo)

                    self._lock.release()

                    if wininfo.on_create:
                        wininfo.on_create(hwnd)

                    return

            self._lock.release()


    def _handle_window_destruction(
        self,
        hWinEventHook,
        event,
        hwnd,
        idObject,
        idChild,
        dwEventThread,
        dwmsEventTime
    ):
        """Check to see if a target window is destroyed."""

        if hwnd \
        and win32gui.IsWindow(hwnd) \
        and idObject == win32con.OBJID_WINDOW:

            self._lock.acquire() # Entering critical section

            for wininfo in self._waiting_to_destroy:
                if hwnd == wininfo.hwnd:
                    print('Window destroyed:', wininfo.title, hwnd)

                    self._waiting_to_destroy.remove(wininfo)

                    self._lock.release() # Leaving critical section

                    if wininfo.on_destroy:
                        wininfo.on_destroy()

                    return

            self._lock.release() # Leaving critical section




