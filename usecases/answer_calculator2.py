import random
import editdistance
from usecases import utils
from usecases import nlp_operations
from usecases import graph_operations
from usecases import recommendations
from usecases import multimedia
from usecases import crowdsourcing


class AnswerCalculator:
    """
    responsible for main calculations to answer a question and initializes all the helper classes
    - calculate answer gets called from bot_base.py
    - handles different cases like When, Closed, Recommendations and Multimedia
    """

    def __init__(self):
        self.nodes = utils.get_dicti("data/nodes.json")
        self.predicates = utils.get_dicti("data/predicates_clean.json")
        self.nlp_operator = nlp_operations.NLP_Operations()
        self.graph_operator = graph_operations.GraphOperations()
        self.recommender = recommendations.Recommendations()
        self.cs = crowdsourcing.Crowdsourcing()
        self.mm = multimedia.Multimedia()
        self.question = None

    def calculate_answer(self, question: str) -> str:
        """
        Calculates the answer to the given question.

        Args:
            question (str): The question to be answered.

        Returns:
            str: The calculated answer.

        Raises:
            AssertionError: If no entities are found in the question.
        """
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
        """
        Handles the 'when' question type by retrieving the publication date of the given entity
        and generating a response template with the entity and its release date.

        Args:
            entity (list): A list containing the entity name.
            label (list): A list containing the label.

        Returns:
            str: The generated response template with the entity and its release date.
        """
        entity = entity[0]
        relation_id = "P577"  # publication date
        entity_id = self.calculate_node_distance(entity)
        answer = self.query(relation_id, entity_id)
        # to return directly if the quesiton was answered using the crowd-data, where we would already have an answer template being used
        if len(answer) > 150:
            return answer
        answer = answer[0]
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
        """
        Handles the 'closed' type of question by calculating the answer based on the given entity and label.

        Args:
            entity (list): The list of entities.
            label (list): The list of labels.

        Returns:
            str: The calculated answer based on the entity and label.
        """
        entity = entity[0]
        relation = self.nlp_operator.get_relation(self.question)
        relation_id = self.calculate_pred_distance(relation)
        relation_label = self.predicates[
            f"http://www.wikidata.org/prop/direct/{relation_id}"
        ]
        entity_id = self.calculate_node_distance(entity)
        print(relation_id, entity_id)
        answer = self.query(relation_id, entity_id)
        # to return directly if the quesiton was answered using the crowd-data, where we would already have an answer template being used
        if len(answer) > 150:
            return answer
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
        """
        Handles the 'recommendation' questions based on the given entity and label.

        Args:
            entity (list): The list of entities.
            label (list): The list of labels.

        Returns:
            str: The recommendations generated based on the given entity and label.
        """
        movies = self.recommender.recommend_movies(entity, 3)
        answers = self.recommender.recommend_answers(movies)
        recommendations1 = self.recommender.generate_answers_for_recommendation(answers)

        entity_ids = [self.calculate_node_distance(ent) for ent in entity]
        embedding_recs = self.graph_operator.recommendations_embeddings(entity_ids)
        embedding_recs_labels = [self.nodes[rec] for rec in embedding_recs]
        recommendations2 = f" Furthermore, I have found some more movies you'd might like based on embeddings: {' and '.join(embedding_recs_labels)}. Enjoy!"
        return recommendations1 + recommendations2

    def handle_multimedia(self, entity: list, label: list):
        """
        Handles multimedia entities by calculating node distances, creating SPARQL queries,
        querying the graph, finding images, and returning the answer text with images.

        Args:
            entity (list): List of entities.
            label (list): List of labels.

        Returns:
            str: Answer text with images.
        """
        entity_ids = [self.calculate_node_distance(ent) for ent in entity]
        queries = [self.mm.create_sparql(ent_id) for ent_id in entity_ids]
        imdb_ids = [self.graph_operator.query(query)[0] for query in queries]
        assert len(imdb_ids) == len(entity_ids), "No imdb ids found for {entity}"
        images = self.mm.find_image(imdb_ids, label)
        answer_images = "\n".join(images)
        answer_text = [f"As you wished for, here is an image of {', '.join(entity)}: "]
        return answer_text[0] + answer_images

    def query(self, relation: str, entity: str) -> str:
        """
        Executes a SPARQL query to retrieve an answer from the knowledge graph with or without embeddings or searches for the answer in the crowd-data.

        Args:
            relation (str): The relation to query.
            entity (str): The entity to query.

        Returns:
            str: The answer retrieved from the knowledge graph.
        """
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
            print("Trying Crowd Data")
            correct, corrected, incorrect, result, kappa = self.cs.search(
                entity, relation
            )
            assert kappa, "Nothing found in crowddata, trying KG"

            if "wd" in result.lower():
                result = self.nodes[f"http://www.wikidata.org/entity/{result[3:]}"]

            answer = (
                f"{result} - according to the crowd, who had an inter-rater agreement of {kappa} in this batch. The answer distribution for this specific task was {correct} support votes and {incorrect} reject votes."
                if correct or incorrect
                else f"{result} - according to the crowd, who had an inter-rater agreement of {kappa} in this batch. The answer was corrected by the crowd workers with {corrected} workers voting for the same correction"
            )

        except AssertionError:
            try:
                print("Trying KG")
                answer = self.graph_operator.query(query)
                assert answer, "No answer found, trying embeddings"
                try:
                    answer = self.nodes[answer[0]]
                except KeyError:
                    pass
            except AssertionError:
                print("Trying embeddings")
                answer = self.graph_operator.query_with_embeddings(entity, relation)
                assert answer, "No answer found with embeddings"
                answer = self.nodes[answer]

        return answer

    def calculate_node_distance(self, entity: str) -> str:
        """
        Calculates the distance between the given entity and all nodes in the graph that are stored in a dictionary.

        Parameters:
            entity (str): The entity to calculate the distance for.

        Returns:
            str: The node with the closest distance to the entity.
        """
        distance_dict = {}
        print("entity: {}".format(entity))
        for key, value in self.nodes.items():
            distance_dict[key.split("/")[-1]] = editdistance.eval(value, entity)
        distance_dict = dict(sorted(distance_dict.items(), key=lambda x: x[1]))
        return list(distance_dict.keys())[0]

    def calculate_pred_distance(self, relation: str) -> str:
        """
        Calculates the distance between the given relation and the predicates in the dictionary.

        Args:
            relation (str): The relation to calculate the distance for.

        Returns:
            str: The key of the predicate with the smallest distance to the given relation.
        """
        pred_distance_dict = {}
        print("relation: {}".format(relation))
        for key, value in self.predicates.items():
            pred_distance_dict[key.split("/")[-1]] = editdistance.eval(value, relation)
        pred_distance_dict = dict(
            sorted(pred_distance_dict.items(), key=lambda x: x[1])
        )
        return list(pred_distance_dict.keys())[0]
