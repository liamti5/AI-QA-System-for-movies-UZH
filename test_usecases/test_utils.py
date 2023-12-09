import unittest
from usecases import utils


class TestUtils(unittest.TestCase):
    def test_dicti_nodes(self):
        expected_value = dict
        actual_value = type(utils.get_dicti("data/nodes.json"))
        self.assertEqual(actual_value, expected_value)

    def test_dicti_preds(self):
        expected_value = dict
        actual_value = type(utils.get_dicti("data/predicates_clean.json"))
        self.assertEqual(actual_value, expected_value)


if __name__ == "__main__":
    unittest.main()
