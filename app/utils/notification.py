import subprocess
import sys
import os


def show_notification(title: str, message: str):
    """
    Show a popup notification using tkinter in a separate process
    This ensures the notification window stays open even if the main program exits

    Args:
        title (str): Title of the notification
        message (str): Content of the notification
    """
    # Get the path to the notification window script
    notification_script = os.path.join(os.path.dirname(__file__), 'notification_window.py')

    # Create a separate process to show the notification
    # This ensures the notification window stays open even if the main program exits
    subprocess.Popen([
        sys.executable,
        notification_script,
        title,
        message
    ])