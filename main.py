from usecases.bot_base import Agent
from usecases.answer_calculator2 import AnswerCalculator
from usecases.graph_operations import GraphOperations
from usecases.nlp_operations import NLP_Operations
from usecases.recommendations import Recommendations
import rdflib


def main():
    # bot = Agent("burn-largo-coffee_bot", "Q9R_PM3LJyRDfQ")
    # bot.listen()
    # nlp = NLP_Operations()
    # print(nlp.get_ner("I enjoy watching Jan Dara, Dry Wind, and Necrosis. What else would you recommend?"))
    answer_calc = AnswerCalculator()
    while True:
        try: 
            print("What would you like to know?\n")
            quest = input()
            if quest == "quit":
                break
            print(answer_calc.calculate_answer(quest))
        except:
            continue
    # print(answer_calc.handle_recommendation(["Jumanji", "Toy Story"]))
    # recommender = Recommendations()
    # test = ["Titaniic"]
    # movies = recommender.recommend_movies(test, 3)
    # answers = recommender.recommend_answers(movies)
    # print(recommender.generate_answers_for_recommendation(answers))
    # graph_op = GraphOperations()
    # print(graph_op.recommendations_embeddings(["Q102225", "Q161678"]))


if __name__ == "__main__":
    main()
