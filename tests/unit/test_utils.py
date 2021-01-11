import subprocess
import unittest.mock as mock

import pytest

from altwalker._utils import prefix_command, url_join, has_command, has_git


class TestUrlJoin:

    @pytest.mark.parametrize(
        "base, url, expected",
        [
            ("http://localhost:5000", "altwalker", "http://localhost:5000/altwalker"),
            ("http://localhost:5000", "/altwalker", "http://localhost:5000/altwalker"),
            ("http://localhost:5000", "/altwalker/", "http://localhost:5000/altwalker"),
            ("http://localhost:5000/", "altwalker", "http://localhost:5000/altwalker"),
            ("http://localhost:5000/", "/altwalker", "http://localhost:5000/altwalker"),
            ("http://localhost:5000/", "/altwalker/", "http://localhost:5000/altwalker")
        ]
    )
    def test_url_join(self, base, url, expected):
        assert url_join(base, url) == expected


class TestPrefixCommand:

    @mock.patch("platform.system", return_value="Linux")
    @pytest.mark.parametrize(
        "command",
        [
            ["gw"],
            ["gw", "--help"],
            ["gw", "--version"],
            ["git"],
            ["git", "--help"],
            ["git", "--version"]
        ]
    )
    def test_prefix_command_linux(self, platform, command):
        assert prefix_command(command) == command

    @mock.patch("platform.system", return_value="Windows")
    @pytest.mark.parametrize(
        "command, expected",
        [
            (["gw"], ["cmd.exe", "/C", "gw"]),
            (["gw", "--help"], ["cmd.exe", "/C", "gw", "--help"]),
            (["gw", "--version"], ["cmd.exe", "/C", "gw", "--version"]),
            (["git"], ["cmd.exe", "/C", "git"]),
            (["git", "--help"], ["cmd.exe", "/C", "git", "--help"]),
            (["git", "--version"], ["cmd.exe", "/C", "git", "--version"]),
        ]
    )
    def test_prefix_command_windows(self, platform, command, expected):
        assert prefix_command(command) == expected


@mock.patch("subprocess.Popen")
@mock.patch("altwalker._utils.prefix_command", side_effect=lambda command: command)
class TestHasCommand:

    def test_has_command(self, prefix_command_mock, popen_mock):
        process = mock.Mock()
        process.communicate.return_value = (b"git version 2.20.1", b"")
        popen_mock.return_value = process

        assert has_command(["git", "--version"])

    def test_error(self, prefix_command_mock, popen_mock):
        process = mock.Mock()
        process.communicate.return_value = (b"", b"git not installed")
        popen_mock.return_value = process

        assert not has_command(["git", "--version"])

    def test_for_file_not_found(self, prefix_command_mock, popen_mock):
        popen_mock.side_effect = FileNotFoundError("Message")
        assert not has_command(["git", "--version"])

    def test_for_timeout(self, prefix_command_mock, popen_mock):
        popen_mock.side_effect = subprocess.TimeoutExpired("git --version", timeout=1)
        assert not has_command(["git", "--version"])


@mock.patch("subprocess.Popen")
@mock.patch("altwalker._utils.prefix_command", side_effect=lambda command: command)
class TestHasGit:

    def test_has_git(self, prefix_command_mock, popen_mock):
        process = mock.Mock()
        process.communicate.return_value = (b"git version 2.20.1", b"")
        popen_mock.return_value = process

        assert has_git()

    def test_error(self, prefix_command_mock, popen_mock):
        process = mock.Mock()
        process.communicate.return_value = (b"", b"git not installed")
        popen_mock.return_value = process

        assert not has_git()

    def test_for_file_not_found(self, prefix_command_mock, popen_mock):
        popen_mock.side_effect = FileNotFoundError("Message")
        assert not has_git()

    def test_for_timeout(self, prefix_command_mock, popen_mock):
        popen_mock.side_effect = subprocess.TimeoutExpired("git --version", timeout=1)
        assert not has_git()
