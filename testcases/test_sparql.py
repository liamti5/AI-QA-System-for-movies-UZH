import unittest
from usecases.sparql import get_ner, get_relation

"""
* There are mainly 8 types of tags:  

    | Tag | Description | Examples |
    | ---- | ---- | ---- |
    | geo | Geographical Entity | Paris, Washington DC |
    | org | Organization | APEC, WTO, United Nations |
    | per | Person | President George Bush |
    | gpe | Geopolitical Entity | U.S., France, Japan |
    | tim | Time indicator | July, Wednesday |
    | art | Artifact | Internet, International Space Station |
    | eve | Event | World War I, Tennis Masters Cup |
    | nat | Natural Phenomenon | Hurricane Katrina |
"""


class TestSparql(unittest.TestCase):
    def test_get_ner(self):
        expected_value = "Star Wars: Episode VI - Return of the Jedi"
        actual_value = get_ner("Who is the director of Star Wars: Episode VI - Return of the Jedi?")
        self.assertEqual(actual_value, expected_value)


    def test_get_relation(self):
        expected_value = "director"
        actual_value = get_relation("Who is the director of Star Wars: Episode VI - Return of the Jedi?")
        self.assertEqual(actual_value, expected_value)


if __name__ == '__main__':
    unittest.main()
