from usecases.bot_base import Agent
from usecases.multimedia import Multimedia
from usecases.graph_operations import GraphOperations
from usecases.answer_calculator2 import AnswerCalculator


def main():
    bot = Agent("burn-largo-coffee_bot", "Q9R_PM3LJyRDfQ")
    bot.listen()
    # ac = AnswerCalculator()
    # # ac.handle_multimedia(["Angelina Jolie"], ["ACTOR"])
    # while True:
    #     print("What do you want to know?")
    #     question = input()
    #     answer = ac.calculate_answer(question)
    #     print(answer)


if __name__ == "__main__":
    main()
