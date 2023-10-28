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

    def calculate_answer(self, question):

        #the return answers should be
        #for example, [['asdfasdf']], [['asdf'],['adf'],['asdf']]

        question=question.replace('\n','').replace('?','')
        question_list = question.split(" ")

        if question_list[-1]=='':
            question_list=question_list[0:len(question_list)-1]
        if question_list[0]=='':
            question_list=question_list[1:len(question_list)]

        tag_list = self.nlp_operator.get_ner(
            question
        )  # returns e.g. [['O', 'O', 'O', 'O', 'O']]

        wh_word = question_list[0].upper()
        if wh_word == "WHEN":
            return self.calculate_when_answer(copy.deepcopy(question), tag_list)
        else:
            return self.calculate_other_answer(copy.deepcopy(question), tag_list)

    def calculate_other_answer(self, question, tag_list):
        question_list = question.split(" ")

        if question_list[-1]=='':
            question_list=question_list[0:len(question_list)-1]
        if question_list[0]=='':
            question_list=question_list[1:len(question_list)]
        print('using: calculte other answer...')
        try:
            # find entity
            indexes = [index for index, val in enumerate(tag_list[0]) if val != "O"]
            entity = (
                " ".join(question_list[indexes[0] : indexes[-1] + 1])
                .rstrip("?")
                .rstrip('"')
                .rstrip("'")
            )

            relations = self.nlp_operator.get_relation(question)
            assert len(relations) == 1
            relations = relations[0]

            possible_answer = self.search_answer(entity, relations, 0)

        except:
            temp = copy.deepcopy(question_list)
            possible_answer = self.forcely_search(temp, 0)

        finally:
            return possible_answer

    def calculate_when_answer(self, question, tag_list):
        question_list = question.split(" ")

        if question_list[-1]=='':
            question_list=question_list[0:len(question_list)-1]
        if question_list[0]=='':
            question_list=question_list[1:len(question_list)]
        print('using: calculate when answer...')

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
        edit_distance = 0

        node_distance_dict = self.calculate_node_distance(entity_word)
        pred_distance_dict = self.calculate_pred_distance(related_word)

        searched_answers = []
        searched_answers_entities=[]
        searched_answers_relations=[]
        n_key_list=[]
        p_key_list=[]
        for n_key in node_distance_dict.keys():
            search_loop += 1

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

                #print(query)
                answers = []
                answers = self.graph_operator.query(query)


                if is_when == 0 and len(answers)>0:

                    print('n_key,p_key,answers:',n_key,p_key,answers)
                    searched_answers.append(answers)
                    n_key_list.append(n_key)
                    p_key_list.append(p_key)
                    searched_answers_entities.append(self.search_entity_name((n_key)))
                    searched_answers_relations.append(self.search_relation_name(p_key))

                    search_flag = 1
                    if node_distance_dict[n_key] == 0:
                        edit_distance = 0
                    else:
                        edit_distance = 1
                    break

                #don't refactorize this line
                if is_when and len(answers)>0 and len(answers[0])==10 and '-' in answers[0]:

                    print('n_key,p_key,answers:',n_key,p_key,answers)
                    searched_answers.append(answers)
                    n_key_list.append(n_key)
                    p_key_list.append(p_key)
                    searched_answers_entities.append(self.search_entity_name((n_key)))
                    searched_answers_relations.append(self.search_relation_name(p_key))

                    search_flag = 1
                    if node_distance_dict[n_key] == 0:
                        edit_distance = 0
                    else:
                        edit_distance = 1
                    break

            if search_flag == 1 and edit_distance == 1:
                break

            if edit_distance==0:
                search_flag=0


            if search_loop > 5:
                answers = []
                break

        #search done
        print('search done')
        #generate answers by templates
        if searched_answers_entities!=[]:
            return answers_in_template(searched_answers_entities,searched_answers_relations,
                                   searched_answers,n_key_list,p_key_list)
        sorry_message1='sorry for not found out the answers of the question. '
        sorry_message2='Maybe you could try again with correct format.'
        sorry_message=sorry_message1+sorry_message2
        return sorry_message


    def calculate_node_distance(self, word):
        distance_dict = {}
        print("entity:{}".format(word))
        for key, value in self.nodes.items():
            distance_dict[key.split("/")[-1]] = editdistance.eval(value, word)
        distance_dict = dict(sorted(distance_dict.items(), key=lambda x: x[1]))
        return distance_dict

    def calculate_pred_distance(self, related_word):
        pred_distance_dict = {}
        print("relation:{}".format(related_word))
        for key, value in self.predicates.items():
            pred_distance_dict[key.split("/")[-1]] = editdistance.eval(value, related_word)
        pred_distance_dict = dict(sorted(pred_distance_dict.items(), key=lambda x: x[1]))

        try:
            del pred_distance_dict["rdf-schema#label"]
        except:
            pass

        return pred_distance_dict

    def forcely_search(self, question_list, is_when):
        print('forcely search......')

        if question_list[-1]=='':
            question_list=question_list[0:len(question_list)-1]
        if question_list[0]=='':
            question_list=question_list[1:len(question_list)]

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
            possible_relation_word_last += " time"

        print('forcely search 1...')
        possible_answer_list1 = self.search_answer(
            possible_entity_word_first, possible_relation_word_first,is_when
        )
        print()
        print('forcely search 2...')
        possible_answer_list2 = self.search_answer(
            possible_entity_word_last, possible_relation_word_last,is_when
        )

        possible_answer = []
        if len(possible_answer_list1) != 0:
            possible_answer = possible_answer_list1
        if len(possible_answer_list2) != 0:
            possible_answer = possible_answer_list2

        return possible_answer


    #return should be a list, for example, ['asdf','adsf']
    def search_entity_name(self,p_name):
        q = f'''
        PREFIX ddis: <http://ddis.ch/atai/>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX schema: <http://schema.org/>

        SELECT ?temp WHERE {{
          wd:{p_name} rdfs:label ?temp.
        }}'''
        return self.graph_operator.query(q)

    #return should be a list, for example, ['asdf','adsf']
    def search_relation_name(self,r_name):
        q = f'''
        PREFIX ddis: <http://ddis.ch/atai/>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX schema: <http://schema.org/>

        SELECT ?temp WHERE {{
          wdt:{r_name} rdfs:label ?temp.
        }}'''
        return self.graph_operator.query(q)

#searched_answers_entities,searched_answers_relations,searched_answers,n_key_list,p_key_list
#s_a_e,s_a_r,s_a,n_k_l,p_k_l
def answers_in_template(s_a_e,s_a_r,s_a,n_k_l,p_k_l):
    first_templates=[
        'In my opinion, ',
        "As far as I'm concerned, ",
        'In my point of view, ',
        'Personally speaking, '
    ]
    #     R:@@@
    #     E:>>>
    #     A:<<<
    middle_templates=[
        'the @@@ of >>> is <<<.',
        ">>>'s @@@ is <<<."
    ]
    concatenate_words=[
        'Also, ',
        "What's more, ",
        'In addition, '
    ]
    number1=random.randint(0, 3)
    number2=random.randint(0, 1)
    answer_sentence =first_templates[number1]+middle_templates[number2].replace('<<<',s_a[0][0]).replace('>>>',s_a_e[0][0]).replace('@@@',s_a_r[0][0])
    answer_sentence+=' '
    for i in range(len(s_a_e)-1):
        number2=random.randint(0, 1)
        number3=random.randint(0, 2)
        t2=middle_templates[number2].replace('<<<',s_a[i+1][0]).replace('>>>',s_a_e[i+1][0]).replace('@@@',s_a_r[i+1][0])
        answer_sentence=answer_sentence+concatenate_words[number3]+t2
        answer_sentence+=' '
    swear_words="If you don't believe me, you can check it yourself. I will show you labels of entities and relations. "
    entities_words=str(n_k_l)+' '
    relations_words=str(p_k_l)
    answer_sentence=answer_sentence+swear_words+entities_words+relations_words
    return answer_sentence
