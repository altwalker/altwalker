import unittest
import unittest.mock as mock

from altwalker.walker import Walker


class WalkerSetUp(unittest.TestCase):

    def setUp(self):
        self.planner = mock.Mock()
        self.executor = mock.Mock()
        self.reporter = mock.Mock()

        self.walker = Walker(self.planner, self.executor, self.reporter)


class TestWalker(WalkerSetUp):

    def test_setUpRun(self):
        self.walker._run_step = mock.Mock()

        self.walker._setUpRun()
        self.walker._run_step.assert_called_once_with({"type": "fixture", "name": "setUpRun"}, optional=True)

    def test_setUpRun_fail(self):
        self.walker._run_step = mock.Mock()
        self.walker._run_step.return_value = False

        status = self.walker._setUpRun()
        self.walker._run_step.assert_called_once_with({"type": "fixture", "name": "setUpRun"}, optional=True)
        self.assertFalse(status)

    def test_tearDownRun(self):
        self.walker._run_step = mock.Mock()

        self.walker._tearDownRun()
        self.walker._run_step.assert_called_once_with({"type": "fixture", "name": "tearDownRun"}, optional=True)

    def test_tearDownRun_fail(self):
        self.walker._run_step = mock.Mock()
        self.walker._run_step.return_value = False

        status = self.walker._tearDownRun()

        self.assertFalse(status)
        self.walker._run_step.assert_called_once_with({"type": "fixture", "name": "tearDownRun"}, optional=True)

    def test_setUpModel(self):
        self.walker._run_step = mock.Mock()

        self.walker._setUpModel("modelName")

        self.walker._run_step.assert_called_once_with(
            {"type": "fixture", "name": "setUpModel", "modelName": "modelName"},
            optional=True)
        self.assertListEqual(self.walker._models, ["modelName"])

    def test_setUpModel_fail(self):
        self.walker._run_step = mock.Mock()
        self.walker._run_step.return_value = False

        status = self.walker._setUpModel("modelName")

        self.walker._run_step.assert_called_once_with(
            {"type": "fixture", "name": "setUpModel", "modelName": "modelName"},
            optional=True)
        self.assertListEqual(self.walker._models, [])
        self.assertFalse(status)

    def test_tearDownModel(self):
        self.walker._run_step = mock.Mock()
        self.walker._run_step.return_value = False

        self.walker._tearDownModel("modelName")
        self.walker._run_step.assert_called_once_with(
            {"type": "fixture", "name": "tearDownModel", "modelName": "modelName"},
            optional=True)

    def test_tearDownModel_fail(self):
        self.walker._run_step = mock.Mock()
        self.walker._run_step.return_value = False

        status = self.walker._tearDownModel("modelName")

        self.assertFalse(status)
        self.walker._run_step.assert_called_once_with(
            {"type": "fixture", "name": "tearDownModel", "modelName": "modelName"},
            optional=True)

    def test_tearDownModels(self):
        self.walker._tearDownModel = mock.Mock()
        self.walker._tearDownModel.return_value = True

        # Should not call _tearDownModel if _models is empty
        self.walker._tearDownModels()
        self.walker._tearDownModel.assert_not_called()
        self.assertListEqual(self.walker._models, [])

        # Should call _tearDownModel for models in _models
        self.walker._models = ["modelName"]
        status = self.walker._tearDownModels()

        self.walker._tearDownModel.assert_called_once_with("modelName")
        self.assertTrue(status)

    def test_tearDownModels_fail(self):
        self.walker._tearDownModel = mock.Mock()
        self.walker._tearDownModel.side_effect = [True, False, True]

        self.walker._models = ["modelName", "modelName", "modelName"]
        status = self.walker._tearDownModels()

        self.assertEqual(self.walker._tearDownModel.call_count, 3)
        self.assertFalse(status)

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
        self.assertEqual(2, self.planner.set_data.call_count)

    def test_update_data_with_no_changes(self):
        data = {
            "A": "1",
            "B": "2"
        }

        self.walker._update_data(data, data)
        self.planner.set_data.assert_not_called()

        self.walker._update_data(data, None)
        self.planner.set_data.assert_not_called()


class TestExecuteStep(WalkerSetUp):

    def setUp(self):
        super().setUp()

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

        self.executor.execute_step.assert_called_once_with("ModelName", "step_name", data)

    def test_result(self):
        result = {
            "data": {}
        }

        self.planner.get_data.return_value = {}
        self.executor.execute_step.return_value = result

        result = self.walker._execute_step(self.step)
        self.assertTrue(result)

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

    def test_without_after(self):
        data = {
            "A": "0"
        }

        self.walker._update_data = mock.Mock()
        self.planner.get_data.return_value = data
        self.executor.execute_step.return_value = {}

        self.walker._execute_step(self.step)

        self.walker._update_data.assert_called_once_with(data, None)


class TestRunStep(WalkerSetUp):

    def setUp(self):
        super().setUp()

        self.step = {
            "id": "id",
            "name": "name",
            "modelName": "ModelName"
        }

    def test_optional(self):
        self.executor.has_step.return_value = False

        status = self.walker._run_step(self.step, optional=True)
        self.assertTrue(status)

    def test_not_optional(self):
        self.executor.has_step.return_value = False

        status = self.walker._run_step(self.step, optional=False)
        self.assertFalse(status)

    def test_not_found(self):
        self.executor.has_step.return_value = False

        self.walker._run_step(self.step, optional=False)

        self.planner.fail.assert_called_once_with("Step not found.")

    def test_not_found_report(self):
        self.executor.has_step.return_value = False

        self.walker._run_step(self.step, optional=False)

        self.reporter.error.assert_called_once_with(self.step, "Step not found.")

    def test_run_step(self):
        self.executor.has_step.return_value = True
        self.walker._execute_step = mock.Mock(return_value={"output": ""})

        self.walker._run_step(self.step, optional=False)

        self.walker._execute_step.assert_called_once_with(self.step)

    def test_report_status(self):
        self.executor.has_step.return_value = True
        self.executor.execute_step.return_value = {"output": ""}

        self.walker._run_step(self.step, optional=False)

        self.reporter.step_end.assert_called_once_with(self.step, {"output": ""})

    def test_error(self):
        error = {
            "message": "Error message.",
            "trace": "Trace"
        }

        self.executor.has_step.return_value = True
        self.walker._execute_step = mock.Mock(return_value={"output": "", "error": error})

        self.walker._run_step(self.step, optional=False)

        self.walker._execute_step.assert_called_once_with(self.step)

    def test_error_status(self):
        self.executor.has_step.return_value = True
        self.walker._execute_step = mock.Mock(return_value=False)

        status = self.walker._run_step(self.step, optional=False)
        self.assertFalse(status)

    def test_error_planner(self):
        error_message = "Error message."

        self.executor.has_step.return_value = True
        self.walker._execute_step = mock.Mock(side_effect=Exception(error_message))

        self.walker._run_step(self.step, optional=False)

        self.planner.fail.assert_called_once_with(error_message)

    def test_error_report(self):
        error_message = "Error message."

        self.executor.has_step.return_value = True
        self.walker._execute_step = mock.Mock(side_effect=Exception(error_message))

        self.walker._run_step(self.step, optional=False)

        self.reporter.error.assert_called_once_with(self.step, error_message, trace=mock.ANY)

    def test_exception(self):
        self.executor.has_step.return_value = True
        self.executor.execute_step.side_effect = Exception("Error message.")

        self.walker._run_step(self.step)

        self.reporter.error.assert_called_once_with(self.step, "Error message.", trace=mock.ANY)

    def test_exception_status(self):
        self.executor.has_step.return_value = True
        self.executor.execute_step.side_effect = Exception("Error message.")

        status = self.walker._run_step(self.step)
        self.assertFalse(status)

    def test_exception_planner(self):
        self.executor.has_step.return_value = True
        self.executor.execute_step.side_effect = Exception("Error message.")

        self.walker._run_step(self.step)

        self.planner.fail.assert_called_once_with("Error message.")

    @mock.patch("traceback.format_exc")
    def test_exception_reporter(self, trace_mock):
        self.executor.has_step.return_value = True
        self.executor.execute_step.side_effect = Exception("Error message.")
        trace_mock.return_value = "Trace."

        self.walker._run_step(self.step)

        self.reporter.error.assert_called_once_with(self.step, "Error message.", trace="Trace.")


class TestItter(WalkerSetUp):

    def setUp(self):
        super().setUp()

        self.walker._setUpRun = mock.MagicMock()
        self.walker._setUpModel = mock.MagicMock()
        self.walker._tearDownModels = mock.MagicMock()
        self.walker._tearDownRun = mock.MagicMock()

    def test_fixtures(self):
        self.planner.has_next.return_value = False

        for _ in self.walker:
            pass

        self.walker._setUpRun.assert_called_once_with()
        self.walker._tearDownModels.assert_called_once_with()
        self.walker._tearDownRun.assert_called_once_with()

    def test_setUpRun_fail(self):
        self.walker._setUpRun.return_value = False
        self.planner.has_next.return_value = False

        for _ in self.walker:
            pass

        self.walker._setUpRun.assert_called_once_with()
        self.walker._tearDownRun.assert_not_called()
        self.assertFalse(self.walker.status)

    def test_setUpModel(self):
        self.walker._setUpRun.return_value = True
        self.planner.has_next.side_effect = [True, False]
        self.planner.get_next.return_value = {"name": "name", "modelName": "modelName"}

        for _ in self.walker:
            pass

        self.walker._setUpModel.assert_called_once_with("modelName")

    def test_setUpModel_not_called_twice(self):
        self.walker._models = ["modelName"]
        self.walker._setUpRun.return_value = True
        self.planner.has_next.side_effect = [True, False]
        self.planner.get_next.return_value = {"name": "name", "modelName": "modelName"}

        for _ in self.walker:
            pass

        self.walker._setUpModel.assert_not_called()

    def test_setUpModel_fails(self):
        self.walker._setUpRun.return_value = True
        self.walker._setUpModel.return_value = False
        self.walker._tearDownModels.return_value = True
        self.walker._tearDownRun.return_value = True

        self.planner.has_next.return_value = True
        self.planner.get_next.return_value = {"name": "name", "modelName": "modelName"}

        for _ in self.walker:
            pass

        self.walker._setUpModel.assert_called_once_with("modelName")
        self.assertFalse(self.walker.status)

    def test_tearDownModels_fails(self):
        self.walker._setUpRun.return_value = True
        self.walker._setUpModel.return_value = True
        self.walker._tearDownModels.return_value = True
        self.walker._tearDownRun.return_value = False

        self.planner.has_next.return_value = False

        for _ in self.walker:
            pass

        self.assertFalse(self.walker.status)

    def test_tearDownRun_fails(self):
        self.walker._setUpRun.return_value = True
        self.walker._setUpModel.return_value = True
        self.walker._tearDownModels.return_value = False
        self.walker._tearDownRun.return_value = True

        self.planner.has_next.return_value = False

        for _ in self.walker:
            pass

        self.assertFalse(self.walker.status)

    def test_yield(self):
        self.walker._run_step = mock.MagicMock()
        self.walker._run_step.return_value = True

        self.walker._setUpRun.return_value = True
        self.planner.has_next.side_effect = [True, False]
        self.planner.get_next.return_value = {"name": "name", "modelName": "modelName"}

        for step in self.walker:
            self.assertDictEqual(step,  {"name": "name", "modelName": "modelName", "status": True})

    def test_report(self):
        self.planner.has_next.return_value = False

        for _ in self.walker:
            pass

        self.reporter.start.assert_called_once_with()
        self.reporter.end.assert_called_once_with()
