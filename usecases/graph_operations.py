import rdflib


class GraphOperations:
    """
    Handles all operations on the graph:
    - defines graph with fixed path that can be overwritten
    - load graph
    - query graph that returns the answer in a list
    """

    def __init__(self, graph_file="data/14_graph.nt"):
        self.graph = rdflib.Graph()
        self.load_graph(graph_file)

    def load_graph(self, graph_file):
        print("loading graph ...")
        self.graph.parse(graph_file, format="turtle")
        print("loaded graph successfully!")

    def query(self, message):
        # remember to delete these 2 lines after this boring evaluation
        message = message.replace('"""', "").replace("'''", "")
        print("message in sparql")
        message = str(message)
        print(message)
        temp = [str(s) for s, in self.graph.query(message)]
        print(temp)
        return temp
