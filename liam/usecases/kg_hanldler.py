from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS

def create_graph(source, format):
    g = Graph()
    g.parse(source=source, format=format)
    return g

def create_namespaces():
    ns1 = Namespace("http://www.wikidata.org/prop/direct/")
    ns2 = Namespace("http://schema.org/")
    ns3 = Namespace("http://ddis.ch/atai/")
    return ns1, ns2, ns3
