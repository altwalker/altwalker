import unittest
import unittest.mock as mock

from altwalker.walker import Walker


class TestWalker(unittest.TestCase):

    def setUp(self):
        self.planner = mock.MagicMock()
        self.executor = mock.MagicMock()
        self.reporter = mock.MagicMock()
        self.data = mock.MagicMock()

        self.walker = Walker(self.planner, self.executor, self.data, self.reporter)

    def test_setUpRun(self):
        self.walker._run_step = mock.Mock()

        self.walker._setUpRun()
        self.walker._run_step.assert_called_once_with({"type": "fixture", "name": "setUpRun"}, optional=True)

    def test_tearDownRun(self):
        self.walker._run_step = mock.Mock()

        self.walker._tearDownRun()
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

        self.walker._tearDownModel("modelName")
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


class TestRunStep(unittest.TestCase):

    def setUp(self):
        self.planner = mock.MagicMock()
        self.executor = mock.MagicMock()
        self.reporter = mock.MagicMock()
        self.data = mock.MagicMock()

        self.walker = Walker(self.planner, self.executor, self.data, reporter=self.reporter)

    def test_execute_step(self):
        step = {
            "name": "name",
            "modelName": "modelName"
        }
        self.executor.has_step.return_value = True
        self.executor.execute_step.return_value = {"output": ""}

        status = self.walker._run_step(step)

        self.executor.has_step.assert_called_once_with(step["modelName"], step["name"])
        self.executor.execute_step.assert_called_once_with(step["modelName"], step["name"], self.data)
        self.assertTrue(status)

    def test_optional(self):
        step = {
            "name": "name",
            "modelName": "modelName"
        }
        self.executor.has_step.return_value = False

        # Should return false if the step is not found and the optional flag is set to false
        status = self.walker._run_step(step, optional=False)
        self.assertFalse(status)

        # Should return true if the step is not found and the optional flag is set to true
        status = self.walker._run_step(step, optional=True)
        self.assertTrue(status)

    def test_exception(self):
        step = {
            "id": "id",
            "name": "name",
            "modelName": "modelName"
        }
        self.executor.has_step.return_value = True
        self.executor.execute_step.side_effect = Exception("error message")

        status = self.walker._run_step(step)
        self.assertFalse(status)

        self.planner.fail.assert_called_once_with(step, "error message")

    def test_report(self):
        step = {
            "name": "name",
            "modelName": "modelName"
        }
        self.executor.has_step.return_value = True
        self.executor.execute_step.return_value = {"output": ""}

        self.walker._run_step(step)

        self.reporter.step_start.assert_called_once_with(step)
        self.reporter.step_status.assert_called_once_with(step, output="", failure=False)

    def test_report_fail(self):
        step = {
            "id": "id",
            "name": "name",
            "modelName": "modelName"
        }

        self.executor.has_step.return_value = True
        self.executor.execute_step.side_effect = Exception("error message")

        status = self.walker._run_step(step)
        self.assertFalse(status)

        self.reporter.step_status.assert_called_once_with(step, failure=True)

    def test_reporter_output(self):
        step = {
            "name": "name",
            "modelName": "modelName"
        }
        self.executor.has_step.return_value = True
        self.executor.execute_step.return_value = {"output": "output"}

        self.walker._run_step(step)
        self.reporter.step_status.assert_called_once_with(step, output="output", failure=False)


class TestItter(unittest.TestCase):

    def setUp(self):
        self.planner = mock.MagicMock()
        self.executor = mock.MagicMock()
        self.reporter = mock.MagicMock()
        self.data = mock.MagicMock()

        self.walker = Walker(self.planner, self.executor, self.data, reporter=self.reporter)

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
        self.assertFalse(self.walker._status)

    def test_setUpModel(self):
        self.walker._setUpRun.return_value = True
        self.planner.has_next.side_effect = [True, False]
        self.planner.get_next.return_value = {"name": "name", "modelName": "modelName"}

        for _ in self.walker:
            pass

        self.walker._setUpModel.assert_called_once_with("modelName")

    def test_setUpModel_twice(self):
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
        self.assertFalse(self.walker._status)

    def test_tearDownModels_fails(self):
        self.walker._setUpRun.return_value = True
        self.walker._setUpModel.return_value = True
        self.walker._tearDownModels.return_value = True
        self.walker._tearDownRun.return_value = False

        self.planner.has_next.return_value = False

        for _ in self.walker:
            pass

        self.assertFalse(self.walker._status)

    def test_tearDownRun_fails(self):
        self.walker._setUpRun.return_value = True
        self.walker._setUpModel.return_value = True
        self.walker._tearDownModels.return_value = False
        self.walker._tearDownRun.return_value = True

        self.planner.has_next.return_value = False

        for _ in self.walker:
            pass

        self.assertFalse(self.walker._status)

    def test_yield(self):
        self.walker._run_step = mock.MagicMock()
        self.walker._run_step.return_value = True

        self.walker._setUpRun.return_value = True
        self.planner.has_next.side_effect = [True, False]
        self.planner.get_next.return_value = {"name": "name", "modelName": "modelName"}

        for step in self.walker:
            self.assertDictEqual(step,  {"name": "name", "modelName": "modelName", "status": True})
