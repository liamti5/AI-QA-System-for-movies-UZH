from usecases.bot_base import Agent
from usecases.answer_calculator2 import AnswerCalculator
from usecases.graph_operations import GraphOperations
import rdflib

def main():
    # bot = Agent("burn-largo-coffee_bot", "Q9R_PM3LJyRDfQ")
    # bot.listen()
    answer_calc = AnswerCalculator()
    quest = ["Who is the screenwriter of the The Masked Gang: Cyprus?", "When was Lord of the Rings released?", "When was The Masked Gang: Cyprus released?"]
    for q in quest:
        print(answer_calc.calculate_answer(q))


if __name__ == '__main__':
    main()
