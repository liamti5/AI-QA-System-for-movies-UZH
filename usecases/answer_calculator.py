from usecases import utils
from usecases import nlp_operations
from usecases import graph_operations
import copy
import editdistance


class AnswerCalculator:
    """
    responsible for main calculations to answer a question and initializes all the helper classes
    - calculate answer gets called from bot_base.py instead of query() (still needs to be implemented in main.py)
    - handles different cases like When
    - calculate_answer: use the other 2 functions to deal with "when" questions and other questions (calculate_other_answer,calculate_when_answer)
    - search_answer: if everything goes well, namely we have found the entity and the relation, then we should handle the question which has maybe many answers for example: The "godfather" questions
    - search_answer_for_all_O: if everything goes badly, namely we haven't found the entity and the relation, pray we could find an answer and one answer is enough, pray it's right
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

    def calculate_answer(self, question):
        question_list = question.split(" ")
        tag_list = self.nlp_operator.get_ner(
            question
        )  # returns e.g. [['O', 'O', 'O', 'O', 'O']]

        wh_word = question_list[0].upper()
        if wh_word == "WHEN":
            return self.calculate_when_answer(copy.deepcopy(question), tag_list)
        else:
            return self.calculate_other_answer(copy.deepcopy(question), tag_list)

    def calculate_other_answer(self, question, tag_list):
        print("calculate other answer")
        question_list = question.split(" ")
        try:
            # find entity
            indexes = [index for index, val in enumerate(tag_list[0]) if val != "O"]
            print(indexes)
            entity = (
                " ".join(question_list[indexes[0] : indexes[-1] + 1])
                .rstrip("?")
                .rstrip('"')
                .rstrip("'")
            )
            print(entity)

            relations = self.nlp_operator.get_relation(question)
            print(relations)
            assert len(relations) == 1
            relations = relations[0]

            possible_answer = self.search_answer(entity, relations, 0)[0]

        except:
            temp = copy.deepcopy(question_list)
            possible_answer = self.forcely_search(temp, 0)

        finally:
            return possible_answer

    def calculate_when_answer(self, question, tag_list):
        question_list = question.split(" ")

        try:
            # find entity
            indexes = [index for index, val in enumerate(tag_list[0]) if val != "O"]
            entity = (
                " ".join(question_list[indexes[0] : indexes[-1] + 1])
                .rstrip("?")
                .rstrip('"')
                .rstrip("'")
            )

            entity_list = " ".join(question_list[indexes[0] : indexes[-1] + 1]).split(
                " "
            )

            # delete entity word
            temp = copy.deepcopy(question_list)
            for word in entity_list:
                temp.remove(word)

            for word in self.all_delete_words:
                try:
                    temp.remove(word)
                except:
                    pass

            assert len(temp) == 1
            relations = temp[0] + " time"

            possible_answer = []
            possible_answer = self.search_answer(entity, relations, 1)

        except:
            temp = copy.deepcopy(question_list)
            possible_answer = self.forcely_search(temp, 1)

        return possible_answer

    def search_answer(self, entity_word, related_word, is_when):
        search_loop = 0
        search_flag = 0
        edit_distance = 1

        node_distance_dict = self.calculate_node_distance(entity_word)
        pred_distance_dict = self.calculate_pred_distance(related_word)

        searched_answers = []
        for n_key in node_distance_dict.keys():
            search_loop += 1

            if node_distance_dict[n_key] == 0:
                edit_distance = 0
            else:
                edit_distance = 1

            for p_key in pred_distance_dict.keys():
                if is_when:
                    query = f"""
                        PREFIX ddis: <http://ddis.ch/atai/>
                        PREFIX wd: <http://www.wikidata.org/entity/>
                        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                        PREFIX schema: <http://schema.org/>
                        SELECT ?date WHERE{{    
                            wd:{n_key} wdt:{p_key} ?date.
                        }}
                        LIMIT 1
                        """
                else:
                    query = f"""
                        PREFIX ddis: <http://ddis.ch/atai/>
                        PREFIX wd: <http://www.wikidata.org/entity/>
                        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                        PREFIX schema: <http://schema.org/>
                        SELECT ?entity_name WHERE{{    
                            wd:{n_key} wdt:{p_key} ?temp.
                            ?temp rdfs:label ?entity_name.
                        }}
                        LIMIT 1
                    """

                print(query)
                answers = []
                answers = self.graph_operator.query(query)
                if len(answers) > 0:
                    search_flag = 1
                if search_flag == 1:
                    searched_answers.append(answers)
                    break
            if search_flag == 1 and edit_distance == 1:
                break
            if search_loop > 10:
                answers = []
                break

        return searched_answers

    def search_answer_for_all_O(self, entity_word, related_word, is_when):
        node_distance_dict = self.calculate_node_distance(entity_word)
        pred_distance_dict = self.calculate_pred_distance(related_word)

        search_flag = 0

        # entity distance seems reliable, try 5 times
        try_times = 0
        for n_key in node_distance_dict.keys():
            try_times += 1
            for p_key in pred_distance_dict.keys():
                if is_when:
                    query = f"""
                        PREFIX ddis: <http://ddis.ch/atai/>
                        PREFIX wd: <http://www.wikidata.org/entity/>
                        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                        PREFIX schema: <http://schema.org/>
                        SELECT ?date WHERE{{    
                            wd:{n_key} wdt:{p_key} ?date.
                        }}
                        LIMIT 1
                        """
                else:
                    query = f"""
                        PREFIX ddis: <http://ddis.ch/atai/>
                        PREFIX wd: <http://www.wikidata.org/entity/>
                        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                        PREFIX schema: <http://schema.org/>
                        SELECT ?entity_name WHERE{{    
                            wd:{n_key} wdt:{p_key} ?temp.
                            ?temp rdfs:label ?entity_name.
                        }}
                        LIMIT 1
                    """

                answers = self.graph_operator.query(query)
                if len(answers) > 0 and len(answers[0]) == 10:
                    search_flag = 1
                if search_flag == 1:
                    break
            if search_flag == 1:
                break
            if try_times > 10:
                break
        return answers

    def calculate_node_distance(self, word):
        distance_dict = {}
        print("entity matching for {}".format(word))
        for key, value in self.nodes.items():
            distance_dict[key.split("/")[-1]] = editdistance.eval(value, word)
        distance_dict = dict(sorted(distance_dict.items(), key=lambda x: x[1]))
        return distance_dict

    def calculate_pred_distance(self, related_word):
        pred_distance_dict = {}
        print("relation matching for {}".format(related_word))
        for key, value in self.predicates.items():
            pred_distance_dict[key.split("/")[-1]] = editdistance.eval(
                value, related_word
            )
        pred_distance_dict = dict(
            sorted(pred_distance_dict.items(), key=lambda x: x[1])
        )

        # don't comment this block
        try:
            del pred_distance_dict["rdf-schema#label"]
        except:
            pass

        return pred_distance_dict

    def forcely_search(self, question_list, is_when):
        for word in self.all_delete_words:
            try:
                question_list.remove(word)
            except:
                pass
        possible_word = copy.deepcopy(question_list)
        for i in range(len(possible_word)):
            possible_word[i] = (
                possible_word[i].replace("?", "").replace('"', "").replace("'", "")
            )

        possible_relation_word_first = possible_word[0]
        possible_entity_word_first = " ".join(possible_word[1:])
        possible_relation_word_last = possible_word[-1]
        possible_entity_word_last = " ".join(possible_word[0:-1])

        if is_when == 1:
            possible_relation_word_first += " time"
            possible_relation_word_last += +" time"

        possible_answer_list1 = self.search_answer_for_all_O(
            possible_entity_word_first, possible_relation_word_first
        )
        possible_answer_list2 = self.search_answer_for_all_O(
            possible_entity_word_last, possible_relation_word_last
        )

        possible_answer = []
        if len(possible_answer_list1) != 0:
            possible_answer = possible_answer_list1
        if len(possible_answer_list2) != 0:
            possible_answer = possible_answer_list2

        return possible_answer
