import subprocess
import unittest
import unittest.mock as mock
import platform

from altwalker.graphwalker import GraphWalkerException, GraphWalkerClient, _create_command, \
    _execute_command, offline, methods, check


class TestGraphWalkerClient(unittest.TestCase):

    def setUp(self):
        self.client = GraphWalkerClient(host="1.2.3.4", port="9999")

    def test_init(self):
        self.assertEqual(self.client.base, "http://1.2.3.4:9999/graphwalker")

    def test_validate_response(self):
        response = mock.MagicMock()

        # Should not raise exception for status code 200
        response.status_code = 200
        self.client._validate_response(response)

        # Should raise exception for any other status exept 200
        response.status_code = 404

        with self.assertRaises(GraphWalkerException) as error:
            self.client._validate_response(response)

        self.assertEqual(str(error.exception), "GraphWalker responded with status code: 404.")

    def test_get_body(self):
        body = mock.MagicMock()

        # Should return the rest of the body if result is ok
        body.json.return_value = {"result": "ok", "data": "data"}

        self.assertEqual(self.client._get_body(body), {"data": "data"})

        # Should raise exception if the error key is present
        body.json.return_value = {"result": "nok", "error": "error message"}

        with self.assertRaises(GraphWalkerException) as error:
            self.client._get_body(body)

        self.assertEqual(str(error.exception), "GraphWalker responded with the error: error message.")

        # Should raise exception if no error key and the result is nok
        body.json.return_value = {"result": "nok"}

        with self.assertRaises(GraphWalkerException) as error:
            self.client._get_body(body)

        self.assertEqual(str(error.exception), "GraphWalker responded with an nok status.")

        # Should raise exception if no error key and the result is neither ok nor nok
        body.json.return_value = {"result": ""}

        with self.assertRaises(GraphWalkerException) as error:
            self.client._get_body(body)

        self.assertEqual(str(error.exception), "GraphWalker did not respond with an ok status.")

    def test_set_data(self):
        self.client._put = mock.MagicMock()

        self.client.set_data("key", 1)
        self.client._put.assert_called_once_with("/setData/key=1")

    def test_set_data_true(self):
        self.client._put = mock.MagicMock()

        self.client.set_data("key", True)
        self.client._put.assert_called_once_with("/setData/key=true")

    def test_set_data_false(self):
        self.client._put = mock.MagicMock()

        self.client.set_data("key", False)
        self.client._put.assert_called_once_with("/setData/key=false")

    def test_set_data_str(self):
        self.client._put = mock.MagicMock()

        self.client.set_data("key", "str")
        self.client._put.assert_called_once_with("/setData/key=%22str%22")


@mock.patch("altwalker._utils.get_command", side_effect=lambda command: [command])
class TestCreateCommand(unittest.TestCase):

    def test_method(self, get_gw):
        command = _create_command("online")
        self.assertEqual(command[1], "online")

    def test_model_path(self, get_gw):
        command = _create_command("online", model_path="model_path")
        self.assertListEqual(["--model", "model_path"], command[2:])

    def test_models(self, get_gw):
        command = _create_command("online")
        self.assertNotIn("--model", command)

        models = [("model_path", "stop_condition")]
        command = _create_command("online", models=models)
        self.assertListEqual(["--model", "model_path", "stop_condition"], command[2:])

        models = [("model_path_1", "stop_condition_1"), ("model_path_2", "stop_condition_2")]
        command = _create_command("online", models=models)

        self.assertListEqual(
            ["--model", "model_path_1", "stop_condition_1", "--model", "model_path_2", "stop_condition_2"],
            command[2:])

    def test_port(self, get_gw):
        command = _create_command("online")
        self.assertNotIn("--port", command)

        port = 9999
        command = _create_command("online", port=port)
        self.assertListEqual(["--port", str(port)], command[2:])

    def test_service(self, get_gw):
        command = _create_command("online")
        self.assertNotIn("--service", command)

        service = "RESTFUL"
        command = _create_command("online", service=service)
        self.assertListEqual(["--service", service], command[2:])

    def test_start_element(self, get_gw):
        command = _create_command("online")
        self.assertNotIn("--start-element", command)

        start_element = "start_vertex"
        command = _create_command("online", start_element=start_element)
        self.assertListEqual(["--start-element", start_element], command[2:])

    def test_verbose(self, get_gw):
        command = _create_command("online")
        self.assertNotIn("--verbose", command)

        command = _create_command("online", verbose=True)
        self.assertIn("--verbose", command)

    def test_unvisited(self, get_gw):
        command = _create_command("online")
        self.assertNotIn("--unvisited", command)

        command = _create_command("online", unvisited=True)
        self.assertIn("--unvisited", command)

    def test_blocked(self, get_gw):
        command = _create_command("online")
        self.assertNotIn("--blocked", command)

        command = _create_command("online", blocked=False)
        self.assertIn("--blocked", command)
        self.assertIn("False", command)

        command = _create_command("online", blocked=True)
        self.assertIn("--blocked", command)
        self.assertIn("True", command)


@mock.patch("subprocess.Popen")
class TestExecuteCommand(unittest.TestCase):

    def test_popen(self, popen_mock):
        popen_mock.return_value.communicate.return_value = (b"output", None)

        _execute_command("offline")

        if platform.system() == "Windows":
            popen_mock.assert_called_once_with(
                ["cmd.exe", "/C", "gw", "offline"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        else:
            popen_mock.assert_called_once_with(
                ["gw", "offline"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

    def test_error(self, popen_mock):
        popen_mock.return_value.communicate.return_value = (None, b"error message")

        with self.assertRaisesRegex(GraphWalkerException, "GraphWalker responded with the error: `error message`."):
            _execute_command("offline")

    def test_output(self, popen_mock):
        popen_mock.return_value.communicate.return_value = (b"output", None)

        output = _execute_command("offline")
        self.assertEqual(output, "output")


@mock.patch("altwalker.graphwalker._execute_command")
class TestOffline(unittest.TestCase):

    def test_execute_command(self, command_mock):
        models = [("model_path", "stop_condition")]
        offline(models, start_element="start_element", unvisited=True, blocked=True)

        command_mock.assert_called_once_with(
            "offline",
            models=models,
            start_element="start_element",
            verbose=True,
            unvisited=True,
            blocked=True)

    def test_step(self, command_mock):
        output = "{" \
            '"modelName": "Example",' \
            '"data": [],' \
            '"currentElementID": "v0",' \
            '"currentElementName": "start_vertex",' \
            '"properties": []' \
            "}"

        command_mock.return_value = output

        step = {"name": "start_vertex", "modelName": "Example", "id": "v0"}

        steps = offline([])
        self.assertListEqual(steps, [step])

    def test_steps(self, command_mock):
        output = "{" \
            '"modelName": "Example",' \
            '"data": [],' \
            '"currentElementID": "v0",' \
            '"currentElementName": "start_vertex",' \
            '"properties": []' \
            "}"

        command_mock.return_value = output + "\n" + output + "\n"

        step = {"name": "start_vertex", "modelName": "Example", "id": "v0"}

        steps = offline([])
        self.assertListEqual(steps, [step, step])

    def test_verbose(self, command_mock):
        output = "{" \
            '"modelName": "Example",' \
            '"data": [],' \
            '"currentElementID": "v0",' \
            '"currentElementName": "start_vertex",' \
            '"properties": []' \
            "}"

        command_mock.return_value = output

        step = {"name": "start_vertex", "modelName": "Example", "id": "v0", "data": {}, "properties": []}

        steps = offline([], verbose=True)
        self.assertListEqual(steps, [step])


@mock.patch("altwalker.graphwalker._execute_command")
class TestCheck(unittest.TestCase):

    def test_execute_command(self, command_mock):
        models = [("model_path", "stop_condition")]
        check(models, blocked=True)

        command_mock.assert_called_once_with("check", models=models, blocked=True)


@mock.patch("altwalker.graphwalker._execute_command")
class TestMethods(unittest.TestCase):

    def test_execute_command(self, command_mock):
        model_path = "model_path"
        methods(model_path, blocked=True)

        command_mock.assert_called_once_with("methods", model_path=model_path, blocked=True)

    def test_methods(self, command_mock):
        model_path = "model_path"
        command_mock.return_value = """step_A\nstep_B\nstep_C\n"""

        output = methods(model_path, blocked=True)

        self.assertListEqual(output, ["step_A", "step_B", "step_C"])
