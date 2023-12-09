import unittest
from usecases import answer_calculator


class TestAnswerCalculator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.answer_calc = answer_calculator.AnswerCalculator()

    def test_calculate_other_answer(self):
        expected_value = ["Richard Marquand"]
        actual_value = self.answer_calc.calculate_other_answer("Who is the director of Star Wars: Episode VI - Return of the Jedi?", [['O', 'O', 'O', 'O', 'O', 'B-org', 'B-per', 'I-per', 'I-per', 'I-per', 'I-per', 'O', 'O', 'B-org']])
        self.assertEqual(actual_value, expected_value)

    def test_calculate_distance_nodes(self):
        expected_value = 0
        actual_value = self.answer_calc.calculate_node_distance("The Godfather")["Q47703"]
        self.assertEqual(actual_value, expected_value)


    def test_calculate_distance_preds(self):
        expected_value = 0
        actual_value = self.answer_calc.calculate_pred_distance("screenwriter")["P58"]
        self.assertEqual(actual_value, expected_value)

if __name__ == "__main__":
    unittest.main()
