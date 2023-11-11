import rdflib
import sklearn.metrics
from usecases import utils



class GraphOperations:
    """
    Handles all operations on the graph:
    - defines graph with fixed path that can be overwritten
    - load graph
    - query graph that returns the answer in a list
    """

    def __init__(self, graph_file="data/14_graph.nt"):
        self.graph = rdflib.Graph()
        self.loaded = False
        self.load_graph(graph_file)

    def load_graph(self, graph_file):
        assert self.loaded is False, "Graph already loaded"
        print("loading graph ...")
        self.graph.parse(graph_file, format="turtle")
        print("loaded graph successfully!")
        self.loaded = True

    def query(self, query):
        query = query.replace('"""', "").replace("'''", "")
        query = str(query)
        answer = [str(s) for s, in self.graph.query(query)]
        return answer
    
    def query_with_embeddings(self, ent, relation) -> str:
        WD = rdflib.Namespace('http://www.wikidata.org/entity/')
        WDT = rdflib.Namespace('http://www.wikidata.org/prop/direct/')
        DDIS = rdflib.Namespace('http://ddis.ch/atai/')
        RDFS = rdflib.namespace.RDFS
        SCHEMA = rdflib.Namespace('http://schema.org/')

        ent = WD[ent]
        relation = WDT[relation]

        entity_emb, ent2id, id2ent = utils.get_entity_embeddings()
        relation_emb, rel2id, id2rel = utils.get_relation_embeddings()
        ent2lbl = {ent: str(lbl) for ent, lbl in self.graph.subject_objects(RDFS.label)}
        lbl2ent = {lbl: ent for ent, lbl in ent2lbl.items()}

        head = entity_emb[ent2id[ent]]
        pred = relation_emb[rel2id[relation]]
        lhs = head + pred
        dist = sklearn.metrics.pairwise_distances(lhs.reshape(1, -1), entity_emb).reshape(-1)
        most_likely = dist.argsort()[0]
        entity = id2ent[most_likely]
        return str(entity) # returns a link e.g. 'http://www.wikidata.org/entity/Q5058838'
