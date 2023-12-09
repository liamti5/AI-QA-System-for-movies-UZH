import spacy
from usecases import utils
from fuzzywuzzy import fuzz


class NLP_Operations:
    """
    responsible for NLP operations
    - get_ner: returns the named entity of a question e.g. [['O', 'O', 'O', 'O', 'B-org']]
    - get_relation: returns the relation of a question e.g. ['director']
    """

    def __init__(self):
        print("loading NLP models ...")
        self.nlp_sm = spacy.load("en_core_web_sm")
        self.nlp_ner = spacy.load("./models/NER_model-best/")
        self.nlp_dif = spacy.load("./models/QD_model-last/")
        self.preds = utils.get_dicti("./data/predicates_clean.json")
        print("SUCCSESS: NLP models loaded")

    def get_ner(self, question) -> list:
        doc = self.nlp_ner(question)
        ne2 = list(doc.ents)
        ne2_text = [str(ent.text) for ent in ne2]
        ne2_label = [str(ent.label_) for ent in ne2]
        return ne2_text, ne2_label

    def get_relation(self, question) -> list:
        doc = self.nlp_sm(question)
        relations = None
        try:
            similarities = {}
            for v in self.preds.values():
                similarity = fuzz.partial_ratio(v, question)
                if similarity > 65:
                    similarities[v] = similarity

            similarities = {k: v for k, v in sorted(similarities.items(), key=lambda item: item[1])}  
            relations = list(similarities.keys())[-1]         
            assert relations, "No exact match found"
        
        except AssertionError:
            try:
                relations = [
                    tok.lemma_
                    for tok in doc
                    if tok.dep_ in ("attr", "nsubj") and tok.pos_ in ("PROPN", "NOUN")
                ]
                assert relations, "No relation found ..."
                relations = " ".join(relations)  

            except AssertionError:
                print(2)
                relations = [
                    tok.lemma_
                    for tok in doc
                    if tok.pos_ in ("VERB")
                ]
        
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
