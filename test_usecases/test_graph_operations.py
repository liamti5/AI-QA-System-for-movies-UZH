import unittest
from usecases import graph_operations


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph_operator = graph_operations.GraphOperations()

    def test_query(self):
        query = """
            PREFIX ddis: <http://ddis.ch/atai/>
            PREFIX wd: <http://www.wikidata.org/entity/>
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            PREFIX schema: <http://schema.org/>
            SELECT ?entity_name WHERE{   
                wd:Q7750525 wdt:P57 ?temp.
                ?temp rdfs:label ?entity_name.
            }
            LIMIT 1
        """
        expected_value = ["Murat Aslan"]
        actual_value = self.graph_operator.query(query)
        self.assertEqual(actual_value, expected_value)

    def test_check_entity_type(self):
        expected_value = True
        actual_value = self.graph_operator._check_entity_type(self.graph_operator.ent2id[self.graph_operator.WD['Q11424']], self.graph_operator.WDT['P31'])
        self.assertEqual(actual_value, expected_value)


if __name__ == "__main__":
    unittest.main()
