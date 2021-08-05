"""Utility functions and classes used by AltWalker internally."""

import platform
import subprocess

import psutil


def url_join(base, url):
    """Join a base with an url."""

    return "{}/{}".format(base.strip("/"), url.strip("/"))


def prefix_command(command):
    """Prefix a command list with ``["cmd.exe", "/C"]`` on Windows, on Linux and POSIX return the command."""

    prefix = ["cmd.exe", "/C"] if platform.system() == "Windows" else []
    prefix.extend(command)

    return prefix


def execute_command(command, timeout=None):
    """Execute a command using ``subprocess.Popen`` and return the output.

    Returns:
        tuple: Returns a tuple ``(stdout_data, stderr_data)``.
    """

    command = prefix_command(command)

    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate(timeout=None)

    process.terminate()
    process.wait()

    return output, error


def has_command(command, timeout=None):
    """Returns True if it can run the command, otherwise returns False."""

    try:
        response = execute_command(command, timeout=None)
        return response[1] == b""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def has_git(timeout=None):
    """Returns True if it can run ``git --version``, otherwise returns False."""

    return has_command(["git", "--version"], timeout=None)


class Command:
    """Run a command in a new process using ``psutil.Popen``."""

    def __init__(self, command, output_file):
        self.command = prefix_command(command)
        self.output_file = output_file
        self.file_handler = open(self.output_file, "w")

        try:
            self.process = psutil.Popen(
                command,
                stdout=self.file_handler,
                stderr=self.file_handler,
                start_new_session=True,
                shell=platform.system() == "Windows"
            )
        except Exception:
            self.clear()
            raise

    @property
    def pid(self):
        return self.process.pid

    def clear(self):
        """Clear the allocated resources."""

        if self.file_handler:
            self.file_handler.close()
            self.file_handler = None

    def poll(self):
        return self.process.poll()

    def wait(self, timeout=None):
        self.process.wait(timeout=timeout)

    def kill(self):
        """Kill the process and all its children."""

        if self.process and self.process.poll() is None:
            for child in self.process.children(recursive=True):
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    pass
                finally:
                    child.wait(1)

            try:
                self.process.kill()
            except psutil.NoSuchProcess:
                pass
            finally:
                self.process.wait(1)

        self.clear()
