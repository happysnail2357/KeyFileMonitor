"""
Demo Program.

A stand-in for the Harris Key Loader R8B software.

Created  8/16/2025 - Paul Puhnaty
"""

import tkinter as tk
from tkinter import filedialog


def main():
    """Entry point of the application."""

    window = build_window()
    window.mainloop()


def build_window():
    """Contruct the window and UI."""

    root = tk.Tk()
    root.title("Key Loader R8B")

    width = 500
    height = 200
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)

    root.geometry(f"{width}x{height}+{x}+{y}")

    row = tk.Frame(root)
    row.pack(padx=10, pady=10, fill="x", expand=True)

    label_var = tk.StringVar(value="No file selected")

    open_button = tk.Button(
        row,
        text="Browse",
        command=lambda: open_file(label_var)
    )
    open_button.pack(side="right")

    file_label = tk.Label(
        row,
        textvariable=label_var,
        bg="#d0d0d0",
        wraplength=400,
        justify="left",
        anchor="w"
    )
    file_label.pack(side="left", fill="x", expand=True, padx=(0, 10))

    return root

def open_file(label_var):
    """Button callback to retrieve a file name from the user."""

    filename = filedialog.askopenfilename(
        title="Open a Distribituion Key File...",
        filetypes=[("All files", "*.*")]
    )

    if filename:
        label_var.set(filename)


if __name__ == "__main__":
    main()
