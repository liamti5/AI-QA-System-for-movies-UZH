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
        # ner = NER_CRF.get_ner(question)
        nlp = spacy.load("./models/NER_model-best/")  
        doc = nlp(question)
        ne2 = list(doc.ents)
        ne2 = [str(ent) for ent in ne2]
        return ne2

    def get_relation(self, question) -> list:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(question)
        relations = [
            tok.lemma_
            for tok in doc
            if tok.dep_ in ("attr", "nsubj") and tok.pos_ in ("NOUN")
        ]
        assert len(relations) == 1, "There should be exactly one relation"
        return relations[0]

    def get_question_type(self, question) -> str:
        nlp = spacy.load("./models/QD_model-last/")  
        doc = nlp(question)
        most_likely_category = max(doc.cats, key=doc.cats.get)
        return most_likely_category


def main():
    nlp = NLP_Operations()
    question = "Who is the director of the movie Titanic?"
    print(nlp.get_question_type(question))


if __name__ == "__main__":
    main()
