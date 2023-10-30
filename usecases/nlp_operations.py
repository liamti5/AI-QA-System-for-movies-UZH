import spacy
from models import NER_CRF


class NLP_Operations:
    """
    responsible for NLP operations
    - get_ner: returns the named entity of a question e.g. [['O', 'O', 'O', 'O', 'B-org']]
    - get_relation: returns the relation of a question e.g. ['director']
    """

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def get_ner(self, question) -> list:
        ner = NER_CRF.get_ner(question)
        return ner

    def get_relation(self, question) -> list:
        doc = self.nlp(question)
        relations = [
            tok.lemma_
            for tok in doc
            if tok.dep_ in ("attr", "nsubj") and tok.pos_ in ("NOUN")
        ]
        return relations
