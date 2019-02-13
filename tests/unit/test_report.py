import unittest

from altwalker.reporter import _add_timestamp, _format_step, _format_step_info


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
