from typing import Union
import editdistance
import random
from usecases import utils
from usecases import nlp_operations
from usecases import graph_operations
from usecases import recommendations


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
        self.recommender = recommendations.Recommendations()
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
        self.question = None

    def calculate_answer(self, question: str) -> str:
        # preprocess question
        self.question = question
        question = question.replace("\n", "").replace("?", "")
        question_list = question.split(" ")
        question_list = list(
            filter(lambda item: item != "", question_list)
        )  # removes leading and trailing whitespaces from the list

        # get question type, returns e.g. WHEN
        question_type = self.nlp_operator.get_question_type(question)
        print("question_type: ", question_type)

        named_entities = self.nlp_operator.get_ner(question)
        assert named_entities, "no entities found"
        print("entities: ", named_entities)

        mapping = {
            "WHEN": self.handle_when,
            "CLOSED": self.handle_closed,
            "RECOMMENDATION": self.handle_recommendation,
            "MULTIMEDIA": self.handle_multimedia,
        }

        # call the corresponding function
        answer = mapping[question_type](named_entities)
        return answer

    def handle_when(self, entity: list) -> str:
        entity = entity[0]
        relation_id = "P577"  # publication date
        entity_id = self.calculate_node_distance(entity)
        answer = self.query(relation_id, entity_id)[0]
        answers_templates = [
            f"The release date of {entity} is {answer}",
            f"{entity} was released on {answer}",
        ]
        answer = answers_templates[random.randint(0, len(answers_templates) - 1)]
        return answer

    def handle_closed(self, entity: list) -> str:
        entity = entity[0]
        relation = self.nlp_operator.get_relation(self.question)
        relation_id = self.calculate_pred_distance(relation)
        entity_id = self.calculate_node_distance(entity)
        print(relation_id, entity_id)
        answer = self.query(relation_id, entity_id)
        answers_templates = [
            f"The {relation} of {entity} is {answer}",
            f"{entity}'s {relation} is {answer}",
        ]
        answer = answers_templates[random.randint(0, len(answers_templates) - 1)]
        return answer

    def handle_recommendation(self, entity: list) -> str:
        movies = self.recommender.recommend_movies(entity, 3)
        answers = self.recommender.recommend_answers(movies)
        return self.recommender.generate_answers_for_recommendation(answers)

    def handle_multimedia(self, entity: list):
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
            answer = self.nodes[answer[0]]
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
