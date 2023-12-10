from usecases.bot_base import Agent
from usecases.graph_operations import GraphOperations

def main():
    bot = Agent("burn-largo-coffee_bot", "Q9R_PM3LJyRDfQ")
    bot.listen()
    # graph = GraphOperations()
    # actual_value = graph._check_entity_type(graph.ent2id[graph.WD['Q10858674']], graph.WDT['P31'])
    # print(actual_value)


if __name__ == "__main__":
    main()
