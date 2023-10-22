import numpy as np
import joblib


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

    # extract features from 2 next words
    if i < len(sent)-2:
        word1 = str(sent[i+2])
        features.update({
            '+2:word.lower()': word1.lower(),
            '+2:word.istitle()': word1.istitle(),
            '+2:word.isupper()': word1.isupper()
        })

    features['position'] = np.sin(i)
    return features


def sent2features(sent_x):
    return [word2features(sent_x, i) for i in range(len(sent_x))]


def get_ner(question):
    crf = joblib.load("models/model_crf_without_repeat.pkl")
    question = question.split(' ')
    print(question)
    q_x = [sent2features(question)]
    q_y = crf.predict(q_x)
    return q_y


def main():
    question = "Who is the main actor in Harry Potter?"
    ner = get_ner(question)
    print(ner)


if __name__ == "__main__":
    main()
