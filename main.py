from usecases.bot_base import Agent
from usecases import recommendations


def main():
    bot = Agent("burn-largo-coffee_bot", "Q9R_PM3LJyRDfQ")
    bot.listen()


if __name__ == "__main__":
    main()
