import json
import os

import pytest
import requests

from altwalker.graphwalker import check, methods, offline, GraphWalkerException, GraphWalkerClient, GraphWalkerService


pytestmark = pytest.mark.graphwalker

os.environ["GRAPHWALKER_LOG_LEVEL"] = "DEBUG"


class TestGraphWalkerService:

    def test_create(self):
        service = GraphWalkerService(port=9001)

        try:
            response = requests.get(
                "http://127.0.0.1:9001/graphwalker/getStatistics")
            assert response.status_code == 200
        except Exception:
            assert False
        finally:
            service.kill()

    def test_kill(self):
        service = GraphWalkerService(port=9001)
        service.kill()

        with pytest.raises(requests.exceptions.ConnectionError):
            requests.get("http://127.0.0.1:9001/graphwalker/getStatistics")

    def test_address_already_in_use(self):
        service = GraphWalkerService(port=9001)

        with pytest.raises(GraphWalkerException) as excinfo:
            GraphWalkerService(port=9001)

        assert "An error occurred while trying to start the GraphWalker Service on port" in str(excinfo.value)
        assert "Address already in use" in str(excinfo.value)

        service.kill()

    def test_invalid_generator(self):
        with pytest.raises(GraphWalkerException) as excinfo:
            GraphWalkerService(models=[("tests/common/models/shop.json", "invalid_generator(never)")])

        assert "An error occurred while trying to start the GraphWalker Service on port" in str(excinfo.value)
        assert "No suitable generator found with name:" in str(excinfo.value)

    def test_invalid_stop_condition(self):
        with pytest.raises(GraphWalkerException) as excinfo:
            GraphWalkerService(models=[("tests/common/models/shop.json", "random(invalid_stop_condition)")])

        assert "An error occurred while trying to start the GraphWalker Service on port" in str(excinfo.value)
        assert "No valid stop condition found." in str(excinfo.value)

    def test_logs(self):
        output_file = "graphwalker-test.log"
        service = GraphWalkerService(port=9001, output_file=output_file)
        service.kill()

        with open(output_file, "r") as fp:
            assert "[HttpServer] Started" in fp.read()

        os.remove(output_file)


class TestGraphWalkerClient:

    @pytest.fixture(autouse=True)
    def graphwalker_client(self):
        self.service = GraphWalkerService()
        self.client = GraphWalkerClient()

        with open('tests/common/models/shop.json') as file:
            data = json.load(file)

        self.client.load(data)

        yield

        self.service.kill()

    def test_load(self):
        with open('tests/common/models/shop.json') as file:
            data = json.load(file)

        self.client.load(data)

    def test_load_for_invalid_model(self):
        with open('tests/common/models/invalid.json') as file:
            data = json.load(file)

        with pytest.raises(GraphWalkerException):
            self.client.load(data)

    def test_has_next(self):
        assert self.client.has_next()

    def test_get_next(self):
        next_element = self.client.get_next()

        assert "modelName" in next_element
        assert "name" in next_element
        assert "id" in next_element

    def test_get_data(self):
        data = self.client.get_data()
        assert isinstance(data, dict)

    @pytest.mark.parametrize(
        "key, value, expected",
        [
            ("isUserLoggedIn", True, "true"),
            ("isUserLoggedIn", False, "false"),
            ("message", "Test message.", "Test message."),
            ("url", "url/example/", "url/example/"),
            ("count", 0, "0"),
            ("count", 1, "1"),
            ("count", 1.33, "1.33"),
            ("count", -1, "-1")
        ]
    )
    def test_set_data(self, key, value, expected):
        self.client.set_data(key, value)
        data = self.client.get_data()

        assert data[key] == expected

    @pytest.mark.skip(reason="Global attributes are broken in GraphWalker 4.3.1")
    @pytest.mark.parametrize(
        "key, value",
        [
            ("global.isUserLoggedIn", True),
            ("global.isUserLoggedIn", False),
            ("global.message", "Test message."),
            ("global.url", "url/example/"),
            ("global.count", 0),
            ("global.count", 1),
            ("global.count", 1.33),
            ("global.count", -1)
        ]
    )
    def test_set_global_data(self, key, value):
        self.client.set_data(key, value)

    def test_restart(self):
        while self.client.has_next():
            self.client.get_next()

        self.client.restart()
        assert self.client.has_next()

    def test_restart_empty_path(self):
        self.client.restart()

    def test_get_statistics(self):
        statistics = self.client.get_statistics()
        assert isinstance(statistics, dict)

    @pytest.mark.parametrize(
        "error_message",
        [
            "",
            "Error message.",
            "Error message with URL: http://example.com/of/url",
            "Special charaters that should be encoded: $&+,/:;=?@<>#%{}|[]^~`"
        ]
    )
    def test_fail(self, error_message):
        self.client.get_next()
        self.client.fail(error_message)

        statistics = self.client.get_statistics()
        assert statistics["totalFailedNumberOfModels"] == 1

    def test_for_inexistent_route(self):
        with pytest.raises(GraphWalkerException):
            self.client._get('/inexistent')


class TestCheck:

    @pytest.mark.parametrize(
        "models",
        [
            [('tests/common/models/simple.json', 'random(never)')],
            [('tests/common/models/simple.json', 'quick_random(vertex_coverage(100))')],
            [('tests/common/models/complex.json', 'random(never)')],
            [('tests/common/models/complex.json', 'quick_random(vertex_coverage(100))')],
            [('tests/common/models/shop.json', 'random(never)')],
            [('tests/common/models/shop.json', 'quick_random(vertex_coverage(100))')],
        ]
    )
    def test_valid_input(self, models):
        output = check(models, blocked=False)
        assert output == "No issues found with the model(s).\n"

    @pytest.mark.parametrize(
        "models, error_message",
        [
            (
                [('tests/common/models/simple.json', 'invalid_generator(never)')],
                "No suitable generator found with name: invalid_generator"
            ),
            (
                [('tests/common/models/simple.json', 'random(invalid_stop_condition)')],
                "No valid stop condition found."
            ),
            (
                [('tests/common/models/no-models.json', 'random(never)')],
                None
            ),
            (
                [('tests/common/models/no-name.json', 'random(never)')],
                None
            )
        ]
    )
    def test_invalid_input(self, models, error_message):
        with pytest.raises(GraphWalkerException) as excinfo:
            check(models, blocked=False)

        if error_message:
            assert error_message in str(excinfo.value)


class TestMethods:

    @pytest.mark.parametrize(
        "models_path, expected",
        [
            (
                'tests/common/models/simple.json',
                ['vertex_a', 'vertex_b', 'edge_a', 'edge_b']
            ),
            (
                'tests/common/models/complex.json',
                ['vertex_a', 'vertex_b', 'vertex_c', 'vertex_d', 'vertex_e', 'edge_a', 'edge_b', 'edge_c']
            ),
            (
                'tests/common/models/no-models.json',
                []
            ),
            (
                'tests/common/models/no-name.json',
                []
            )
        ]
    )
    def test_valid_input(self, models_path, expected):
        result = methods(models_path)
        assert set(result) == set(expected)


class TestOffline:

    @pytest.mark.parametrize(
        "models, expected",
        [
            (
                [('tests/common/models/simple.json', 'random(vertex_coverage(100))')],
                [
                    {'id': 'v0', 'modelName': 'Simple', 'name': 'vertex_a'},
                    {'id': 'e0', 'modelName': 'Simple', 'name': 'edge_a'},
                    {'id': 'v1', 'modelName': 'Simple', 'name': 'vertex_b'}
                ]
            ),
            (
                [('tests/common/models/complex.json', 'random(length(3))')],
                [
                    {'id': 'v0', 'modelName': 'ComplexA', 'name': 'vertex_a'},
                    {'id': 'e0', 'modelName': 'ComplexA', 'name': 'edge_a'},
                    {'id': 'v1', 'modelName': 'ComplexA', 'name': 'vertex_b'},
                    {'id': 'e1', 'modelName': 'ComplexA', 'name': 'edge_b'},
                    {'id': 'v2', 'modelName': 'ComplexA', 'name': 'vertex_c'},
                    {'id': 'v3', 'modelName': 'ComplexB', 'name': 'vertex_d'},
                    {'id': 'e2', 'modelName': 'ComplexB', 'name': 'edge_c'},
                    {'id': 'v4', 'modelName': 'ComplexB', 'name': 'vertex_e'},
                ]
            )
        ]
    )
    def test_valid_input(self, models, expected):
        path = offline(models)
        assert path == expected

    @pytest.mark.parametrize(
        "models, error_message",
        [
            (
                [('tests/common/models/simple.json', 'invalid_generator(never)')],
                "No suitable generator found with name: invalid_generator"
            ),
            (
                [('tests/common/models/simple.json', 'random(invalid_stop_condition)')],
                "No valid stop condition found."
            ),
            (
                [('tests/common/models/no-models.json', 'random(length(3))')],
                None
            ),
            (
                [('tests/common/models/no-name.json', 'random(length(3))')],
                None
            )
        ]
    )
    def test_invalid_input(self, models, error_message):
        with pytest.raises(GraphWalkerException) as excinfo:
            offline(models)

        if error_message:
            assert error_message in str(excinfo.value)
