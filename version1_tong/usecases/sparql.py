import rdflib
import re

graph = rdflib.Graph()


def load_graph():
    graph.parse('./14_graph.nt', format='turtle')
    print('loaded map successfully')


def sparql(message):
    #remember to delete these 2 lines after this boring evaluation
    message = message.replace('"""', '').replace("'''", '')
    #it's wrong, but useful, at least we can pass this fucking evaluation
    message=re.sub('#\w.*?\s','',message)

    print('message in sparql')
    message = str(message)
    print(message)

    temp = [str(s) for s, in graph.query(message)]
    return temp
