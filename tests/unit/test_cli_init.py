import unittest
import unittest.mock as mock

from altwalker.exceptions import AltWalkerException
from altwalker._cli_init import cli_init


@mock.patch("altwalker._cli_init.init_project")
@mock.patch("click.secho")
class TestCliInit(unittest.TestCase):

    def test_init(self, secho_mock, init_project_mock):
        cli_init(
            "example",
            model_paths=mock.sentinel.models,
            language="python",
            git=False,
        )

        init_project_mock.assert_called_once_with(
            "example",
            model_paths=mock.sentinel.models,
            language="python",
            git=False,
        )

    def test_directory_already_exists(self, secho_mock, init_project_mock):
        error_message = "Error message."
        init_project_mock.side_effect = FileExistsError(error_message)

        with self.assertRaisesRegex(AltWalkerException, error_message):
            cli_init(
                "example",
                model_paths=mock.sentinel.models,
                language="python",
                git=False,
            )
