import json
import os

import requests
import unittest


from altwalker.graphwalker import GraphWalkerException, GraphWalkerClient, GraphWalkerService


class TestGraphWalkerService(unittest.TestCase):

    def test_create(self):
        service = GraphWalkerService(port=9001)

        try:
            response = requests.get(
                "http://127.0.0.1:9001/graphwalker/getStatistics")
            self.assertEqual(response.status_code, 200)
        except Exception:
            self.assertTrue(False)
        finally:
            service.kill()

    def test_kill(self):
        service = GraphWalkerService(port=9001)
        service.kill()

        with self.assertRaises(requests.exceptions.ConnectionError):
            requests.get("http://127.0.0.1:9001/graphwalker/getStatistics")

    def test_address_already_in_use(self):
        service = GraphWalkerService(port=9001)

        with self.assertRaises(GraphWalkerException) as context:
            GraphWalkerService(port=9001)

        self.assertIn("Could not start GraphWalker Service", str(context.exception))

        service.kill()

    def test_logs(self):
        output_file = "graphwalker-test.log"
        service = GraphWalkerService(port=9001, output_file=output_file)
        service.kill()

        with open(output_file, "r") as fp:
            self.assertIn("[HttpServer] Started", fp.read())

        os.remove(output_file)


class TestGraphWalkerClient(unittest.TestCase):

    def setUp(self):
        self.service = GraphWalkerService()
        self.client = GraphWalkerClient()

        with open('tests/common/models/shop.json') as file:
            data = json.load(file)

        self.client.load(data)

    def tearDown(self):
        self.service.kill()

    def test_load(self):
        with open('tests/common/models/shop.json') as file:
            data = json.load(file)

        self.client.load(data)

    def test_load_for_invalid_model(self):
        with open('tests/common/models/invalid.json') as file:
            data = json.load(file)

        with self.assertRaises(GraphWalkerException):
            self.client.load(data)

    def test_has_next(self):
        self.assertTrue(self.client.has_next())

    def test_get_next(self):
        next_element = self.client.get_next()

        self.assertTrue("modelName" in next_element)
        self.assertTrue("name" in next_element)
        self.assertTrue("id" in next_element)

    def test_get_data(self):
        data = self.client.get_data()
        self.assertTrue(isinstance(data, dict))

    def test_set_data_to_true(self):
        self.client.set_data("validLogin", True)
        self.assertEqual(self.client.get_data()["validLogin"], "true")

    def test_set_data_to_false(self):
        self.client.set_data("validLogin", False)
        self.assertEqual(self.client.get_data()["validLogin"], "false")

    def test_set_data_to_str(self):
        self.client.set_data("message", "value")
        self.assertEqual(self.client.get_data()["message"], "value")

    def test_set_data_to_int(self):
        self.client.set_data("count", 1)
        self.assertEqual(self.client.get_data()["count"], "1")

    def test_set_data_with_special_characters(self):
        self.client.set_data("url", "url/example/")
        self.assertEqual(self.client.get_data()["url"], "url/example/")

    def test_restart(self):
        while self.client.has_next():
            self.client.get_next()

        self.client.restart()
        self.assertTrue(self.client.has_next())

    def test_restart_empty_parth(self):
        self.client.restart()

    def test_get_statistics(self):
        statistics = self.client.get_statistics()
        self.assertTrue(isinstance(statistics, dict))

    def test_fail(self):
        self.client.get_next()

        self.client.fail("Error message.")
        self.assertEqual(self.client.get_statistics()[
                         "totalFailedNumberOfModels"], 1)

    def test_fail_with_special_characters(self):
        self.client.get_next()

        self.client.fail("Error message with url: example/of/url")
        self.assertEqual(self.client.get_statistics()[
                         "totalFailedNumberOfModels"], 1)

    def test_fail_with_no_message(self):
        self.client.get_next()

        self.client.fail("")
        self.assertEqual(self.client.get_statistics()[
                         "totalFailedNumberOfModels"], 1)

    def test_for_inexistent_route(self):
        with self.assertRaises(GraphWalkerException):
            self.client._get('/inexistent')
