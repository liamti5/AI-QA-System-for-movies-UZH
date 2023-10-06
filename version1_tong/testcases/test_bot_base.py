import unittest
from usecases import bot_base

class TestBotBase(unittest.TestCase):
    
    @classmethod
    def setUp(cls):
        cls.agent = bot_base.Agent(username="burn-largo-coffee_bot", password="Q9R_PM3LJyRDfQ")
        cls.agent.load_graph("./data/14_graph.nt", "turtle") 
    

    def test_query_graph_clean_input(self):
        queries = [
            {
                'description': 'Highest user rating',
                'query': """
                    PREFIX ddis: <http://ddis.ch/atai/>
                    PREFIX wd: <http://www.wikidata.org/entity/>
                    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                    PREFIX schema: <http://schema.org/>
                    SELECT ?lbl WHERE {
                        ?movie wdt:P31 wd:Q11424 .
                        ?movie ddis:rating ?rating .
                        ?movie rdfs:label ?lbl .
                    }
                    ORDER BY DESC(?rating)
                    LIMIT 1
                """,
                'expected_result': ['Forrest Gump']
            },
            {
                'description': 'Lowest user rating',
                'query': """
                    PREFIX ddis: <http://ddis.ch/atai/>
                    PREFIX wd: <http://www.wikidata.org/entity/>
                    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                    PREFIX schema: <http://schema.org/>
                    SELECT ?lbl WHERE {
                        ?movie wdt:P31 wd:Q11424 .
                        ?movie ddis:rating ?rating .
                        ?movie rdfs:label ?lbl .
                    }
                    ORDER BY ASC(?rating)
                    LIMIT 1
                """,
                'expected_result': ['Vampire Assassin']
            },
            {
                'description': 'Director of Apocalypse Now',
                'query': """
                    PREFIX ddis: <http://ddis.ch/atai/>
                    PREFIX wd: <http://www.wikidata.org/entity/>
                    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                    PREFIX schema: <http://schema.org/>
                    SELECT ?director WHERE {
                        ?movie rdfs:label "Apocalypse Now"@en .
                        ?movie wdt:P57 ?directorItem .
                        ?directorItem rdfs:label ?director .
                    }
                    LIMIT 1
                """,
                'expected_result': ['Francis Ford Coppola']
            },
            {
                'description': 'Star Wars: Episode VI - Return of the Jedi',
                'query': """
                     PREFIX ddis: <http://ddis.ch/atai/>  
                     PREFIX wd: <http://www.wikidata.org/entity/>   
                     PREFIX wdt: <http://www.wikidata.org/prop/direct/>   
                     PREFIX schema: <http://schema.org/>   
                     SELECT ?director WHERE {  
                            ?movie rdfs:label ?movieLabel .
                            FILTER(CONTAINS(?movieLabel, "Return of the Jedi"))  
                            ?movie wdt:P57 ?directorItem . 
                            ?directorItem rdfs:label ?director . 
                        }
                        LIMIT 1
                        """,
                        'expected_result': ['Richard Marquand']
            },
            {
                'description': 'Star Wars: Episode VI - Return of the Jedi',
                'query': """
                    PREFIX ddis: <http://ddis.ch/atai/>
                    PREFIX wd: <http://www.wikidata.org/entity/>
                    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                    PREFIX schema: <http://schema.org/>

                    SELECT ?screenwriter WHERE {
                        ?movie rdfs:label ?movieLabel .
                        FILTER(CONTAINS(?movieLabel, "The Masked Gang"))

                        ?movie wdt:P58 ?screenwriterItem .
                        ?screenwriterItem rdfs:label ?screenwriter .
                    }

                    LIMIT 1
                """,
                'expected_result': ['Murat Aslan']
            },
            {
                'description': 'Star Wars: Episode VI - Return of the Jedi',
                'query': """
                    PREFIX ddis: <http://ddis.ch/atai/>
                    PREFIX wd: <http://www.wikidata.org/entity/>
                    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                    PREFIX schema: <http://schema.org/>
                    SELECT ?dateValue WHERE {
                        ?movie rdfs:label ?movieLabel .
                        FILTER(CONTAINS(?movieLabel, "The Godfather"))
                        ?movie wdt:P577 ?dateValue .
                    }

                    LIMIT 1
                """,
                'expected_result': ['2006-03-21']
            }
        ]

        for query_data in queries:
            with self.subTest(description=query_data['description']):
                expected_value = query_data['expected_result']
                actual_value = self.agent.query_graph(query_data['query'])
                self.assertEqual(actual_value, expected_value)


    def test_query_graph_dirty_input(self):
        queries =  [
            {
                'description': "Query contains double quotes'''",
                'query': """
                    '''
                    PREFIX ddis: <http://ddis.ch/atai/>
                    PREFIX wd: <http://www.wikidata.org/entity/>
                    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                    PREFIX schema: <http://schema.org/>
                    SELECT ?lbl WHERE {
                        ?movie wdt:P31 wd:Q11424 .
                        ?movie ddis:rating ?rating .
                        ?movie rdfs:label ?lbl .
                    }
                    ORDER BY DESC(?rating)
                    LIMIT 1
                    '''
                """,
                'expected_result': ['Forrest Gump']
            },
            {
                'description': 'Query contains double quotes """',
                'query': '''
                    """
                    PREFIX ddis: <http://ddis.ch/atai/>
                    PREFIX wd: <http://www.wikidata.org/entity/>
                    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                    PREFIX schema: <http://schema.org/>
                    SELECT ?lbl WHERE {
                        ?movie wdt:P31 wd:Q11424 .
                        ?movie ddis:rating ?rating .
                        ?movie rdfs:label ?lbl .
                    }
                    ORDER BY DESC(?rating)
                    LIMIT 1
                    """
                ''',
                'expected_result': ['Forrest Gump']
            },
             {
                'description': 'Query contains hashtags',
                'query': '''
                    """ #test
                    PREFIX ddis: <http://ddis.ch/atai/>
                    PREFIX wd: <http://www.wikidata.org/entity/>
                    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                    PREFIX schema: <http://schema.org/>
                    SELECT ?lbl WHERE {
                        ?movie wdt:P31 wd:Q11424 .
                        ?movie ddis:rating ?rating .
                        ?movie rdfs:label ?lbl .
                    }
                    ORDER BY DESC(?rating)
                    LIMIT 1
                    """
                ''',
                'expected_result': ['Forrest Gump']
            }
        ]

        for query_data in queries:
            with self.subTest(description=query_data['description']):
                expected_value = query_data['expected_result']
                actual_value = self.agent.query_graph(query_data['query'])
                self.assertEqual(actual_value, expected_value)


if __name__ == '__main__':
    unittest.main()