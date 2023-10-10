import unittest
from usecases.sparql import load_graph, query
from usecases import bot_base

class TestBotBase(unittest.TestCase):  

    @classmethod
    def setUpClass(cls):
        load_graph()


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
                'description': 'multiple results (limit = 10)',
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
                    LIMIT 10
                """,
                'expected_result': ['Vampire Assassin', 'Vampires vs. Zombies', 'Aag', 'Joystick Nation – Generation Hip Hop', 'Going Overboard', "Alex l'ariete", 'House of the Dead', 'Killers', "Ghosts Can't Do It", 'Snakes on a Train']
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
                actual_value = query(query_data['query'])
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
                'description': 'Query contains comments',
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
                actual_value = query(query_data['query'])
                self.assertEqual(actual_value, expected_value)


if __name__ == '__main__':
    unittest.main()