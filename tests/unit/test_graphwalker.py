#    Copyright(C) 2023 Altom Consulting
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <https://www.gnu.org/licenses/>.

import json
import unittest.mock as mock

import pytest

from altwalker.graphwalker import (GraphWalkerClient, GraphWalkerException,
                                   _create_command, _execute_command,
                                   _get_error_message, check, get_version,
                                   methods, offline)

GW_VERSION_OUTPUT = """\
org.graphwalker version: 4.3.3-SNAPSHOT-21bb711

org.graphwalker is open source software licensed under MIT license
The software (and it's source) can be downloaded from http://graphwalker.org
"""


class TestGetErrorMessage:

    @pytest.mark.parametrize(
        "logs",
        [
            "No error message.",
            "[HttpServer] Started"
        ]
    )
    def test_no_error(self, logs):
        assert _get_error_message(logs) is None

    @pytest.mark.parametrize(
        "error_message",
        [
            "No valid generator found.",
            "No valid stop condition found.",
            "Address already in use."
        ]
    )
    def test_for_errors(self, error_message):
        output = f"An error occurred when running command:\n{error_message}\n"
        assert _get_error_message(output) == error_message


class TestCreateCommand:

    @pytest.mark.parametrize(
        "command",
        [
            "check",
            "methods",
            "online",
            "offline"
        ]
    )
    def test_command(self, command):
        has_command_mock = mock.Mock(return_value=True)

        with mock.patch('altwalker.graphwalker.has_command', has_command_mock):
            result = _create_command(command)

        assert has_command_mock.called
        assert ["gw", command] == result

    def test_debug(self):
        has_command_mock = mock.Mock(return_value=True)

        with mock.patch('altwalker.graphwalker.has_command', has_command_mock):
            result = _create_command("offline", debug="OFF")

        assert has_command_mock.called
        assert ["gw", "--debug", "OFF", "offline"] == result

    def test_model_path(self):
        has_command_mock = mock.Mock(return_value=True)

        with mock.patch('altwalker.graphwalker.has_command', has_command_mock):
            result = _create_command("online", model_path="model.json")

        assert has_command_mock.called
        assert ["gw", "online", "--model", "model.json"] == result

    def test_models(self):
        has_command_mock = mock.Mock(return_value=True)
        models = [("model.json", "random(never)")]

        with mock.patch('altwalker.graphwalker.has_command', has_command_mock):
            result = _create_command("online", models=models)

        assert has_command_mock.called
        assert ["gw", "online", "--model", "model.json", "random(never)"] == result

    def test_multiple_models(self):
        has_command_mock = mock.Mock(return_value=True)
        models = [("model_1", "stop_condition_1"), ("model_2", "stop_condition_2")]

        with mock.patch('altwalker.graphwalker.has_command', has_command_mock):
            result = _create_command("online", models=models)

        assert has_command_mock.called
        assert [
            "gw", "online", "--model", "model_1", "stop_condition_1", "--model", "model_2", "stop_condition_2"
        ] == result

    def test_port(self):
        has_command_mock = mock.Mock(return_value=True)
        port = 9999

        with mock.patch('altwalker.graphwalker.has_command', has_command_mock):
            result = _create_command("online", port=port)

        assert has_command_mock.called
        assert ["gw", "online", "--port", str(port)] == result

    def test_service(self):
        has_command_mock = mock.Mock(return_value=True)
        service = "RESTFUL"

        with mock.patch('altwalker.graphwalker.has_command', has_command_mock):
            result = _create_command("online", service=service)

        assert has_command_mock.called
        assert ["gw", "online", "--service", service] == result

    def test_start_element(self):
        has_command_mock = mock.Mock(return_value=True)
        start_element = "start_vertex"

        with mock.patch('altwalker.graphwalker.has_command', has_command_mock):
            result = _create_command("online", start_element=start_element)

        assert has_command_mock.called
        assert ["gw", "online", "--start-element", start_element] == result

    def test_verbose(self):
        result = _create_command("online", verbose=True)
        assert "--verbose" in result

    def test_unvisited(self):
        result = _create_command("online", unvisited=True)
        assert "--unvisited" in result

    @pytest.mark.parametrize(
        "blocked",
        [
            True,
            False,
        ]
    )
    def test_blocked(self, blocked):
        has_command_mock = mock.Mock(return_value=True)

        with mock.patch('altwalker.graphwalker.has_command', has_command_mock):
            result = _create_command("online", blocked=blocked)

        assert has_command_mock.called
        assert ["gw", "online", "--blocked", str(blocked)] == result


@mock.patch("altwalker.graphwalker.execute_command")
class TestExecuteCommand:

    def test_popen(self, execute_command_mock):
        has_command_mock = mock.Mock(return_value=True)
        execute_command_mock.return_value = (b"output", None)

        with mock.patch('altwalker.graphwalker.has_command', has_command_mock):
            _execute_command("offline")

        assert has_command_mock.called
        execute_command_mock.assert_called_once_with(["gw", "offline"])

    def test_error(self, execute_command_mock):
        execute_command_mock.return_value = (None, b"error message")

        with pytest.raises(GraphWalkerException) as excinfo:
            _execute_command("offline")

        assert "error message" in str(excinfo.value)

    def test_output(self, execute_command_mock):
        execute_command_mock.return_value = (b"output", None)

        output = _execute_command("offline")
        assert output == "output"


@mock.patch("altwalker.graphwalker._execute_command")
class TestVersion:

    def test_execute_command(self, command_mock):
        command_mock.return_value = GW_VERSION_OUTPUT

        output = get_version()

        assert output == (4, 3, 3, 'SNAPSHOT', '21bb711')
        command_mock.assert_called_once_with("--version")

    @pytest.mark.parametrize(
        "version_string, version",
        [
            ("org.graphwalker version: 4.3.2-SNAPSHOT-21bb711", (4, 3, 2, 'SNAPSHOT', '21bb711')),
            ("org.graphwalker version: 4.3.2", (4, 3, 2)),
            ("org.graphwalker version: 4.1", (4, 1)),
            ("org.graphwalker version: 3.1.8", (3, 1, 8))
        ]
    )
    def test_get_version(self, command_mock, version_string, version):
        command_mock.return_value = version_string

        output = get_version()

        assert output == version
        command_mock.assert_called_once_with("--version")


@mock.patch("altwalker.graphwalker._execute_command")
class TestOffline:

    def test_execute_command(self, command_mock):
        models = [("model_path", "stop_condition")]
        offline(models, start_element="start_element", unvisited=True, blocked=True)

        command_mock.assert_called_once_with(
            "offline",
            models=models,
            start_element="start_element",
            verbose=True,
            unvisited=True,
            blocked=True
        )

    def test_step(self, command_mock):
        output = json.dumps({
            "currentElementID": "v0",
            "currentElementName": "start_vertex",
            "modelName": "Example",
            "data": {},
            "properties": []
        })

        command_mock.return_value = output

        step = {
            "id": "v0",
            "name": "start_vertex",
            "modelName": "Example"
        }

        steps = offline(mock.sentinel.models)
        assert steps == [step]

    def test_steps(self, command_mock):
        output = json.dumps({
            "currentElementID": "v0",
            "currentElementName": "start_vertex",
            "modelName": "Example",
            "data": {},
            "properties": []
        })

        command_mock.return_value = f"{output}\n{output}\n"

        step = {
            "id": "v0",
            "name": "start_vertex",
            "modelName": "Example"
        }

        steps = offline(mock.sentinel.models)
        assert steps == [step, step]

    def test_verbose(self, command_mock):
        output = json.dumps({
            "currentElementID": "v0",
            "currentElementName": "start_vertex",
            "modelName": "Example",
            "data": {},
            "properties": []
        })

        command_mock.return_value = output

        step = {
            "id": "v0",
            "name": "start_vertex",
            "modelName": "Example",
            "data": {},
            "properties": []
        }

        steps = offline(mock.sentinel.models, verbose=True)
        assert steps == [step]


@mock.patch("altwalker.graphwalker._execute_command")
class TestCheck:

    def test_execute_command(self, command_mock):
        models = [("model_path", "stop_condition")]
        check(models, blocked=True)

        command_mock.assert_called_once_with("check", models=models, blocked=True)


@mock.patch("altwalker.graphwalker._execute_command")
class TestMethods:

    def test_execute_command(self, command_mock):
        model_path = "model_path"
        methods(model_path, blocked=True)

        command_mock.assert_called_once_with("methods", model_path=model_path, blocked=True)

    @pytest.mark.parametrize(
        "output, expected",
        [
            ("", []),
            ("step_A\n", ["step_A"]),
            ("step_A\nstep_B\n", ["step_A", "step_B"]),
            ("step_A\nstep_B\nstep_C\n", ["step_A", "step_B", "step_C"]),
        ]
    )
    def test_methods(self, command_mock, output, expected):
        command_mock.return_value = output
        result = methods(mock.sentinel.model_path, blocked=True)

        assert result == expected


class TestGraphWalkerClient:

    @pytest.fixture(autouse=True)
    def graphwalker_client(self):
        self.client = GraphWalkerClient(host="1.2.3.4", port="9999")

    def test_init(self):
        assert self.client.base == "http://1.2.3.4:9999/graphwalker"

    @pytest.mark.parametrize(
        "message, expected",
        [
            (
                "",
                "Unknown%20error."
            ),
            (
                "Error message.",
                "Error%20message."
            ),
            (
                "Error message with URL: http://example.com/of/url",
                "Error%20message%20with%20URL%3A%20http%3A%2F%2Fexample.com%2Fof%2Furl"
            ),
            (
                "Special charaters that should be encoded: $&+,/:;=?@<>#%",
                "Special%20charaters%20that%20should%20be%20encoded%3A%20%24%26%2B%2C%2F%3A%3B%3D%3F%40%3C%3E%23%25"
            )
        ]
    )
    def test_normalize_fail_message(self, message, expected):
        assert self.client._normalize_fail_message(message) == expected

    def test_validate_response(self):
        response = mock.Mock()

        # Should not raise exception for status code 200
        response.status_code = 200
        self.client._validate_response(response)

        # Should raise exception for any other status exept 200
        response.status_code = 404

        with pytest.raises(GraphWalkerException) as excinfo:
            self.client._validate_response(response)

        assert "GraphWalker responded with status code: 404." == str(excinfo.value)

    def test_get_body(self):
        body = mock.Mock()
        body.json.return_value = {"result": "ok", "data": "data"}

        assert self.client._get_body(body) == {"data": "data"}

    @pytest.mark.parametrize(
        "response, error",
        [
            ({"result": ""}, "GraphWalker did not respond with an ok status."),
            ({"result": "nok"}, "GraphWalker responded with an nok status."),
            ({"result": "nok", "error": "error message"}, "GraphWalker responded with the error: error message.")
        ]
    )
    def test_get_body_error(self, response, error):
        body = mock.Mock()
        body.json.return_value = response

        with pytest.raises(GraphWalkerException) as excinfo:
            self.client._get_body(body)

        assert error == str(excinfo.value)

    def test_get_next(self):
        self.client._get = mock.Mock(return_value={
            "currentElementID": "v0",
            "currentElementName": "start_vertex",
            "modelName": "Example",
            "data": {},
            "properties": []
        })

        expected = {
            "id": "v0",
            "name": "start_vertex",
            "modelName": "Example"
        }
        step = self.client.get_next()

        assert step == expected

    def test_get_next_verbose(self):
        self.client.verbose = True
        self.client._get = mock.Mock(return_value={
            "currentElementID": "v0",
            "currentElementName": "start_vertex",
            "modelName": "Example",
            "data": {},
            "properties": []
        })

        expected = {
            "id": "v0",
            "name": "start_vertex",
            "modelName": "Example",
            "data": {},
            "properties": []
        }
        step = self.client.get_next()

        assert step == expected

    @pytest.mark.parametrize(
        "key, value, url",
        [
            ("isUserLoggedIn", True, "/setData/isUserLoggedIn=true"),
            ("isUserLoggedIn", False, "/setData/isUserLoggedIn=false"),
            ("count", 0, "/setData/count=0"),
            ("count", 1, "/setData/count=1"),
            ("count", -1, "/setData/count=-1"),
            ("count", 1.33, "/setData/count=1.33"),
            ("string", "abc", "/setData/string=%22abc%22"),
            ("message", "Test mesasge.", "/setData/message=%22Test%20mesasge.%22"),
            ("url", "url/example/", "/setData/url=%22url%2Fexample%2F%22"),
        ]
    )
    def test_set_data(self, key, value, url):
        self.client._put = mock.Mock()

        self.client.set_data(key, value)
        self.client._put.assert_called_once_with(url)
