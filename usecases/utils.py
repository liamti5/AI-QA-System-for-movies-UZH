import json
import rdflib
import csv
import numpy as np
import pandas as pd


def get_dicti(path):
    """
    file for all kind of utils, for now only:
    - loads a json file from the specified path and returns it as a dictionary
    - we use this for the nodes and predicates
    """

    with open(path, "r") as f:
        dicti = json.load(f)
    return dicti


def get_entity_embeddings(
    path_emb="data/entity_embeds.npy", path_ids="data/entity_ids.del"
):
    entitiy_emb = np.load(path_emb)
    with open(path_ids, "r") as ifile:
        ent2id = {
            rdflib.term.URIRef(ent): int(idx)
            for idx, ent in csv.reader(ifile, delimiter="\t")
        }
        id2ent = {v: k for k, v in ent2id.items()}

    return entitiy_emb, ent2id, id2ent


def get_relation_embeddings(
    path_emb="data/relation_embeds.npy", path_ids="data/relation_ids.del"
):
    relation_emb = np.load(path_emb)
    with open(path_ids, "r") as ifile:
        rel2id = {
            rdflib.term.URIRef(rel): int(idx)
            for idx, rel in csv.reader(ifile, delimiter="\t")
        }
        id2rel = {v: k for k, v in rel2id.items()}

    return relation_emb, rel2id, id2rel

def get_csv(path_csv):
    with open(path_csv, "r") as f:
        df = pd.read_csv(f)
    return df