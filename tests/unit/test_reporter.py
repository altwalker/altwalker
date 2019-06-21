import sys
import unittest
import unittest.mock as mock
from pathlib import Path

import pytest

from altwalker.reporter import _add_timestamp, _format_step, _format_step_info, \
    Reporter, Reporting, _Formater, PrintReporter, FileReporter, ClickReporter, \
    PathReporter


class TestAddTimestamp(unittest.TestCase):

    def test_add_timestamp(self):
        string = _add_timestamp("message")
        self.assertRegex(string, r"\[.*-.*-.* .*:.*:.*\..*\] message")


class TestFormatStep(unittest.TestCase):

    def test_for_element(self):
        step = {
            "modelName": "ModelA",
            "name": "vertex_name"
        }

        self.assertEqual("ModelA.vertex_name", _format_step(step))

    def test_for_fixture(self):
        step = {
            "name": "vertex_name"
        }

        self.assertEqual("vertex_name", _format_step(step))


class TestFormatStepInfo(unittest.TestCase):

    def test_for_data(self):
        step = {
            "data": {
                "key": "value"
            }
        }

        self.assertRegex(_format_step_info(step), "Data:\n")
        self.assertRegex(_format_step_info(step), "\"key\": \"value\"")

    def test_for_unvisited_elements(self):
        step = {
            "unvisitedElements": [
                {
                    "name": "Element"
                }
            ]
        }

        self.assertRegex(_format_step_info(step), "Unvisited Elements:\n")
        self.assertRegex(_format_step_info(step), "\"name\": \"Element\"")


class TestReporting(unittest.TestCase):

    def setUp(self):
        self.reporting = Reporting()

        self.reporter_a = mock.Mock(spec=Reporter)
        self.reporter_b = mock.Mock(spec=Reporter)

        self.step = {
            "id": "v_0",
            "name": "step_name",
            "modelName": "ModelName"
        }

    def register_reporter(self):
        self.reporting.register("reporter_a", self.reporter_a)
        self.reporting.register("reporter_b", self.reporter_b)

    def test_register(self):
        self.reporting.register("reporter_a", self.reporter_a)

        self.assertTrue("reporter_a" in self.reporting._reporters)

    def test_register_with_the_same_key(self):
        self.reporting.register("reporter_a", self.reporter_a)

        with self.assertRaisesRegex(ValueError, "A reporter with the key: .* is already registered."):
            self.reporting.register("reporter_a", self.reporter_a)

    def test_unregister(self):
        self.reporting.register("reporter_a", self.reporter_a)
        self.reporting.unregister("reporter_a")

        self.assertFalse("reporter_a" in self.reporting._reporters)

    def test_unregister_inexistent_key(self):
        with self.assertRaises(KeyError):
            self.reporting.unregister("inexistent")

    def test_start(self):
        self.register_reporter()

        message = "Example message"
        self.reporting.start(message=message)

        self.reporter_a.start.assert_called_once_with(message=message)
        self.reporter_b.start.assert_called_once_with(message=message)

    def test_end(self):
        self.register_reporter()

        message = "Example message"
        self.reporting.end(message=message)

        self.reporter_a.end.assert_called_once_with(message=message)
        self.reporter_b.end.assert_called_once_with(message=message)

    def test_step_start(self):
        self.register_reporter()

        self.reporting.step_start(self.step)

        self.reporter_a.step_start.assert_called_once_with(self.step)
        self.reporter_b.step_start.assert_called_once_with(self.step)

    def test_step_end(self):
        self.register_reporter()

        result = {
            "output": "Outptut message.",
            "error": {
                "message": "Error message",
                "trace": "Traceback"
            }
        }
        self.reporting.step_end(self.step, result)

        self.reporter_a.step_end.assert_called_once_with(self.step, result)
        self.reporter_b.step_end.assert_called_once_with(self.step, result)

    def test_error(self):
        self.register_reporter()

        error_message = "Error message."
        trace = "Traceback"
        self.reporting.error(self.step, error_message, trace=trace)

        self.reporter_a.error.assert_called_once_with(self.step, error_message, trace=trace)
        self.reporter_b.error.assert_called_once_with(self.step, error_message, trace=trace)

    def test_report(self):
        self.register_reporter()

        self.reporting.report()

        self.reporter_a.report.assert_called_once_with()
        self.reporter_b.report.assert_called_once_with()

    def test_report_value(self):
        self.reporter_a.report.return_value = mock.sentinel.report_a
        self.reporter_b.report.return_value = None

        self.register_reporter()

        report = self.reporting.report()

        self.assertTrue("reporter_a" in report)
        self.assertEqual(report["reporter_a"], mock.sentinel.report_a)

        self.assertFalse("report_b" in report)


class TestFormater(unittest.TestCase):

    def setUp(self):
        self.formater = _Formater()
        self.formater._log = mock.Mock(spec=Reporter._log)

        self.step = {
            "id": "v_0",
            "name": "step_name",
            "modelName": "ModelName"
        }

    def test_step_start(self):
        self.formater.step_start(self.step)

        self.assertEqual(self.formater._log.mock_calls, [mock.ANY])

    def test_step_end(self):
        result = {
            "output": "",
        }
        self.formater.step_end(self.step, result)

        self.assertEqual(self.formater._log.mock_calls, [mock.ANY])

    def test_step_end_with_output(self):
        result = {
            "output": "Step output.",
        }
        self.formater.step_end(self.step, result)

        self.assertEqual(self.formater._log.mock_calls, [mock.ANY])

    def test_step_end_with_error(self):
        result = {
            "output": "",
            "error": {
                "message": "Error message"
            }
        }
        self.formater.step_end(self.step, result)

        self.assertEqual(self.formater._log.mock_calls, [mock.ANY])

    def test_step_end_with_trace(self):
        result = {
            "output": "",
            "error": {
                "message": "Error message",
                "trace": "Traceback"
            }
        }
        self.formater.step_end(self.step, result)

        self.assertEqual(self.formater._log.mock_calls, [mock.ANY])

    def test_error(self):
        error_message = "Error message."
        self.formater.error(self.step, error_message)

        self.assertEqual(self.formater._log.mock_calls, [mock.ANY])

    def test_error_with_trace(self):
        error_message = "Error message."
        trace = "Traceback"
        self.formater.error(self.step, error_message, trace=trace)

        self.assertEqual(self.formater._log.mock_calls, [mock.ANY])


class TestPrintReporter(unittest.TestCase):

    @pytest.mark.skipif(sys.version_info < (3, 5), reason="Requires python3.5 or higher.")
    def test_reporter(self):
        with mock.patch("altwalker.reporter.print") as print_:
            reporter = PrintReporter()

            message = "Log message."
            reporter._log(message)

            print_.assert_called_once_with(message)


class TestFileReporter(unittest.TestCase):

    def setUp(self):
        self.path = "report.txt"

    def tearDown(self):
        path = Path(self.path)

        if path.exists():
            path.unlink()

    def test_reporter(self):
        FileReporter(self.path)

        self.assertTrue(Path(self.path).exists())

    @pytest.mark.skipif(sys.version_info < (3, 5), reason="Requires python3.5 or higher.")
    def test_log(self):
        open_ = mock.mock_open()

        with mock.patch('altwalker.reporter.open', open_, create=True):
            reporter = FileReporter(self.path)
            message = "Log message."
            reporter._log(message)

            open_().write.assert_called_once_with(message + "\n")


class TestClickReporter(unittest.TestCase):

    def setUp(self):
        self.reporter = ClickReporter()

        self.step = {
            "id": "v_0",
            "name": "step_name",
            "modelName": "ModelName"
        }

    def test_step_end(self):
        self.reporter._log = mock.Mock(spec=Reporter._log)

        result = {
            "output": "",
        }
        self.reporter.step_end(self.step, result)

        self.assertEqual(self.reporter._log.mock_calls, [mock.ANY])

    def test_step_end_with_output(self):
        self.reporter._log = mock.Mock(spec=Reporter._log)

        result = {
            "output": "Step output.",
        }
        self.reporter.step_end(self.step, result)

        self.assertEqual(self.reporter._log.mock_calls, [mock.ANY])

    def test_step_end_with_error(self):
        self.reporter._log = mock.Mock(spec=Reporter._log)

        result = {
            "output": "",
            "error": {
                "message": "Error message"
            }
        }
        self.reporter.step_end(self.step, result)

        self.assertEqual(self.reporter._log.mock_calls, [mock.ANY])

    def test_step_end_with_trace(self):
        self.reporter._log = mock.Mock(spec=Reporter._log)

        result = {
            "output": "",
            "error": {
                "message": "Error message",
                "trace": "Traceback"
            }
        }
        self.reporter.step_end(self.step, result)

        self.assertEqual(self.reporter._log.mock_calls, [mock.ANY])

    def test_error(self):
        self.reporter._log = mock.Mock(spec=Reporter._log)

        error_message = "Error message."
        self.reporter.error(self.step, error_message)

        self.assertEqual(self.reporter._log.mock_calls, [mock.ANY])

    def test_error_with_trace(self):
        self.reporter._log = mock.Mock(spec=Reporter._log)

        error_message = "Error message."
        trace = "Traceback"
        self.reporter.error(self.step, error_message, trace=trace)

        self.assertEqual(self.reporter._log.mock_calls, [mock.ANY])

    @mock.patch("click.echo")
    def test_log(self, echo):
        message = "Log message."
        self.reporter._log(message)

        echo.assert_called_once_with(message)


class TestPathReporter(unittest.TestCase):

    def setUp(self):
        self.reporter = PathReporter()

    def test_reporter(self):
        report = self.reporter.report()
        self.assertListEqual(report, [])

    def test_for_step(self):
        step = {
            "id": "id",
            "name": "name",
            "modelName": "ModelName"
        }

        self.reporter.step_end(step, {})
        report = self.reporter.report()

        self.assertListEqual(report, [step])

    def test_for_multiple_steps(self):
        step_a = {
            "id": "0",
            "name": "step_a",
            "modelName": "ModelName"
        }

        step_b = {
            "id": "1",
            "name": "step_b",
            "modelName": "ModelName"
        }

        self.reporter.step_end(step_a, {})
        self.reporter.step_end(step_b, {})

        report = self.reporter.report()

        self.assertListEqual(report, [step_a, step_b])

    def test_for_fixture(self):
        fixture = {
            "name": "setUpModel",
            "modelName": "ModelName"
        }

        self.reporter.step_end(fixture, {})
        report = self.reporter.report()

        self.assertListEqual(report, [])
