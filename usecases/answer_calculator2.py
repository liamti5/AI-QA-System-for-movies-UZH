from usecases import utils
from usecases import nlp_operations
from usecases import graph_operations
import copy
import editdistance
import random


class AnswerCalculator:
    """
    responsible for main calculations to answer a question and initializes all the helper classes
    - calculate answer gets called from bot_base.py instead of query() (still needs to be implemented in main.py)
    - handles different cases like When
    - calculate_answer: use the other 2 functions to deal with "when" questions and other questions (calculate_other_answer,calculate_when_answer)
    - search_answer: if everything goes well, namely we have found the entity and the relation, then we should handle the question which has maybe many answers for example: The "godfather" questions
    """

    def __init__(self):
        self.nodes = utils.get_dicti("data/nodes.json")
        self.predicates = utils.get_dicti("data/predicates_clean.json")
        self.nlp_operator = nlp_operations.NLP_Operations()
        self.graph_operator = graph_operations.GraphOperations()
        self.wh_words = [
            "What",
            "what",
            "when",
            "When",
            "where",
            "Where",
            "Who",
            "who",
            "Whom",
            "whom",
            "Which",
            "which",
            "Whose",
            "whose",
            "Why",
            "why",
            "How",
            "how",
        ]
        self.useless_words = [
            "am",
            "is",
            "are",
            "have",
            "has",
            "had",
            "was",
            "were",
            "a",
            "an",
            "the",
            "that",
            "this",
            "these",
            "those",
            "above",
            "across",
            "against",
            "along",
            "among",
            "around",
            "at",
            "before",
            "behind",
            "below",
            "beneath",
            "beside",
            "between",
            "by",
            "down",
            "from",
            "in",
            "into",
            "near",
            "off",
            "on",
            "to",
            "woward",
            "under",
            "upon",
            "with",
            "and",
            "within",
            "of",
            "for",
            "since",
            "during",
            "over",
        ]
        self.all_delete_words = self.wh_words + self.useless_words

    def calculate_answer(self, question: str) -> str:
        # preprocess question
        question = question.replace("\n", "").replace("?", "")
        question_list = question.split(" ")
        question_list = list(
            filter(lambda item: item != "", question_list)
        )  # removes leading and trailing whitespaces from the list

        # get question type, returns e.g. WHEN
        question_type = self.nlp_operator.get_question_type(question)
        print("question_type: ", question_type)

        # get tags of words, returns e.g. [['O', 'O', 'O', 'O', 'O']]
        tag_list = self.nlp_operator.get_ner(question)
        print("tag_list: ", tag_list)

        # find entity
        indexes = [index for index, val in enumerate(tag_list[0]) if val != "O"]
        entity = (
            " ".join(question_list[indexes[0] : indexes[-1] + 1])
            .rstrip("?")
            .rstrip('"')
            .rstrip("'")
        )
        print("entity: ", entity)

        # find relation
        relation = ""
        if not question_type == "WHEN":
            relation = self.nlp_operator.get_relation(question)
            print("relation: ", relation)

        mapping = {
            "WHEN": self.handle_when,
            "CLOSED": self.handle_closed,
            "RECOMMENDATION": self.handle_recommendation,
            "MULTIMEDIA": self.handle_multimedia,
        }
        # call the corresponding function
        answer = mapping[question_type](entity, relation)
        return answer

    def handle_when(self, entity: str, relation: str) -> str:
        relation_id = "P577"  # publication date
        entity_id = self.calculate_node_distance(entity)
        answer = self.query(relation_id, entity_id)
        return answer

    def handle_closed(self, entity: str, relation: str) -> str:
        relation_id = self.calculate_pred_distance(relation)
        entity_id = self.calculate_node_distance(entity)
        answer = self.query(relation_id, entity_id)
        return answer

    def handle_recommendation(self, entity: str, relation: str):
        return

    def handle_multimedia(self, entity: str, relation: str):
        return

    def query(self, relation: str, entity: str) -> str:
        query = f"""
            PREFIX ddis: <http://ddis.ch/atai/>
            PREFIX wd: <http://www.wikidata.org/entity/>
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            PREFIX schema: <http://schema.org/>
            SELECT ?answer
            WHERE {{
                wd:{entity} wdt:{relation} ?answer.
            }}
            LIMIT 1
        """

        try:
            answer = self.graph_operator.query(query)
            assert answer, "No answer found, trying embeddings"
        except AssertionError:
            print("Using embeddings")
            answer = self.graph_operator.query_with_embeddings(entity, relation)
            answer = self.nodes[answer]
        finally:
            if not answer:
                answer = "Sorry, I don't know the answer to this question."

        return answer

    def calculate_node_distance(self, entity: str) -> str:
        distance_dict = {}
        print("entity: {}".format(entity))
        for key, value in self.nodes.items():
            distance_dict[key.split("/")[-1]] = editdistance.eval(value, entity)
        distance_dict = dict(sorted(distance_dict.items(), key=lambda x: x[1]))
        return list(distance_dict.keys())[0]

    def calculate_pred_distance(self, relation: str) -> str:
        pred_distance_dict = {}
        print("relation: {}".format(relation))
        for key, value in self.predicates.items():
            pred_distance_dict[key.split("/")[-1]] = editdistance.eval(value, relation)
        pred_distance_dict = dict(
            sorted(pred_distance_dict.items(), key=lambda x: x[1])
        )
        return list(pred_distance_dict.keys())[0]
