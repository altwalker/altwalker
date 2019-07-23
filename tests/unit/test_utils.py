import platform
import unittest
import unittest.mock as mock

from altwalker._utils import get_command, url_join, has_git


class TestGetCommand(unittest.TestCase):

    def test_get_command(self):
        if platform.system() == "Windows":
            self.assertListEqual(get_command("gw"), ["cmd.exe", "/C", "gw"])
        else:
            self.assertListEqual(get_command("gw"), ["gw"])


class TestUrlJoin(unittest.TestCase):

    def test_url_join(self):
        expected = "http://localhost:5000/altwalker"

        self.assertEqual(url_join("http://localhost:5000", "altwalker"), expected)
        self.assertEqual(url_join("http://localhost:5000", "/altwalker"), expected)
        self.assertEqual(url_join("http://localhost:5000", "/altwalker/"), expected)
        self.assertEqual(url_join("http://localhost:5000/", "altwalker"), expected)
        self.assertEqual(url_join("http://localhost:5000/", "/altwalker"), expected)
        self.assertEqual(url_join("http://localhost:5000/", "/altwalker/"), expected)


@mock.patch("subprocess.Popen")
class TestHasGit(unittest.TestCase):

    def test_has_git(self, popen):
        process = mock.Mock()
        process.communicate.return_value = (b"git version 2.20.1", b"")
        popen.return_value = process

        self.assertTrue(has_git())

    def test_stderr(self, popen):
        process = mock.Mock()
        process.communicate.return_value = (b"", b"git not installed")
        popen.return_value = process

        self.assertFalse(has_git())

    def test_for_file_not_found(self, popen):
        popen.side_effect = FileNotFoundError("Message")
        self.assertFalse(has_git())
