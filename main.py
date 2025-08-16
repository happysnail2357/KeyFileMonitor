"""
Key File Banner for Harris Key Loader R8B.

Created  8/16/2025 - Paul Puhnaty
"""

import win32gui

from Banner import KeyMonitorBanner


def main():
    """Entry point of the application."""

    # Find key loader window
    key_loader_hwnd = win32gui.FindWindow(None, "Key Loader R8B")

    # Create UI
    banner = KeyMonitorBanner(key_loader_hwnd)

    banner.show()

    # Obtain key file name




if __name__ == "__main__":
    main()
