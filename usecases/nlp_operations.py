import spacy


class NLP_Operations:
    """
    responsible for NLP operations
    - get_ner: returns the named entity of a question e.g. [['O', 'O', 'O', 'O', 'B-org']]
    - get_relation: returns the relation of a question e.g. ['director']
    """

    def __init__(self):
        self.nlp_sm = spacy.load("en_core_web_sm")
        self.nlp_ner = spacy.load("./models/NER_model-best/")
        self.nlp_dif = spacy.load("./models/QD_model-last/")

    def get_ner(self, question) -> list:
        doc = self.nlp_ner(question)
        ne2 = list(doc.ents)
        ne2 = [str(ent) for ent in ne2]
        return ne2

    def get_relation(self, question) -> list:
        doc = self.nlp_sm(question)
        try:
            relations = [
                tok.lemma_
                for tok in doc
                if tok.dep_ in ("attr", "compound", "nsubj")
                and tok.pos_ in ("PROPN", "NOUN")
            ]
            assert relations, "No relation found ..."
            relations = " ".join(relations)
            return relations
        except AssertionError:
            relations = [tok.lemma_ for tok in doc if tok.pos_ in ("VERB")][0]
        return relations

    def get_question_type(self, question) -> str:
        doc = self.nlp_dif(question)
        most_likely_category = max(doc.cats, key=doc.cats.get)
        return most_likely_category


def main():
    nlp = NLP_Operations()
    question = "Who is the director of the movie Titanic?"
    print(nlp.get_question_type(question))


if __name__ == "__main__":
    main()
