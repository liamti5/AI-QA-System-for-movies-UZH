import unittest
from usecases import crowdsourcing


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cs = crowdsourcing.Crowdsourcing()

    def test_search(self):
        correct_ex, corrected_ex, incorrect_ex, result_ex, kappa_ex = 3, 0, 0, "2015-01-05", 0.04
        correct, corrected, incorrect, result, kappa = self.cs.search("Q23999890", "P577")
        assert [correct_ex, corrected_ex, incorrect_ex, result_ex, kappa_ex] ==  [correct, corrected, incorrect, result, kappa]

if __name__ == "__main__":
    unittest.main()