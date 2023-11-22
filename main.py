from usecases.bot_base import Agent
from usecases import recommendations


def main():
    bot = Agent("burn-largo-coffee_bot", "Q9R_PM3LJyRDfQ")
    bot.listen()
    # recommendor = recommendations.Recommendations()
    # movies = recommendor.recommend_movies(['The Nightmare on Elm Street', 'Friday the 13th', 'Halloween'], 3)
    # answer = recommendor.recommend_answers(movies)
    # recommendation_text = recommendor.generate_answers_for_recommendation(answer)
    # print(recommendation_text)


if __name__ == "__main__":
    main()
