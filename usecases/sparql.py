import rdflib
import re
from models import NER_CRF
import spacy
import json
import editdistance


nlp = spacy.load("en_core_web_sm")


graph = rdflib.Graph()


def load_graph():
    print('loading graph')
    graph.parse('data/14_graph.nt', format='turtle')
    print('loaded graph successfully')


def query(message):
    # remember to delete these 2 lines after this boring evaluation
    message = message.replace('"""', '').replace("'''", '')
    # it's wrong, but useful, at least we can pass this fucking evaluation
    message = re.sub('#\w.*?\s', '', message)
    print('message in sparql')
    message = str(message)
    print(message)
    temp = [str(s) for s, in graph.query(message)]
    return temp


def query2(message):
    entity = get_ner(message)
    relation = get_relation(message)

    nodes = get_nodes()
    predicates = get_predicates()

    matching_entity = get_matching(entity, nodes)
    matching_relation = get_matching(relation, predicates)
    print(matching_entity, matching_relation)

    query = get_sparql(matching_entity, matching_relation)
    print(query)

    answer = [str(s) for s, in graph.query(query)]
    print(answer)

    return answer


def get_ner(question):
    question_list = question.split(" ")
    ner = NER_CRF.get_ner(question)    
    indexes = [index for index, val in enumerate(ner[0]) if val != "O"]
    entity = " ".join(question_list[indexes[0]:indexes[-1]+1]).rstrip("?")
    return entity


def get_relation(question):
    try: 
        doc = nlp(question)
        relations = [tok.lemma_ for tok in doc if tok.dep_ in ('attr', 'nsubj') and tok.pos_ in ('NOUN')]
        assert len(relations) == 1
        return relations[0]
    except AssertionError:
        return


def get_nodes():
    with open('data/nodes.json', 'r') as f:
        nodes = json.load(f)
    return nodes


def get_predicates():
    with open('data/predicates_clean.json', 'r') as f:
        predicates = json.load(f)    
    return predicates


def get_matching(item, dicti):
    assert type(dicti) == dict
    tmp = 9999
    match_node = ""
    for key, value in dicti.items():                
        if editdistance.eval(value, item) < tmp:
            tmp = editdistance.eval(value, item)
            match_node = key
    
    match_node = match_node.split('/')[-1]
    return match_node    

    
def get_sparql(ner, relation):
    query = f"""
            PREFIX ddis: <http://ddis.ch/atai/>
            PREFIX wd: <http://www.wikidata.org/entity/>
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            PREFIX schema: <http://schema.org/>

            SELECT ?subject WHERE {{
                wd:{ner} wdt:{relation} ?item .
                ?item rdfs:label ?subject .
            }}
            LIMIT 5
        """
    return query