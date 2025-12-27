import tkinter as tk
from tkinter import messagebox
import sys
import winsound  # For Windows sound


def show_notification_window(title: str, message: str):
    """
    Show a popup notification window using tkinter

    Args:
        title (str): Title of the notification
        message (str): Content of the notification
    """
    # Create a root window for the messagebox
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # try:
    #     # On Windows, play the system default notification sound
    #     winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
    # except:
    #     # Fallback for non-Windows systems
    #     root.bell()  # Play the default system bell# Play system notification sound
    

    # Make sure the messagebox is on top
    root.attributes("-topmost", True)

    # Show the messagebox
    messagebox.showinfo(title, message, parent=root)

    # Destroy the root window after showing the message
    root.destroy()


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        title = sys.argv[1]
        message = sys.argv[2]
        show_notification_window(title, message)
    else:
        show_notification_window("Уведомление", "Таймер завершен!")