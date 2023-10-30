import unittest
from usecases import nlp_operations


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nlp_operator = nlp_operations.NLP_Operations()

    def test_get_ner_all_O(self):
        expected_value = [['O', 'O', 'O', 'O', 'O']]
        actual_value = self.nlp_operator.get_ner("When was The Godfather released?")
        self.assertEqual(actual_value, expected_value)

    def test_get_ner(self):
        expected_value = [['O', 'O', 'O', 'O', 'O', 'B-org', 'B-per', 'I-per', 'I-per', 'I-per', 'I-per', 'O', 'O', 'B-org']]
        actual_value = self.nlp_operator.get_ner("Who is the director of Star Wars: Episode VI - Return of the Jedi?")
        self.assertEqual(actual_value, expected_value)

    def test_get_relation(self):
        expected_value = ["director"]
        actual_value = self.nlp_operator.get_relation("Who is the director of Star Wars: Episode VI - Return of the Jedi?")
        self.assertEqual(actual_value, expected_value)


if __name__ == "__main__":
    unittest.main()
