import unittest
import unittest.mock as mock

from altwalker.planner import OnlinePlanner, OfflinePlanner


class TestOnlinePlanner(unittest.TestCase):

    def setUp(self):
        self.service = mock.MagicMock()
        self.client = mock.MagicMock()

        self.planner = OnlinePlanner(self.service, self.client)

    def setModels(self):
        self.planner.models = {
            "name": "Name",
            "models": [
                {
                    "name": "ModelName",
                    "vertices": [
                        {
                            "id": "0",
                            "name": "VertexA"
                        },
                        {
                            "id": "1",
                            "name": "VertexB"
                        }
                    ],
                    "edges": [
                        {
                            "id": "3",
                            "name": "EdgeA",
                            "sourceVertexId": "0",
                            "targetVertexId": "1"
                        },
                        {
                            "id": "4",
                            "name": "EdgeB",
                            "targetVertexId": "1"
                        }
                    ]
                }
            ]
        }

    def test_init(self):
        self.assertEqual(self.planner.steps, [])
        self.assertEqual(self.planner.failed_step, {})
        self.assertEqual(self.planner.failed_fixtures, [])

    def test_kill(self):
        self.planner.kill()

        # Should call the kill method from the service
        self.service.kill.assert_called_once_with()

    def test_restart(self):
        self.planner.restart()

        # Should call the restart method from the client
        self.client.restart.assert_called_once_with()
        self.assertDictEqual(self.planner.failed_step, {})
        self.assertListEqual(self.planner.failed_fixtures, [])

    def test_load(self):
        models = {
            "name": "Name",
            "models": [
                {
                    "name": "ModelName",
                    "vertices": [],
                    "edges": []
                }
            ]
        }

        self.planner.load(models)

        # Should call the load method from the client
        self.client.load.assert_called_once_with(models)

    def test_get_data(self):
        self.planner.get_data()

        # Should call the get_data method from the client
        self.client.get_data.assert_called_once_with()

    def test_set_data(self):
        self.planner.set_data("key", "value")

        # Should call the set_data method from the cleint
        self.client.set_data.assert_called_once_with("key", "value")

    def test_get_statistics(self):
        self.planner.get_statistics()

        # Should call the get_statistics method from the client
        self.client.get_statistics.assert_called_once_with()

    def test_get_statistics_steps(self):
        # Should add the steps to the statistics
        self.client.get_statistics.return_value = {}

        steps = [{"id": 1, "name": "vertexName"}]
        self.planner.steps = steps

        self.assertEqual(self.planner.get_statistics(), {"steps": steps, "failedStep": {}, "failedFixtures": []})

    def test_get_statistics_failed_step(self):
        # Should add the failed_step to the statistics
        self.client.get_statistics.return_value = {}

        failed_step = {"id": 1, "name": "vertexName", "modelName": "ModelName"}
        self.planner.failed_step = failed_step

        self.assertEqual(self.planner.get_statistics(), {"steps": [], "failedStep": failed_step, "failedFixtures": []})

    def test_get_statistics_failed_fixtures(self):
        # Should add the failed_fixtures to the statistics
        self.client.get_statistics.return_value = {}

        failed_fixtures = [{"name": "setUpModel", "modelName": "ModelName"}]
        self.planner.failed_fixtures = failed_fixtures

        self.assertEqual(
            self.planner.get_statistics(),
            {"steps": [], "failedStep": {}, "failedFixtures": failed_fixtures})

    def test_fail_on_step(self):
        step = {
            "id": "0",
            "name": "VertexA",
            "modelName": "ModelName"
        }

        self.setModels()
        self.planner.fail(step, "error message")

        # Should call the fail method from the client
        self.client.fail.assert_called_once_with("error message")

        # Should set the failed_step attribute
        self.assertDictEqual(self.planner.failed_step, step)

    def test_fail_on_setUpRun(self):
        self.setModels()
        self.planner.fail({"type": "fixture", "name": "setUpRun"}, "error message")

        # Should call the fail method from the client
        self.client.fail.assert_called_once_with("error message")

        # Should set the fail
        expected = {
            "type": "fixture",
            "name": "setUpRun"
        }

        self.assertDictEqual(self.planner.failed_step, {})
        self.assertEqual(self.planner.failed_fixtures, [expected])

    def test_fail_on_setUpModel(self):
        self.setModels()
        self.planner.fail({"type": "fixture", "name": "setUpModel", "modelName": "ModelName"}, "error message")

        # Should call the fail method from the client
        self.client.fail.assert_called_once_with("error message")

        # Should set the fail
        expected = {
            "type": "fixture",
            "name": "setUpModel",
            "modelName": "ModelName"
        }

        self.assertDictEqual(self.planner.failed_step, {})
        self.assertEqual(self.planner.failed_fixtures, [expected])

    def test_has_next(self):
        self.planner.has_next()

        # Should call the has_next method from the client
        self.client.has_next.assert_called_once_with()

    def test_get_next(self):
        self.setModels()

        step = {
            "id": "3",
            "name": "EdgeA",
            "modelName": "ModelName"
        }
        self.client.get_next.return_value = step

        actual_step = self.planner.get_next()

        # Sould call the get_next method from the client
        self.client.get_next.assert_called_once_with()

        # The steps should be correct and in the steps list
        self.assertDictEqual(actual_step, step)
        self.assertLessEqual(self.planner.steps, [step])


class TestOfflinePlanner(unittest.TestCase):

    def setUp(self):
        self.vertex = {
            "id": "v0",
            "name": "vertex_name",
            "modelName": "ModelName"
        }

        self.edge = {
            "id": "e0",
            "name": "eadge_name",
            "modelName": "ModelName"
        }

        self.steps = [self.vertex if x % 2 == 0 else self.edge for x in range(4)]
        self.planner = OfflinePlanner(self.steps)

    def test_init(self):
        self.assertDictEqual(self.planner.failed_step, {})
        self.assertListEqual(self.planner.failed_fixtures, [])
        self.assertListEqual(self.planner.path, self.steps)

    def test_get_data(self):
        data = self.planner.get_data()
        self.assertDictEqual(data, {})

    def test_set_data(self):
        message = "The set_data and get_data are not supported in offline mode so calls to them have no effect."
        with self.assertWarnsRegex(UserWarning, message):
            self.planner.set_data("key", "value")

    def test_has_next(self):
        self.assertTrue(self.planner.has_next())

        self.planner._position = len(self.steps)
        self.assertFalse(self.planner.has_next())

    def test_get_next(self):
        self.assertDictEqual(self.planner.get_next(), self.vertex)
        self.assertDictEqual(self.planner.get_next(), self.edge)

    def test_fail(self):
        self.planner.fail(self.vertex, "Error message")
        self.assertDictEqual(self.planner.failed_step, self.vertex)

        self.planner.fail({"name": "setUpRun"}, "Error message")
        self.assertListEqual(self.planner.failed_fixtures, [{"name": "setUpRun"}])

    def test_restart(self):
        self.planner.fail(self.vertex, "Error message")
        self.planner.fail({"name": "setUpRun"}, "Error message")

        self.planner._position = len(self.steps)
        self.planner.restart()

        self.assertTrue(self.planner.has_next)
        self.assertDictEqual(self.planner.failed_step, {})
        self.assertListEqual(self.planner.failed_fixtures, [])

    def test_get_statistics(self):
        self.assertIn("failedStep", self.planner.get_statistics())
        self.assertIn("failedFixtures", self.planner.get_statistics())
        self.assertIn("steps", self.planner.get_statistics())

    def test_steps(self):
        expected_steps = []
        self.assertListEqual(self.planner.steps, expected_steps)

        expected_steps.append(self.planner.get_next())
        self.assertListEqual(self.planner.steps, expected_steps)

    def test_path(self):
        new_path = [self.vertex if x % 2 == 0 else self.edge for x in range(2)]
        self.planner.path = new_path

        self.assertListEqual(self.planner.path, new_path)
        self.assertTrue(self.planner.has_next)
        self.assertDictEqual(self.planner.failed_step, {})
        self.assertListEqual(self.planner.failed_fixtures, [])
