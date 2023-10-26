import json


def get_dicti(path):
    """
    file for all kind of utils, for now only:
    - loads a json file from the specified path and returns it as a dictionary
    - we use this for the nodes and predicates
    """

    with open(path, "r") as f:
        dicti = json.load(f)
    return dicti
