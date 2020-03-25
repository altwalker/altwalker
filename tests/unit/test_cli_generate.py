import unittest
import unittest.mock as mock

from altwalker.exceptions import AltWalkerException
from altwalker._cli_generate import cli_generate


@mock.patch("altwalker._cli_generate.generate_tests")
@mock.patch("click.secho")
class TestCliGenerate(unittest.TestCase):

    def test_generate_tests(self, secho_mock, generate_tests_mock):
        cli_generate("example", mock.sentinel.models, language="python")

        generate_tests_mock.assert_called_once_with(
            "example",
            mock.sentinel.models,
            language="python"
        )

    def test_no_language(self, secho_mock, generate_tests_mock):
        cli_generate("example", mock.sentinel.models, language=None)

        generate_tests_mock.assert_called_once_with(
            "example",
            mock.sentinel.models,
            language="python"
        )

    def test_directory_already_exists(self, secho_mock, generate_tests_mock):
        error_message = "Unkown error."
        generate_tests_mock.side_effect = FileExistsError(error_message)

        with self.assertRaisesRegex(AltWalkerException, error_message):
            cli_generate("example", mock.sentinel.models, language="python")
