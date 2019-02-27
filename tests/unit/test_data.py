import unittest
import unittest.mock as mock


from altwalker.data import GraphData


class TestGraphData(unittest.TestCase):

    def setUp(self):
        self.planner = mock.MagicMock()
        self.data = GraphData(self.planner)

    def test_set(self):
        self.data.set("key", "value")

        self.planner.set_data.assert_called_once_with("key", "value")

    def test_set_dict(self):
        self.data.set({"key1": "value", "key2": "value"})

        self.assertEqual(self.planner.set_data.call_count, 2)

        self.planner.set_data.assert_any_call("key1", "value")
        self.planner.set_data.assert_any_call("key2", "value")

    def test_set_kargs(self):
        self.data.set(key1="value", key2="value")

        self.assertEqual(self.planner.set_data.call_count, 2)

        self.planner.set_data.assert_any_call("key1", "value")
        self.planner.set_data.assert_any_call("key2", "value")

        self.data.set()

    def test_setitem(self):
        self.data["key1"] = "value"

        self.planner.set_data.assert_called_once_with("key1", "value")

    def test_get(self):
        self.planner.get_data.return_value = {"key": "value"}

        data = self.data.get()

        self.assertDictEqual(data, {"key": "value"})
        self.planner.get_data.assert_called_once_with()

    def test_get_arg(self):
        self.planner.get_data.return_value = {"key1": "value1", "key2": "value2", "key3": "value3"}

        value = self.data.get("key1")

        self.assertEqual(value, "value1")
        self.planner.get_data.assert_called_once_with()

    def test_get_args(self):
        self.planner.get_data.return_value = {"key1": "value", "key2": "value", "key3": "value"}

        data = self.data.get("key1", "key3")

        self.assertDictEqual(data, {"key1": "value", "key3": "value"})
        self.planner.get_data.assert_called_once_with()

    def test_getitem(self):
        self.planner.get_data.return_value = {"key1": "value1", "key2": "value2", "key3": "value3"}

        value = self.data["key1"]

        self.assertEqual(value, "value1")
        self.planner.get_data.assert_called_once_with()
