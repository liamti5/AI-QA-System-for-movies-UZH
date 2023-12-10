import rdflib
import sklearn.metrics
from collections import Counter
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
        self.WD = rdflib.Namespace("http://www.wikidata.org/entity/")
        self.WDT = rdflib.Namespace("http://www.wikidata.org/prop/direct/")
        self.DDIS = rdflib.Namespace("http://ddis.ch/atai/")
        self.RDFS = rdflib.namespace.RDFS
        self.SCHEMA = rdflib.Namespace("http://schema.org/")
        self.entity_emb, self.ent2id, self.id2ent = utils.get_entity_embeddings()
        self.relation_emb, self.rel2id, self.id2rel = utils.get_relation_embeddings()

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
        ent = self.WD[ent]
        relation = self.WDT[relation]

        ent2lbl = {
            ent: str(lbl) for ent, lbl in self.graph.subject_objects(self.RDFS.label)
        }
        lbl2ent = {lbl: ent for ent, lbl in ent2lbl.items()}

        head = self.entity_emb[self.ent2id[ent]]
        pred = self.relation_emb[self.rel2id[relation]]
        lhs = head + pred
        dist = sklearn.metrics.pairwise_distances(
            lhs.reshape(1, -1), self.entity_emb
        ).reshape(-1)
        most_likely = dist.argsort()[0]
        entity = self.id2ent[most_likely]
        print(entity)
        return str(
            entity
        )  # returns a link e.g. 'http://www.wikidata.org/entity/Q5058838'

    def recommendations_embeddings(self, ents: list) -> list:
        ents = [self.ent2id[self.WD[ent]] for ent in ents]
        recommendations = []
        for ent in ents:
            dist = sklearn.metrics.pairwise_distances(
                self.entity_emb[ent].reshape(1, -1), self.entity_emb
            ).reshape(-1)
            most_likely = dist.argsort()[1:15]
            for movie in most_likely:
                if self._check_entity_type(self.id2ent[movie], self.WD["Q11424"]):
                    recommendations.append(str(self.id2ent[movie]))
        counts = Counter(recommendations).most_common(2)
        try:
            first_rec = str(counts[0][0])
            second_rec = str(counts[1][0])
            recs = [first_rec, second_rec]
        except IndexError:
            return [str(counts[0][0])]
        return recs

    def _check_entity_type(self, entity_id, type_id):
        for s, _, _ in self.graph.triples((entity_id, self.WDT["P31"], type_id)):
            if s:
                return True
        return False
