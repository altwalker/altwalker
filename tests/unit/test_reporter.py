import os
import json
import unittest.mock as mock

import pytest

from altwalker.reporter import Reporter, Reporting, ClickReporter, FileReporter, \
    PathReporter


class TestReporting:

    @pytest.fixture(autouse=True)
    def setup(self):
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

        assert "reporter_a" in self.reporting._reporters

    def test_register_with_the_same_key(self):
        self.reporting.register("reporter_a", self.reporter_a)

        with pytest.raises(ValueError) as excinfo:
            self.reporting.register("reporter_a", self.reporter_a)

        assert "A reporter with the key: reporter_a is already registered." == str(excinfo.value)

    def test_unregister(self):
        self.reporting.register("reporter_a", self.reporter_a)
        self.reporting.unregister("reporter_a")

        assert "reporter_a" not in self.reporting._reporters

    def test_unregister_inexistent_key(self):
        with pytest.raises(KeyError):
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
        self.reporting.end(message=message, statistics=mock.sentinel.statistics, status=True)

        self.reporter_a.end.assert_called_once_with(message=message, statistics=mock.sentinel.statistics, status=True)
        self.reporter_b.end.assert_called_once_with(message=message, statistics=mock.sentinel.statistics, status=True)

    def test_step_start(self):
        self.register_reporter()

        self.reporting.step_start(self.step)

        self.reporter_a.step_start.assert_called_once_with(self.step)
        self.reporter_b.step_start.assert_called_once_with(self.step)

    def test_step_end(self):
        self.register_reporter()

        step_result = {
            "output": "Outptut message.",
            "error": {
                "message": "Error message",
                "trace": "Traceback"
            }
        }
        self.reporting.step_end(self.step, step_result)

        self.reporter_a.step_end.assert_called_once_with(self.step, step_result)
        self.reporter_b.step_end.assert_called_once_with(self.step, step_result)

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

        assert "reporter_a" in report
        assert report["reporter_a"] == mock.sentinel.report_a

        assert "report_b" not in report


class TestClickReporter:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.reporter = ClickReporter()
        self.reporter._log = mock.Mock(spec=Reporter._log)

        self.step = {
            "id": "v_0",
            "name": "step_name",
            "modelName": "ModelName"
        }

    def test_step_end(self):
        step_result = {
            "output": "",
        }
        self.reporter.step_end(self.step, step_result)

        assert self.reporter._log.called

    def test_step_end_with_output(self):
        step_result = {
            "output": "Step output.",
        }
        self.reporter.step_end(self.step, step_result)

        assert self.reporter._log.called

    def test_step_end_with_result(self):
        step_result = {
            "result": {"prop": "val"},
        }

        def log(string):
            assert "Result:" in string
            assert "\"prop\"" in string
            assert "\"val\"" in string

        self.reporter._log.side_effect = log

        self.reporter.step_end(self.step, step_result)

        assert self.reporter._log.called

    def test_step_end_with_error(self):
        self.reporter._log = mock.Mock(spec=Reporter._log)

        step_result = {
            "output": "",
            "error": {
                "message": "Error message"
            }
        }
        self.reporter.step_end(self.step, step_result)

        assert self.reporter._log.called

    def test_step_end_with_trace(self):
        self.reporter._log = mock.Mock(spec=Reporter._log)

        step_result = {
            "output": "",
            "error": {
                "message": "Error message",
                "trace": "Traceback"
            }
        }
        self.reporter.step_end(self.step, step_result)

        assert self.reporter._log.called

    def test_error(self):
        self.reporter._log = mock.Mock(spec=Reporter._log)

        error_message = "Error message."
        self.reporter.error(self.step, error_message)

        assert self.reporter._log.called

    def test_error_with_trace(self):
        self.reporter._log = mock.Mock(spec=Reporter._log)

        error_message = "Error message."
        trace = "Traceback"
        self.reporter.error(self.step, error_message, trace=trace)

        assert self.reporter._log.called

    def test_error_no_step(self):
        self.reporter._log = mock.Mock(spec=Reporter._log)

        error_message = "Error message."
        self.reporter.error(None, error_message)

        assert self.reporter._log.called


class TestFileReporter:

    def test_reporter(self, tmpdir):
        report_path = os.path.join(str(tmpdir), "report.log")
        FileReporter(report_path)

        assert os.path.isfile(report_path)

    def test_log(self, tmpdir):
        report_path = os.path.join(str(tmpdir), "report.log")
        reporter = FileReporter(report_path)

        message = "Log message."
        reporter._log(message)

        with open(report_path, "r") as fp:
            assert fp.read() == message + "\n"


class TestPathReporter:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.reporter = PathReporter()

    def test_reporter(self):
        report = self.reporter.report()
        assert report == []

    def test_for_step(self):
        step = {
            "id": "id",
            "name": "name",
            "modelName": "ModelName"
        }

        self.reporter.step_end(step, {})
        report = self.reporter.report()

        assert report == [step]

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

        assert report == [step_a, step_b]

    def test_for_fixture(self):
        fixture = {
            "name": "setUpModel",
            "modelName": "ModelName"
        }

        self.reporter.step_end(fixture, {})
        report = self.reporter.report()

        assert report == []

    def test_file(self, tmpdir):
        report_file = "{}/path.json".format(tmpdir)
        self.reporter._file = report_file

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
        self.reporter.end()

        with open(report_file) as fp:
            assert json.load(fp) == self.reporter.report()

    @pytest.mark.parametrize("verbose", [True, False])
    @mock.patch("click.secho")
    def test_verbose(self, secho_mock, verbose, tmpdir):
        report_file = "{}/path.json".format(tmpdir)
        self.reporter._file = report_file
        self.reporter._verbose = verbose

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
        self.reporter.end()

        assert secho_mock.called == verbose
