import pandas as pd
import numpy as np
import json
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split
import sklearn_crfsuite
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics
from collections import Counter

#extract features from sentence
def word2features(sent, i):
    word = str(sent[i])
    features = {
        'bias': 1.0, 
        'word.lower()': word.lower(), 
        'word[-3:]': word[-3:],
        'word[-2:]': word[-2:],
        'word.isupper()': word.isupper(),
        'word.istitle()': word.istitle(),
        'word.isdigit()': word.isdigit()
    }
    

    if i > 0:
        word1 = str(sent[i-1])
        features.update({
            '-1:word.lower()': word1.lower(),
            '-1:word.istitle()': word1.istitle(),
            '-1:word.isupper()': word1.isupper()
        })
    else:
        features['BOS'] = True

        
    if i > 1:
        word1 = str(sent[i-2])
        features.update({
            '-2:word.lower()': word1.lower(),
            '-2:word.istitle()': word1.istitle(),
            '-2:word.isupper()': word1.isupper()
        }) 
        
        
    if i < len(sent)-1:
        word1 = str(sent[i+1])
        features.update({
            '+1:word.lower()': word1.lower(),
            '+1:word.istitle()': word1.istitle(),
            '+1:word.isupper()': word1.isupper()
        })
    else:
        features['EOS'] = True
        
        
    
    #extract features from 2 next words
    if i < len(sent)-2:
        word1 = str(sent[i+2])
        features.update({
            '+2:word.lower()': word1.lower(),
            '+2:word.istitle()': word1.istitle(),
            '+2:word.isupper()': word1.isupper()
        })
    


    features['position']=np.sin(i)
    return features

#get sentence from ner_dataset.csv
class SentenceGetter_ner(object):
    
    def __init__(self, data):
        self.n_sent = 1
        self.data = data
        self.empty = False
        agg_func_x = lambda s: [w for w in s['word'].values.tolist()]
        agg_func_y = lambda s: [[p, t] for p, t in zip(s['pos'].values.tolist(),s['tag'].values.tolist())]
        
        self.grouped_x = self.data.groupby('sentence_idx').apply(agg_func_x)
        self.grouped_y = self.data.groupby('sentence_idx').apply(agg_func_y)
        self.x=[s for s in self.grouped_x]
        self.y=[s for s in self.grouped_y]

#get sentence from ner.csv
class SentenceGetter_nerdataset(object):
    
    def __init__(self, data):
        self.n_sent = 1
        self.data = data
        self.empty = False
        agg_func_x = lambda s: [w for w in s['Word'].values.tolist()]
        agg_func_y = lambda s: [[p, t] for p, t in zip(s['POS'].values.tolist(),s['Tag'].values.tolist())]
        
        self.grouped_x = self.data.groupby('Sentence #').apply(agg_func_x)
        self.grouped_y = self.data.groupby('Sentence #').apply(agg_func_y)
        self.x=[s for s in self.grouped_x]
        self.y=[s for s in self.grouped_y]



#the same as the codes in tutorial
def sent2features(sent_x):
    return [word2features(sent_x, i) for i in range(len(sent_x))]
def sent2labels(sent_y):
    return [label for postag, label in sent_y]
def sent2postag(sent_y):
    return [postag for postag, label in sent_y]

#get sentences from the csv files
n_df = pd.read_csv('ner.csv',encoding='cp1252')
getter = SentenceGetter_ner(n_df)
big_sentence_x = getter.x
big_sentence_y=getter.y

df = pd.read_csv('ner_d.csv', encoding = "ISO-8859-1")
df = df.fillna(method='ffill')
getter = SentenceGetter_nerdataset(df)
sentence_x = getter.x
sentence_y = getter.y


#delete repeated sentences here

#this function check all sentences in sentence_list and
#obverse if they are the same as sentence
#if yes, delete it
def delete_repeated_sentence(sentence,sentence_list,y_sentence_list):
    for i in range(len(sentence_list)):
        if sentence_list[i]==sentence:
            del sentence_list[i],y_sentence_list[i]
            break
    return

for i in range(len(sentence_x)):
    delete_repeated_sentence(sentence_x[i],big_sentence_x,big_sentence_y)



#delete repeated sentences in the same list
t=0
def delete_repeated_sentence_in_a_list(sentence_x,sentence_y):
    global t
    for i in range(len(sentence_x)):
        for j in range(i+1,len(sentence_x)):
            if sentence_x[i]==sentence_x[j]:
                del sentence_x[j],sentence_y[j]
                break
    t=1
    return t
while(t==0):
    delete_repeated_sentence_in_a_list(sentence_x,sentence_y)

t=0
while(t==0):
    delete_repeated_sentence_in_a_list(big_sentence_x,big_sentence_y)


#in fact, it's time-consuming to deal with the sentences
#if it's a huge dataset, we should save the preprocessed data into a pickle file
#so when we want to train the model next time, just read the preprocessed data
#from the file

#but I am lazy so it's good


#prepare X,y
#y2 here are useless because we won't use them
X = [sent2features(s) for s in big_sentence_x]
y1 = [sent2labels(s) for s in big_sentence_y]
y2 = [sent2postag(s) for s in big_sentence_y]


X = X+[sent2features(s) for s in sentence_x]
y1 = y1+[sent2labels(s) for s in sentence_y]
y2 = y2+[sent2postag(s) for s in sentence_y]



#split the dataset
#in fact, you could change the ratios if you want
train_length=int(len(X)*0.75)


x_train_set=X[0:train_length]
y1_train_set=y1[0:train_length]
y2_train_set=y2[0:train_length]

x_test_set=X[train_length:]
y1_test_set=y1[train_length:]
y2_test_set=y2[train_length:]


#train
crf = sklearn_crfsuite.CRF(
    algorithm='lbfgs',
    c1=0.1,
    c2=0.1,
    max_iterations=300,
    all_possible_transitions=True
)
try:
    crf.fit(x_train_set, y1_train_set)
except:
    pass

y_pred = crf.predict(x_test_set)

#calculate accuracy
t_pred=[]
t_test=[]
for x in y_pred:
    t_pred.extend(x)
    
for x in y1_test_set:
    t_test.extend(x)

n_test=[]
n_pred=[]
for i in range(len(t_pred)):
    if t_pred[i]==t_test[i] and t_pred[i]=='O':
        pass
    else:
        n_test.append(t_test[i])
        n_pred.append(t_pred[i])

#print(f1_score(t_pred, t_test, average="micro"))
n_pred=np.array(n_pred)
n_test=np.array(n_test)
correct=len(n_test[n_pred==n_test])
all_cases=len(n_test)

print(correct)
print(all_cases)
print('acc:',correct/all_cases)


import joblib

# save
joblib.dump(crf, "model_crf_without_repeat.pkl") 
# load
crf = joblib.load("model_crf_without_repeat.pkl")

#check the model whether it could work correctly
question="Who is the screenwriter of The Masked Gang: Cyprus?"
question=question.split(' ')
print(question)
q_x=[sent2features(question)]
q_y = crf.predict(q_x)
print(q_y)