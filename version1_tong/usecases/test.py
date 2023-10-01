import rdflib

graph = rdflib.Graph()
def load_graph():
    graph.parse('./14_graph.nt', format='turtle')
    print('loaded map successfully')


def sparql(message):
    try:
        return [str(s) for s, in graph.query(message)]
    except:
        return '???'

t='''
    PREFIX ddis: <http://ddis.ch/atai/> 
    PREFIX wd: <http://www.wikidata.org/entity/> 
    PREFIX wdt: <http://www.wikidata.org/prop/direct/> 
    PREFIX schema: <http://schema.org/> 

    SELECT ?lbl WHERE {
        ?genre rdfs:label "neo-noir"@en .
        ?actor rdfs:label "Ryan Gosling"@en .
        ?movie wdt:P136 ?genre .
        ?movie wdt:P161 ?actor .
        ?movie rdfs:label ?lbl .
    }
'''
load_graph()
print(sparql(t))
