from typing import Union
import editdistance
import random
from usecases import utils
from usecases import nlp_operations
from usecases import graph_operations
from usecases import recommendations
from usecases import multimedia


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
        self.mm = multimedia.Multimedia()
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

        named_entities, entity_label = self.nlp_operator.get_ner(question)
        assert named_entities, "no entities found"
        print("entities: ", named_entities)

        mapping = {
            "WHEN": self.handle_when,
            "CLOSED": self.handle_closed,
            "RECOMMENDATION": self.handle_recommendation,
            "MULTIMEDIA": self.handle_multimedia,
        }

        # call the corresponding function
        answer = mapping[question_type](named_entities, entity_label)
        return answer

    def handle_when(self, entity: list, label: list) -> str:
        entity = entity[0]
        relation_id = "P577"  # publication date
        entity_id = self.calculate_node_distance(entity)
        answer = self.query(relation_id, entity_id)[0]
        answers_templates = [
            f"The release date of {entity} is {answer}",
            f"{entity} was released on {answer}",
            f"Actually, {entity} was released on {answer}.",
            f"Oh, {entity}? It was released on {answer}.",
            f"You asked about {entity}? It hit the theaters on {answer}.",
        ]
        answer = answers_templates[random.randint(0, len(answers_templates) - 1)]
        return answer

    def handle_closed(self, entity: list, label: list) -> str:
        entity = entity[0]
        relation = self.nlp_operator.get_relation(self.question)
        relation_id = self.calculate_pred_distance(relation)
        relation_label = self.predicates[
            f"http://www.wikidata.org/prop/direct/{relation_id}"
        ]
        entity_id = self.calculate_node_distance(entity)
        print(relation_id, entity_id)
        answer = self.query(relation_id, entity_id)
        answers_templates = [
            f"The {relation_label} of {entity} is {answer}",
            f"{entity}'s {relation_label} is {answer}",
            f"Oh, the {relation_label} of {entity}? That's {answer}.",
            f"Looks like {entity}'s {relation_label} is {answer}.",
            f"Ah, for {entity}, the {relation_label} is actually {answer}.",
            f"Yup, {entity}'s {relation_label}? Definitely {answer}.",
            f"Alright, so {entity} has {answer} as its {relation_label}.",
        ]
        answer = answers_templates[random.randint(0, len(answers_templates) - 1)]
        return answer

    def handle_recommendation(self, entity: list, label: list) -> str:
        movies = self.recommender.recommend_movies(entity, 3)
        answers = self.recommender.recommend_answers(movies)
        recommendations1 = self.recommender.generate_answers_for_recommendation(answers)

        entity_ids = [self.calculate_node_distance(ent) for ent in entity]
        embedding_recs = self.graph_operator.recommendations_embeddings(entity_ids)
        embedding_recs_labels = [self.nodes[rec] for rec in embedding_recs]
        recommendations2 = f" Furthermore, I have found some more movies you'd might like based on embeddings: {' and '.join(embedding_recs_labels)}. Enjoy!"
        return recommendations1 + recommendations2

    def handle_multimedia(self, entity: list, label: list):
        entity_ids = [self.calculate_node_distance(ent) for ent in entity]
        queries = [self.mm.create_sparql(ent_id) for ent_id in entity_ids]
        imdb_ids = [self.graph_operator.query(query)[0] for query in queries]
        assert imdb_ids, "No imdb ids found for {entity}"
        images = self.mm.find_image(imdb_ids, label)
        answer_images = "\n".join(images)
        answer_text = [
            f"As you wished for, here are some images of {', '.join(entity)}"
        ]
        return answer_text[0] + answer_images

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
            try:
                answer = self.nodes[answer[0]]
            except KeyError:
                answer = answer
        except AssertionError:
            print("Using embeddings")
            answer = self.graph_operator.query_with_embeddings(entity, relation)
            assert answer, "No answer found with embeddings"
            answer = self.nodes[answer]
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
