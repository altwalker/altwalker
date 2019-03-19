import platform
import signal
import os

import psutil


def kill(pid):
    """Send the SIGINT signal to a process and all its children."""

    process = psutil.Process(pid)

    for child in process.children(recursive=True):
        os.kill(child.pid, signal.SIGINT)

    os.kill(process.pid, signal.SIGINT)


def get_command(command_name):
    command = ["cmd.exe", "/C"] if platform.system() == "Windows" else []
    command.append(command_name)

    return command
