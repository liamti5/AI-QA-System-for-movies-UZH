import rdflib
from models import NER_CRF
import spacy
import json
import editdistance
import copy

nlp = spacy.load("en_core_web_sm")

'''
calculate_answer: use the other 2 functions to deal with "when" questions and other questions
(calculate_other_answer,calculate_when_answer)

search_answer: if everything goes well, namely we have found the entity and the relation,
then we should handle the question which has maybe many answers
for example: The "godfather" questions


search_answer_for_all_O: if everything goes badly, namely we haven't found the entity and the relation,
pray we could find an answer and one answer is enough, pray it's right
'''


graph = rdflib.Graph()



wh_words=['What','what','when','When','where','Where','Who','who',
          'Whom','whom','Which','which','Whose','whose','Why','why',
          'How','how']
useless_words=['am','is','are','was','were','a','an','the','that','this','these','those',
            'above','across','against','along','among','around','at','before','behind',
            'below','beneath','beside','between','by','down','from','in','into',
            'near','off','on','to','woward','under','upon','with','and','within','of',
            'for','since','during','over']

all_delete_words=wh_words+useless_words


def get_nodes():
    with open('data/nodes.json', 'r') as f:
        nodes = json.load(f)
    return nodes


def get_predicates():
    with open('data/predicates_clean.json', 'r') as f:
        predicates = json.load(f)    
    return predicates


nodes = get_nodes()
predicates = get_predicates()


def calculate_node_distance(entity):
    node_distance_dict={}
    tmp = 9999
    match_node = ""
    print("entity matching for {}".format(entity_word))
    for key, value in nodes.items():
        node_distance_dict[key.split('/')[-1]]=editdistance.eval(value, entity_word)
    node_distance_dict=dict(sorted(node_distance_dict.items(), key=lambda x:x[1]))
    return node_distance_dict



def calculate_pred_distance(related_word):
    pred_distance_dict={}
    tmp = 9999
    match_pred = ""
    print("relation matching for {}".format(related_word))
    for key, value in predicates.items():
        pred_distance_dict[key.split('/')[-1]]=editdistance.eval(value, related_word)
    pred_distance_dict=dict(sorted(pred_distance_dict.items(), key=lambda x:x[1]))

    #don't comment this block
    try:
        del pred_distance_dict['rdf-schema#label']
    except:
        pass

    return pred_distance_dict


def forcely_search(question_list,is_when):
    for word in all_delete_words:
        try:
            question_list.remove(word)
        except:
            pass
    possible_word=copy.deepcopy(question_list)
    for i in range(len(possible_word)):
        possible_word[i]=possible_word[i].replace('?','').replace('"','').replace("'",'')

    possible_relation_word_first=possible_word[0]
    possible_entity_word_first=' '.join(possible_word[1:])
    possible_relation_word_last=possible_word[-1]
    possible_entity_word_last=' '.join(possible_word[0:-1])

    if is_when==1:
        possible_relation_word_first+=' time'
        possible_relation_word_last+=+' time'

    possible_answer_list1=search_answer_for_all_O(possible_entity_word_first,possible_relation_word_first,is_when)
    possible_answer_list2=search_answer_for_all_O(possible_entity_word_last,possible_relation_word_last,is_when)
    
    possible_answer=[]
    if len(possible_answer_list1)!=0:
        possible_answer=possible_answer_list1
    if len(possible_answer_list2)!=0:
        possible_answer=possible_answer_list2

    return possible_answer

def load_graph():
    print('loading graph')
    graph.parse('data/14_graph.nt', format='turtle')
    print('loaded graph successfully')


def query(message):
    # remember to delete these 2 lines after this boring evaluation
    message = message.replace('"""', '').replace("'''", '')
    print('message in sparql')
    message = str(message)
    print(message)
    temp = [str(s) for s, in graph.query(message)]
    return temp


def query2(message):
    return calculate_answer(message)


def calculate_answer(question):
    
    question_list = question.split(" ")
    ner = NER_CRF.get_ner(question)

    wh_word=question_list[0].upper()
    if wh_word=='WHEN':
        return calculate_when_answer(copy.deepcopy(question),ner[0])
    else:
        return calculate_other_answer(copy.deepcopy(question),ner[0])


def calculate_other_answer(question_list,tag_list):
    try: 
        #find entity  
        indexes = [index for index, val in enumerate(tag_list) if val != "O"]
        entity = " ".join(question_list[indexes[0]:indexes[-1]+1]).rstrip("?").rstrip('"').rstrip("'")

        #TODO: you should delete one line
        #find relations
        doc = nlp(question)
        relations = [tok.lemma_ for tok in doc if tok.dep_ in ('attr', 'nsubj') and tok.pos_ in ('NOUN')][0]

        assert len(relations) == 1
        relations=relations[0]
        
        possible_answer=[]
        possible_answer = search_answer(entity,relations,0)

    except:
        temp=copy.deepcopy(question_list)
        possible_answer=forcely_search(temp,0)
    
    return possible_answer

def calculate_when_answer(question_list,tag_list):
    try: 
        #find entity
        indexes = [index for index, val in enumerate(tag_list) if val != "O"]
        entity = " ".join(question_list[indexes[0]:indexes[-1]+1]).rstrip("?").rstrip('"').rstrip("'")

        entity_list=" ".join(question_list[indexes[0]:indexes[-1]+1]).split(' ')

        #delete entity word
        temp=copy.deepcopy(question_list)
        for word in entity_list:
            temp.remove(word)

        for word in all_delete_words:
            try:
                temp.remove(word)
            except:
                pass

        assert len(temp) == 1
        relations=temp[0]+' time'
        
        possible_answer=[]
        possible_answer = search_answer(entity,relations,1)

    except:
        temp=copy.deepcopy(question_list)
        possible_answer=forcely_search(temp,1)


    return possible_answer






def search_answer(entity,relations,is_when):
    search_loop=0
    search_flag=0
    edit_distance=1

    node_distance_dict=calculate_node_distance(entity_word)
    pred_distance_dict=calculate_pred_distance(related_word)

    searched_answers=[]
    for n_key in node_distance_dict.keys():
        search_loop+=1

        if node_distance_dict[n_key]==0:
            edit_distance=0
        else:
            edit_distance=1

        for p_key in pred_distance_dict.keys():
            query = f'''
    PREFIX ddis: <http://ddis.ch/atai/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX schema: <http://schema.org/>
    SELECT ?entity_name WHERE{{    
        wd:{n_key} wdt:{p_key} ?temp.
        ?temp rdfs:label ?entity_name.
    }}
    LIMIT 1
    '''
            
            answers = [str(s) for s, in g.query(query)]
            if len(answers)>0:
                if is_when and len(answers[0])==10:
                    search_flag=1
                else:
                    search_flag=1
            if search_flag==1:
                searched_answers.append(answers)
                break
        if search_flag==1 and edit_distance==1:
            break
        if search_loop>10:
            answers=[]
            break

    return searched_answers





def search_answer_for_all_O(entity_word,related_word,is_when):
    node_distance_dict=calculate_node_distance(entity_word)
    pred_distance_dict=calculate_pred_distance(related_word)
    
    search_flag=0

    #entity distance seems reliable, try 5 times
    try_times=0
    for n_key in node_distance_dict.keys():
        try_times+=1
        for p_key in pred_distance_dict.keys():
            query = f'''
    PREFIX ddis: <http://ddis.ch/atai/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX schema: <http://schema.org/>
    SELECT ?date WHERE{{    
        wd:{n_key} wdt:{p_key} ?date.
    }}
    LIMIT 1
    '''

            answers = [str(s) for s, in g.query(query)]
            if len(answers)>0:
                if is_when and len(answers[0])==10:
                    search_flag=1
                else:
                    search_flag=1
            if search_flag==1:
                break
        if search_flag==1:
            break
        if try_times>10:
            break
    return answers



#test this file
def main():
    #write test codes here
    pass

if __name__ == '__main__':
    main()
