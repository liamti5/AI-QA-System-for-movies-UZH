import unittest 
import time
from usecases import sparql, bot_base


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

    # @classmethod
    # def setUpClass(cls):
    #     bot_base.load_graph()


    def test_get_ner(self):
        expected_value = "The Godfather"
        actual_value = sparql.get_ner("When was The Godfather released?")
        self.assertEqual(actual_value, expected_value)


    def test_get_relation(self):
        expected_value = "director"
        actual_value = sparql.get_relation("Who is the director of Star Wars: Episode VI - Return of the Jedi?")
        self.assertEqual(actual_value, expected_value)

    
    # def test_get_sparql(self):
    #     expected_value = """
    #         PREFIX ddis: <http://ddis.ch/atai/>
    #         PREFIX wd: <http://www.wikidata.org/entity/>
    #         PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    #         PREFIX schema: <http://schema.org/>

    #         SELECT ?subject WHERE {
    #             wd:Q7750525 wdt:P57 ?item.
    #             ?director rdfs:label ?subject.
    #         }
    #         LIMIT 5
    #     """
    #     actual_value = get_sparql("Star Wars: Episode VI - Return of the Jedi", "director")
    #     self.assertEqual(actual_value, expected_value)

    def test_get_matching(self):
        expected_value = "this is a"
        actual_value = sparql.get_matching("test", {"this is a": "test"})
        self.assertEqual(actual_value, expected_value)


    # def test_query2(self):
    #     start_time = time.perf_counter_ns()
    #     expected_value = ['Richard Marquand']
    #     actual_value = sparql.query2("Who is the director of Star Wars: Episode VI - Return of the Jedi?")
    #     self.assertEqual(actual_value, expected_value)
    #     end_time = time.perf_counter_ns()
    #     print(f"test_query2 took: {round((end_time - start_time) * 10**-9, 4)}s")


if __name__ == '__main__':
    unittest.main()
