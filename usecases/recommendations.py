import pandas as pd
import random
from fuzzywuzzy import process
from collections import Counter


class Recommendations:
    def __init__(self, data="./data/movies.csv"):
        self.movie_df = pd.read_csv(data, usecols=["title", "genres"])
        self.liked_movies = []
        self.preprocess()

    def preprocess(self):
        self.movie_titles = [
            " ".join(x.split(" ")[:-1]) for x in self.movie_df["title"].tolist()
        ]
        self.movie_times = [
            x.split(" ")[-1][1:5] for x in self.movie_df["title"].tolist()
        ]
        self.movie_genres = [x.split("|") for x in self.movie_df["genres"].tolist()]

    def check_genres_in_list(self, genres_1, genres_2):
        for g in genres_1:
            if g in genres_2:
                return 1
        return 0

    def recommend_movies(self, movies, n):
        self.liked_movies = movies
        number_of_all_movies = len(self.movie_titles)

        movie_index = []
        for movie in movies:
            threshold = 90
            match, similarity = process.extractOne(movie, self.movie_titles)
            if similarity >= threshold:
                movie_index.append(self.movie_titles.index(match))
            else:
                print(f"{movie} was not found or no close match found")

        assert movie_index, "I could'nt find any movies for you, sry!"

        movie_r_time = []
        movie_r_genres = []
        for i in movie_index:
            movie_r_time.append(self.movie_times[i])
            movie_r_genres.append(self.movie_genres[i])

        genres_counter = Counter()
        for l in movie_r_genres:
            for item in l:
                genres_counter.update({item: 1})

        genres_counter = dict(
            sorted(genres_counter.items(), key=lambda item: item[1], reverse=True)
        )
        movie_r_time = list(set(movie_r_time))

        time_r_list = movie_r_time[:n]
        genres_r_list = list(genres_counter)[:n]

        search_answers_index = []
        search_answers_number = 0
        recommend_reason = -1

        # best: time and genres both pass
        for i in range(number_of_all_movies):
            if (
                self.movie_times[i] in time_r_list
                and self.check_genres_in_list(self.movie_genres[i], genres_r_list)
                and self.movie_titles[i] not in movies
            ):
                search_answers_number += 1
                search_answers_index.append(i)
                if search_answers_number == n:
                    break

        if search_answers_index:
            recommend_reason = 0
            return search_answers_index, recommend_reason

        # only considering genres
        for i in range(number_of_all_movies):
            if (
                self.check_genres_in_list(self.movie_genres[i], genres_r_list)
                and self.movie_titles[i] not in movies
            ):
                search_answers_number += 1
                search_answers_index.append(i)
                if search_answers_number == n:
                    break

        if search_answers_index:
            recommend_reason = 2
            return search_answers_index, recommend_reason

        # only considering time
        for i in range(number_of_all_movies):
            if (
                self.movie_times[i] in time_r_list
                and self.movie_titles[i] not in movies
            ):
                search_answers_number += 1
                search_answers_index.append(i)
                if search_answers_number == n:
                    break

        if search_answers_index:
            recommend_reason = 1
            return search_answers_index, recommend_reason
        else:
            print("no answers have been found")

        return search_answers_index, recommend_reason

    def recommend_answers(self, search_answers_outcomes):
        search_answers_index, recommend_reason = search_answers_outcomes
        movie_list = [self.movie_titles[x] for x in search_answers_index]
        time_list = [self.movie_times[x] for x in search_answers_index]
        genres_list = [self.movie_genres[x] for x in search_answers_index]

        recommend_categories = ""
        whether_found = recommend_reason == -1
        if recommend_reason == -1:
            recommend_categories = "have not been found, so no reasons"
        elif recommend_reason == 0:
            recommend_categories = "all the movies were published in the same year and the genres are the same"
        elif recommend_reason == 1:
            recommend_categories = "all the movies were published in the same year"
        elif recommend_reason == 2:
            recommend_categories = "all the movies are the same genres"
        return movie_list, time_list, genres_list, recommend_categories, whether_found

    def generate_answers_for_recommendation(self, search_answers_outcomes):
        (
            movie_list,
            time_list,
            genres_list,
            recommend_categories,
            whether_found,
        ) = search_answers_outcomes
        time_set = set(time_list)
        genres_set = set()
        for genres in genres_list:
            genres_set.update(genres)

        if whether_found:
            return "no answers have been found, try again."
        else:
            answers1 = [
                "Adequate recommendations will be: {}, because {}.".format(
                    ", ".join(movie_list), recommend_categories
                ),
                f"Since you like {', '.join(self.liked_movies)}, I think you would enjoy {', '.join(movie_list)}, because {recommend_categories}."
            ]
            answer2 = " The details about the movies are shown as follows: "
            answer3 = "the publication date of all movies is {} and the genres of all movie are {}.".format(
                ", ".join(time_set), ", ".join(genres_set)
            )
            return answers1[random.randint(0, len(answers1) - 1)] + answer2 + answer3
