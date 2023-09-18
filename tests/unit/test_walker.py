import unittest.mock as mock

import pytest

from altwalker.exceptions import GraphWalkerException
from altwalker.executor import Executor
from altwalker.planner import Planner
from altwalker.reporter import Reporter
from altwalker.walker import Walker, create_walker


class WalkerTestCase:

    @pytest.fixture(autouse=True)
    def walker(self):
        self.planner = mock.Mock(spec_set=Planner)
        self.executor = mock.Mock(spec_set=Executor)
        self.reporter = mock.Mock(spec_set=Reporter)
        self.walker = Walker(self.planner, self.executor, self.reporter)

        yield self.walker


class TestWalker(WalkerTestCase):

    def test_setup_run(self):
        self.walker._execute_step = mock.Mock()

        self.walker._setup_run()
        self.walker._execute_step.assert_called_once_with({"type": "fixture", "name": "setUpRun"}, current_step=None)

    def test_setup_run_fail(self):
        self.walker._execute_step = mock.Mock()
        self.walker._execute_step.return_value = False

        status = self.walker._setup_run()
        self.walker._execute_step.assert_called_once_with({"type": "fixture", "name": "setUpRun"}, current_step=None)
        assert not status

    def test_setup_run_fail_reporter_end(self):
        self.walker._execute_step = mock.Mock()
        self.walker._execute_step.return_value = False
        self.reporter.end = mock.Mock()

        for _ in self.walker:
            assert False, "The setUpRun fixture should fail"

        self.walker._execute_step.assert_called_once_with({"type": "fixture", "name": "setUpRun"}, current_step=None)
        self.reporter.end.assert_called_once_with(statistics=mock.ANY, status=False)

    def test_teardown_run(self):
        self.walker._execute_step = mock.Mock()

        self.walker._teardown_run()
        self.walker._execute_step.assert_called_once_with({"type": "fixture", "name": "tearDownRun"}, current_step=None)

    def test_teardown_run_fail(self):
        self.walker._execute_step = mock.Mock()
        self.walker._execute_step.return_value = False

        status = self.walker._teardown_run()

        self.walker._execute_step.assert_called_once_with({"type": "fixture", "name": "tearDownRun"}, current_step=None)
        assert not status

    def test_setup_model(self):
        self.walker._execute_step = mock.Mock()

        self.walker._setup_model("modelName")

        self.walker._execute_step.assert_called_once_with(
            {"type": "fixture", "name": "setUpModel", "modelName": "modelName"},
            current_step=None
        )
        assert self.walker._models == ["modelName"]

    def test_setup_model_fail(self):
        self.walker._execute_step = mock.Mock()
        self.walker._execute_step.return_value = False

        status = self.walker._setup_model("modelName")

        self.walker._execute_step.assert_called_once_with(
            {"type": "fixture", "name": "setUpModel", "modelName": "modelName"},
            current_step=None
        )
        assert self.walker._models == []
        assert not status

    def test_teardown_model(self):
        self.walker._execute_step = mock.Mock()
        self.walker._execute_step.return_value = False

        self.walker._teardown_model("modelName")

        self.walker._execute_step.assert_called_once_with(
            {"type": "fixture", "name": "tearDownModel", "modelName": "modelName"},
            current_step=None
        )

    def test_teardown_model_fail(self):
        self.walker._execute_step = mock.Mock()
        self.walker._execute_step.return_value = False

        status = self.walker._teardown_model("modelName")

        self.walker._execute_step.assert_called_once_with(
            {"type": "fixture", "name": "tearDownModel", "modelName": "modelName"},
            current_step=None
        )
        assert not status

    def test_teardown_models(self):
        self.walker._teardown_model = mock.Mock()
        self.walker._teardown_model.return_value = True

        # It should call _teardown_model for models in _models
        self.walker._models = ["modelName"]
        status = self.walker._teardown_models()

        self.walker._teardown_model.assert_called_once_with("modelName")
        assert status

    def test_teardown_models_empty(self):
        self.walker._teardown_model = mock.Mock()
        self.walker._teardown_model.return_value = True

        # It should not call _teardown_model if _models is empty
        self.walker._teardown_models()
        self.walker._teardown_model.assert_not_called()
        assert self.walker._models == []

    def test_teardown_models_fail(self):
        self.walker._teardown_model = mock.Mock()
        self.walker._teardown_model.side_effect = [True, False, True]

        self.walker._models = ["modelName", "modelName", "modelName"]
        status = self.walker._teardown_models()

        assert self.walker._teardown_model.call_count == 3
        assert not status

    def test_update_data(self):
        data_before = {
            "A": "1",
            "B": "2",
        }

        data_after = {
            "A": "1",
            "B": "3",
            "C": "4",
        }

        self.walker._update_data(data_before, data_after)

        self.planner.set_data.assert_any_call("B", "3")
        self.planner.set_data.assert_any_call("C", "4")
        assert self.planner.set_data.call_count == 2

    def test_update_data_with_no_changes(self):
        data = {
            "A": "1",
            "B": "2"
        }

        self.walker._update_data(data, data)
        self.planner.set_data.assert_not_called()

        self.walker._update_data(data, None)
        self.planner.set_data.assert_not_called()


class TestExecuteStep(WalkerTestCase):

    @pytest.fixture(autouse=True)
    def setup_step(self):
        self.step = {
            "name": "step_name",
            "modelName": "ModelName"
        }

    def test_executor(self):
        data = {
            "A": "0"
        }

        self.planner.get_data.return_value = data
        self.executor.execute_step.return_value = {}

        self.walker._execute_step(self.step)

        self.executor.execute_step.assert_called_once_with(
            "ModelName",
            "step_name",
            data=data,
            step=self.step
        )

    def test_result(self):
        return_value = {
            "data": {}
        }

        self.planner.get_data.return_value = {}
        self.executor.execute_step.return_value = return_value

        result = self.walker._execute_step(self.step)
        assert result

    def test_error(self):
        data = {
            "A": "0"
        }

        self.planner.get_data.return_value = data
        self.executor.execute_step.return_value = {
            "error": {
                "message": "Error Message"
            }
        }

        self.walker._execute_step(self.step)

        self.planner.fail.assert_called_once_with("Error Message")

    def test_before_data(self):
        self.planner.get_data.return_value = {}
        self.executor.execute_step.return_value = {}

        self.walker._execute_step(self.step)

        self.planner.get_data.assert_called_once_with()

    def test_after_data(self):
        before_data = {
            "A": "0"
        }

        after_data = {
            "A": "1"
        }

        self.walker._update_data = mock.Mock()
        self.planner.get_data.return_value = before_data
        self.executor.execute_step.return_value = {"data": after_data}

        self.walker._execute_step(self.step)

        self.walker._update_data.assert_called_once_with(before_data, after_data)

    def test_without_after_data(self):
        data = {
            "A": "0"
        }

        self.walker._update_data = mock.Mock()
        self.planner.get_data.return_value = data
        self.executor.execute_step.return_value = {}

        self.walker._execute_step(self.step)

        self.walker._update_data.assert_called_once_with(data, None)


class TestExecuteFixture(WalkerTestCase):

    def test_not_found(self):
        self.executor.has_step.return_value = False
        self.walker._execute_step = mock.Mock(return_value={"output": ""})

        status = self.walker._execute_fixture("setUpModel", model_name="BaseModel")

        self.executor.has_step.assert_called_once_with("BaseModel", "setUpModel")
        self.walker._execute_step.assert_not_called()
        assert status

    @pytest.mark.parametrize("fixture_name, model_name, current_step", [
        ("setUpRun", None, None),
        ("tearDownRun", None, None),
        ("setUpModel", "BaseModel", None),
        ("tearDownModel", "ModelName", None),
        ("beforeStep", "BaseModel", mock.sentinel.STEP),
        ("afterStep", "ModelName", mock.sentinel.STEP),
    ])
    def test_run_fixture(self, fixture_name, model_name, current_step):
        self.executor.has_step.return_value = True
        self.walker._execute_step = mock.Mock(return_value=True)

        status = self.walker._execute_fixture(fixture_name, model_name=model_name, current_step=current_step)

        fixture = {"type": "fixture", "name": fixture_name}
        if model_name:
            fixture["modelName"] = model_name

        self.walker._execute_step.assert_called_once_with(fixture, current_step=current_step)
        assert status

    def test_error(self):
        error_message = "Error message."
        self.walker._execute_step = mock.Mock(side_effect=Exception(error_message))
        self.executor.has_step.return_value = True

        status = self.walker._execute_fixture("setUpRun")

        self.walker._execute_step.assert_called_once_with({"type": "fixture", "name": "setUpRun"}, current_step=None)
        self.walker._planner.fail.assert_called_once_with(error_message)
        self.walker._reporter.error.assert_called_once()
        assert not status


class TestExecuteTest(WalkerTestCase):

    @pytest.fixture(autouse=True)
    def setup_step(self):
        self.step = {
            "id": "id",
            "name": "name",
            "modelName": "ModelName"
        }

    def test_not_found(self):
        self.executor.has_step.return_value = False

        self.walker._execute_test(self.step)

        self.planner.fail.assert_called_once_with("Step not found.")

    def test_not_found_report(self):
        self.executor.has_step.return_value = False

        self.walker._execute_test(self.step)

        self.reporter.error.assert_called_once_with(
            self.step,
            "Step not found.\nUse the 'verify' command to validate the test code against the model(s)."
        )

    def test_run_step(self):
        self.executor.has_step.return_value = True
        self.walker._execute_step = mock.Mock(return_value={"output": ""})

        self.walker._execute_test(self.step)

        self.walker._execute_step.assert_called_once_with(self.step, current_step=self.step)

    def test_report_status(self):
        self.executor.has_step.return_value = True
        self.executor.execute_step.return_value = {"output": ""}

        self.walker._execute_test(self.step)

        self.reporter.step_end.assert_called_once_with(self.step, {"output": ""})

    def test_error(self):
        error = {
            "message": "Error message.",
            "trace": "Trace"
        }

        self.executor.has_step.return_value = True
        self.walker._execute_step = mock.Mock(return_value={"output": "", "error": error})

        self.walker._execute_test(self.step)

        self.walker._execute_step.assert_called_once_with(self.step, current_step=self.step)

    def test_error_status(self):
        self.executor.has_step.return_value = True
        self.walker._execute_step = mock.Mock(return_value=False)

        status = self.walker._execute_test(self.step)
        assert not status

    def test_error_planner(self):
        error_message = "Error message."

        self.executor.has_step.return_value = True
        self.walker._execute_step = mock.Mock(side_effect=Exception(error_message))

        self.walker._execute_test(self.step)

        self.planner.fail.assert_called_once_with(error_message)

    def test_error_report(self):
        error_message = "Error message."

        self.executor.has_step.return_value = True
        self.walker._execute_step = mock.Mock(side_effect=Exception(error_message))

        self.walker._execute_test(self.step)

        self.reporter.error.assert_called_once_with(self.step, error_message, trace=mock.ANY)

    def test_exception(self):
        self.executor.has_step.return_value = True
        self.executor.execute_step.side_effect = Exception("Error message.")

        self.walker._execute_test(self.step)

        self.reporter.error.assert_called_once_with(self.step, "Error message.", trace=mock.ANY)

    def test_exception_status(self):
        self.executor.has_step.return_value = True
        self.executor.execute_step.side_effect = Exception("Error message.")

        status = self.walker._execute_test(self.step)
        assert not status

    def test_exception_planner(self):
        self.executor.has_step.return_value = True
        self.executor.execute_step.side_effect = Exception("Error message.")

        self.walker._execute_test(self.step)

        self.planner.fail.assert_called_once_with("Error message.")

    @mock.patch("traceback.format_exc")
    def test_exception_reporter(self, trace_mock):
        self.executor.has_step.return_value = True
        self.executor.execute_step.side_effect = Exception("Error message.")
        trace_mock.return_value = "Trace."

        self.walker._execute_test(self.step)

        self.reporter.error.assert_called_once_with(self.step, "Error message.", trace="Trace.")


class TestRunStep(WalkerTestCase):

    @pytest.fixture(autouse=True)
    def setup_step(self):
        self.step = {
            "id": "id",
            "name": "name",
            "modelName": "ModelName"
        }

    def test_step_without_name(self):
        self.walker._execute_step = mock.Mock()
        self.walker._execute_fixture = mock.Mock()

        status = self.walker._run_step({"id": "id", "modelName": "BaseModel"})

        self.walker._execute_step.assert_not_called()
        self.walker._execute_fixture.assert_not_called()
        assert status

    def test_run_step(self):
        self.walker._execute_test = mock.Mock(return_value=True)
        self.walker._execute_fixture = mock.Mock(return_value=True)

        status = self.walker._run_step(self.step)

        self.walker._execute_test.assert_called_once_with(self.step)
        self.walker._execute_fixture.assert_any_call("beforeStep", current_step=self.step)
        self.walker._execute_fixture.assert_any_call("beforeStep", model_name=self.step["modelName"], current_step=self.step)
        self.walker._execute_fixture.assert_any_call("afterStep", current_step=self.step)
        self.walker._execute_fixture.assert_any_call("afterStep", model_name=self.step["modelName"], current_step=self.step)
        assert status

    def test_fail(self):
        self.walker._execute_test = mock.Mock(return_value=False)
        self.walker._execute_fixture = mock.Mock(return_value=True)

        status = self.walker._run_step(self.step)

        assert not status

    @pytest.mark.parametrize("fixture_mock_side_effect", [
        [False, True, True, True],
        [True, False, True, True],
        [True, True, False, True],
        [True, True, True, False],
    ])
    def test_fixture_fail(self, fixture_mock_side_effect):
        self.walker._execute_test = mock.Mock(return_value=True)
        self.walker._execute_fixture = mock.Mock(side_effect=fixture_mock_side_effect)

        status = self.walker._run_step(self.step)

        assert not status


class TestItter(WalkerTestCase):

    @pytest.fixture(autouse=True)
    def setup_mocks(self, walker):
        walker._setup_run = mock.MagicMock()
        walker._setup_model = mock.MagicMock()
        walker._teardown_models = mock.MagicMock()
        walker._teardown_run = mock.MagicMock()

    def test_fixtures(self):
        self.planner.has_next.return_value = False

        for _ in self.walker:
            pass

        self.walker._setup_run.assert_called_once_with()
        self.walker._teardown_models.assert_called_once_with()
        self.walker._teardown_run.assert_called_once_with()

    def test_setup_run_fail(self):
        self.walker._setup_run.return_value = False
        self.planner.has_next.return_value = False

        for _ in self.walker:
            pass

        self.walker._setup_run.assert_called_once_with()
        self.walker._teardown_run.assert_not_called()
        assert not self.walker.status

    def test_setup_model(self):
        self.walker._setup_run.return_value = True
        self.planner.has_next.side_effect = [True, False]
        self.planner.get_next.return_value = {"name": "name", "modelName": "modelName"}

        for _ in self.walker:
            pass

        self.walker._setup_model.assert_called_once_with("modelName")

    def test_setup_model_not_called_twice(self):
        self.walker._models = ["modelName"]
        self.walker._setup_run.return_value = True
        self.planner.has_next.side_effect = [True, False]
        self.planner.get_next.return_value = {"name": "name", "modelName": "modelName"}

        for _ in self.walker:
            pass

        self.walker._setup_model.assert_not_called()

    def test_setup_model_fails(self):
        self.walker._setup_run.return_value = True
        self.walker._setup_model.return_value = False
        self.walker._teardown_models.return_value = True
        self.walker._teardown_run.return_value = True

        self.planner.has_next.return_value = True
        self.planner.get_next.return_value = {"name": "name", "modelName": "modelName"}

        for _ in self.walker:
            pass

        self.walker._setup_model.assert_called_once_with("modelName")
        assert not self.walker.status

    def test_teardown_models_fails(self):
        self.walker._setup_run.return_value = True
        self.walker._setup_model.return_value = True
        self.walker._teardown_models.return_value = True
        self.walker._teardown_run.return_value = False

        self.planner.has_next.return_value = False

        for _ in self.walker:
            pass

        assert not self.walker.status

    def test_teardown_run_fails(self):
        self.walker._setup_run.return_value = True
        self.walker._setup_model.return_value = True
        self.walker._teardown_models.return_value = False
        self.walker._teardown_run.return_value = True

        self.planner.has_next.return_value = False

        for _ in self.walker:
            pass

        assert not self.walker.status

    def test_yield(self):
        self.walker._run_step = mock.MagicMock()
        self.walker._run_step.return_value = True

        self.walker._setup_run.return_value = True
        self.planner.has_next.side_effect = [True, False]
        self.planner.get_next.return_value = {"name": "name", "modelName": "modelName"}

        for step in self.walker:
            assert step == {"name": "name", "modelName": "modelName", "status": True}

    def test_report(self):
        self.planner.has_next.return_value = False

        for _ in self.walker:
            pass

        self.reporter.start.assert_called_once_with()
        self.reporter.end.assert_called_once_with(statistics=mock.ANY, status=mock.ANY)

    def test_get_next_fail(self):
        self.walker._setup_run.return_value = True
        self.walker._setup_model.return_value = True
        self.walker._teardown_models.return_value = True
        self.walker._teardown_run.return_value = True

        self.planner.has_next.return_value = True
        self.planner.get_next.side_effect = GraphWalkerException("Fail get_next")

        for _ in self.walker:
            pass

        self.reporter.error.assert_called_with(None, "Fail get_next")
        assert not self.walker.status

    def test_should_skip_edge_without_name(self):
        self.walker._execute_test = mock.MagicMock()
        self.walker._execute_fixture = mock.MagicMock()

        self.planner.has_next.side_effect = [True, False]
        self.planner.get_next.side_effect = [
            {"modelName": "modelName"}
        ]

        for step in self.walker:
            pass

        self.walker._execute_fixture.assert_not_called()
        self.walker._execute_test.assert_not_called()


class TestRun(WalkerTestCase):

    @pytest.fixture(autouse=True)
    def setup_mocks(self, walker):
        walker._run_step = mock.MagicMock()
        walker._setup_run = mock.MagicMock()
        walker._setup_model = mock.MagicMock()
        walker._teardown_models = mock.MagicMock()
        walker._teardown_run = mock.MagicMock()

    def test_success(self):
        self.walker._run_step.return_value = True

        self.planner.has_next.side_effect = [True, False]
        self.planner.get_next.return_value = {"name": "name", "modelName": "modelName"}

        status = self.walker.run()
        assert status

    def test_fail(self):
        self.walker._setup_run.return_value = True
        self.walker._setup_model.return_value = True
        self.walker._teardown_models.return_value = True
        self.walker._teardown_run.return_value = True
        self.walker._run_step.return_value = False

        self.planner.has_next.side_effect = [True, False]
        self.planner.get_next.return_value = {"name": "name", "modelName": "modelName"}

        status = self.walker.run()
        assert not status


class TestCreateWalker:

    def test_planner(self):
        planner = mock.sentinel.planner
        executor = mock.sentinel.executor

        walker = create_walker(planner, executor)

        assert walker._planner == planner

    def test_executor(self):
        planner = mock.sentinel.planner
        executor = mock.sentinel.executor

        walker = create_walker(planner, executor)

        assert walker._executor == executor

    def test_reporter(self):
        planner = mock.sentinel.planner
        executor = mock.sentinel.executor
        reporter = mock.sentinel.reporter

        walker = create_walker(planner, executor, reporter=reporter)

        assert walker._reporter == reporter
