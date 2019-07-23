import platform
import subprocess
import signal
import os

import psutil
import click


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


def url_join(base, url):
    """Join a base with an url."""

    return "{}/{}".format(base.strip("/"), url.strip("/"))


def has_git():
    """Returns True if it can run ``git --version``, otherwise returns False."""

    try:
        process = subprocess.Popen(["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        response = process.communicate()

        return response[1] == b""
    except FileNotFoundError:
        return False


def click_formatwarning(message, category, filename, lineno, file=None, line=None):
    """Format a warning on a single line and style the text."""

    return click.style("{}: {}\n".format(category.__name__, message), fg="yellow")
