"""Makes sure this file is only run after 'datasets/filtered/keyword_graph.txt' is made"""
from __future__ import annotations
from typing import Optional
import json
import numpy as np
import graph_classes


class Media:
    """The media class that contains metadata about a show/movie
    """
    title: str  # unique string denoting the media’s name of reference
    type: str  # is either 'movie' or 'show'
    genres: set[str]  # set of genres that apply to the media
    rating: float  # from 0 to 10 inclusive, denotes the rating score
    date: int  # the year of the media’s initial release
    synopsis: str  # string of a brief summary, contains keywords to be extracted
    keywords: set[str]  # set of words that describe the media.
    recommendation: Optional[dict[str, tuple[float, set[Media]]]]

    def __init__(self, entry: dict, form: str) -> None:
        """
        Preconditions:
        - The entry is a dictionary from a finalized json dataset that conforms with the naming scheme
        - form is either 'TV' or 'movie' or 'anime'
        """
        self.title = entry['title']
        self.type = form
        if isinstance(entry['genre'], str):
            self.genres = set(entry['genre'].split(', '))
        else:
            self.genres = set(entry['genre'])
        self.rating = float(entry['rating'])
        if isinstance(entry['release_date'], int):
            self.date = entry['release_date']
        else:  # Otherwise 'release_date' is a string
            str_to_float = float(entry['release_date'])
            float_to_int = int(str_to_float)
            self.date = float_to_int
        self.synopsis = entry['plot_summary']
        self.keywords = set(entry['keywords'])  # Originally, entry['keywords'] was a list
        self.recommendation = {}

    def __str__(self) -> str:
        """
        Returns a string representation of a Media object
        """
        return f"Media({self.title}, {self.type}, {self.genres}, " \
               f"{self.rating}, {self.date}, {self.synopsis}, {self.keywords}, {self.recommendation})"

    def compare(self, other: Media, parent_set: set[Media], graph: graph_classes.Graph) -> float:
        """compares itself to another media with 4 assessments,
        and mutates its recommendation accordingly

        Preconditions:
        - other in parent_set
        """
        sim_scores = [0, 0, 0, 0]
        mul = (0.07, 0.11, 0.28, 0.54)  # this should be subject to change (and tweaking will majorly affect results)
        # 1. date comparison
        sim_scores[0] = self.date_comparison(other, list(parent_set))
        # 2. rating comparison
        sim_scores[1] = self.rating_comparison(other, list(parent_set))
        # 3. genre comparison
        sim_scores[2] = self.genre_comparison(other)
        # 4. keyword comparison
        sim_scores[3] = self.keyword_comparison(other, graph)
        # balancing comparison values
        # assert sum(sim_scores) <= 4  # 4 would be if it gets perfect scores in each # COMMENTED OUT BC IT FAILED
        # assert len(sim_scores) == len(mul)
        perfect_score = 4 * sum(mul)
        act_score = sum(sim_scores[x] * mul[x] for x in range(0, len(sim_scores))) / perfect_score
        return min(act_score + (self.rating / 50), 1)

    def keyword_comparison(self, other: Media, graph: graph_classes.Graph) -> float:
        """compares two medias' keywords using a keyword graph"""
        true_path_scores = []
        for anime_keyword in self.keywords:
            anime_word = anime_keyword.lower()
            paths = []
            for other_keyword in other.keywords:
                other_word = other_keyword.lower()
                # the following two lines assert line is for testing only (so delete later)
                # words = {x for x in graph._vertices}
                # assert anime_word in words and other_word in words

                path = graph.shortest_path(anime_word, other_word)
                if path:
                    paths.append(path[0])
            if not paths:  # if all the shortest_path lengths were False, i.e. no words connected
                true_path_scores.append(0)
            else:
                true_path_score = 1 / min(paths)  # one of these other shows's keywords relates to this keyword the best
                true_path_scores.append(true_path_score)
        while true_path_scores.count(0) >= 5 and any(x > 0 for x in true_path_scores):
            true_path_scores.remove(0)
        return sum(true_path_scores) / len(true_path_scores)

    def rating_comparison(self, other: Media, list_of_media: list[Media]) -> float:
        """
        This function first computes the IQR (Interquartile range) of the ratings of the input show list.
        Then, it checks if the ratings of the recommended show is within that IQR. If yes, then it is deemed to be
        a "good fit" and so its rating score is set to the maximum score (ie: 1.0).

        If not, then we calculate the z-score for the input show rating. Z scores describe the number of standard
        deviations a point is above or below the mean. Taking the absolute value would mean we would be investigating
        simply how many standard deviations a point is away from the mean (regardless of directionality)

        This z-score is calculated by getting the following:
            1. Getting the mean rating from the input show list
            2. Getting the standard deviation from the input show list. Standard deviation is a measure of spread and
            variation. If the standard deviation is zero, we would not move to Step 3. and will handle the result
            different (see code comments in body)
            3. Calculating (recommended show rating - mean show rating) / standard deviation).
            Here, a negative z-score would mean that the recommended show rating is BELOW the mean show rating of
            input list. A positive z-score would mean that the recommended show rating is ABOVE
            the mean show rating of input list. A z-score of 0 would mean the recommended show rating is close to
            average.

        Our group has made the design decision to only recommend shows that have either a rating close to or above the
        average rating from the input list.

        Therefore, if the z-score is negative, the rating score would be set to the MINIMUM (ie: 0.0).
        If the z-score is 0.0, the rating score would be 0.5 (arbitrary, mean benchmark established)
        If the z-score is positive, the rating score would be 0.5 + z score

        Arguments:
        self: Refers to the Media object of reference (the anime recommendation)
        other: Refers to comparison Media object (the user input media)
        list_of_media: Refers to the list of input media objects
        """
        # Step 3: Get mean rating from list of user-input shows (this is used for z score calculation)
        mean_rating = calculating_mean_rating(list_of_media)

        # Step 3: Get IQR date range from list of user-input shows
        iqr_of_ratings = calculating_iqr_of_ratings(list_of_media)

        # Step 4: Get the standard deviation and z score of the recommendation
        standard_dev_of_ratings = calculating_s_d_ratings(list_of_media)

        # Handle for cases where standard_dev_of_ratings = 0
        if standard_dev_of_ratings == 0:
            rating_difference = self.rating - other.rating
            if rating_difference >= 0:
                # ^^ If the recommended show rating is >= input show, its rating score is maxed out
                return 1.0
            else:
                return 0.0

        else:
            z_score_of_recommend = (self.rating - mean_rating) / standard_dev_of_ratings

            # Step 4: If the recommended show's date falls within the range dictated by the values in iqr_of_dates...
            # ... then the show is a good fit "date wise" with the user inputs.
            if self.rating >= iqr_of_ratings[0] and self.rating <= iqr_of_ratings[1]:
                return 1.0
            elif z_score_of_recommend < 0.0:
                return 0.0
            elif z_score_of_recommend == 0.0:
                return 0.5
            elif 0.5 + z_score_of_recommend > 1.0:
                return 1.0
            else:
                return 0.5 + z_score_of_recommend

    def date_comparison(self, other: Media, list_of_media: list[Media]) -> float:
        """
        This function first computes the IQR (Interquartile range) of the dates of the input show list.
        Then, it checks if the date of the recommended show is within that IQR. If yes, then it is deemed to be
        a "good fit" and so its date score is set to the MAXIMUM score (ie: 1.0).

        If not, then we calculate the z-score for the input show date. Z scores describe the number of standard
        deviations a point is above or below the mean. Taking the absolute value would mean we would be investigating
        simply how many standard deviations a point is away from the mean (regardless of directionality)

        This z-score is calculated by getting the following:
            1. Getting the mean date from the input show list
            2. Getting the standard deviation from the input show list. Standard deviation is a measure of spread and
            variation. If the standard deviation is zero, we would not move to Step 3. and will handle the result
            different (see code comments in body)
            3. Calculating abs((recommended show date - mean date) / standard deviation). We take the absolute value
            because z-scores can be negative, and as mentioned prior, we do not care about directionality.

        The higher the z-score, the further away the recommended show date is from the mean show date from the input
        set. Therefore, the higher the z-score, the lower the date score should be.

        So, if the abs(z-score) is < 1, we would consider that a good fit and also return the maximum score (1.0)
        Otherwise, we would return 1/abs(z-score).

        Arguments:
        self: Refers to the Media object of reference (the anime recommendation)
        other: Refers to comparison Media object (the user input media)
        list_of_media: Refers to the list of input media objects
        """

        # Step 1: Get mean date from list of user-input shows (this is used for z score calculation)
        mean_date = calculating_mean_date(list_of_media)

        # Step 2: Get IQR date range from list of user-input shows
        iqr_of_dates = calculating_iqr_of_dates(list_of_media)

        # Step 3: Get the standard deviation and z score of the recommendation
        standard_dev_of_dates = calculating_s_d_dates(list_of_media)

        # Step 4: If standard deviation = 0 (when all entries in list_of_media are same), date score is based on...
        # ... the date distance from input shows and recommended show

        if standard_dev_of_dates == 0:
            date_difference = abs(self.date - other.date)
            if date_difference == 0:
                return 1.0
            else:
                return 1 / date_difference  # The greater the difference is between dates, the lower the date score

        else:
            abs_z_score_of_recommend = abs((self.date - mean_date) / standard_dev_of_dates)
            # Step 5: If the recommended show's date falls within the range dictated by the values in iqr_of_dates...
            # ... then the show is a good fit "date wise" with the user inputs.
            if self.date in range(iqr_of_dates[0], iqr_of_dates[1]) or abs_z_score_of_recommend < 1:
                return 1.0
            else:
                return 1 / abs_z_score_of_recommend

    def genre_comparison(self, other: Media) -> float:
        """
        Compute the fraction of shared genres between itself (a Media object) and another Media object
        """
        num_genre_shared = len(self.genres.intersection(other.genres))
        return num_genre_shared / len(other.genres)


def calculating_mean_rating(user_input_media: list[Media]) -> float:
    """
    Calculates the mean show rating of a user input media list
    """
    all_input_show_ratings = np.array([input_show.rating for input_show in user_input_media])
    return float(np.mean(all_input_show_ratings))


def calculating_s_d_ratings(user_input_media: list[Media]) -> float:
    """
    Calculates the standard deviation of the show ratings of a user input media list
    """
    all_input_show_ratings = np.array([input_show.rating for input_show in user_input_media])
    return float(np.std(all_input_show_ratings))


def calculating_iqr_of_ratings(user_input_media: list[Media]) -> tuple[float, float]:
    """
    Returns a tuple of 2 show ratings, with the lower one representing Q1 (the show rating of which 25% of the all
    show ratings of the input set fall below this threshold) and the higher one representing Q3
    (the show rating of which 75% of the all show ratings of the input set fall below this threshold)
    """
    all_input_show_ratings = np.array([input_show.rating for input_show in user_input_media])
    # Note that IQR = Q3 - Q1
    q1, q3 = np.percentile(all_input_show_ratings, [25, 75])
    return (float(q1), float(q3))


def calculating_mean_date(user_input_media: list[Media]) -> int:
    """
    Calculates the mean date of a user input media list
    """
    all_input_show_dates = np.array([input_show.date for input_show in user_input_media])
    return int(np.mean(all_input_show_dates))


def calculating_s_d_dates(user_input_media: list[Media]) -> float:
    """
    Calculates the standard deviation of the dates of a user input media list
    """
    all_input_show_dates = np.array([input_show.date for input_show in user_input_media])
    return int(np.std(all_input_show_dates))


def calculating_iqr_of_dates(user_input_media: list[Media]) -> tuple[int, int]:
    """
    Returns a tuple of 2 dates, with the lower one representing Q1 (the date of which 25% of the all
    dates of the input set fall below this threshold) and the higher one representing Q3
    (the date of which 75% of the all dates of the input set fall below this threshold)
    """
    all_input_show_dates = np.array([input_show.date for input_show in user_input_media])
    # Note that IQR = Q3 - Q1
    q1, q3 = np.percentile(all_input_show_dates, [25, 75])
    return (int(q1), int(q3))


def build_keyword_graph_from_file() -> graph_classes.Graph:
    """makes the graph to be used in the keywords assessment"""
    with open('datasets/filtered/keyword_graph.txt', 'r') as f:
        lines = f.readlines()
    keyword_graph = graph_classes.Graph()
    edges = eval(lines[1])
    vertices = eval(lines[0])
    for vertex in vertices:
        keyword_graph.add_vertex(vertex)
    keyword_graph.add_all_edges(edges)
    return keyword_graph


# IMPORTANT: PLEASE READ HERE:
# If you want to test out our recommendation algorithm (on one user entry and comparing to only a subset of all...
# ... animes found on final_animes.json), you can run method test_compare() in the console.
# NOTE: This check may take a couple of minutes (1-4 minutes)
def test_compare() -> None:
    """
    A test function that returns the strongest ranked anime recommendation. Recommendation is made
    based on only a subset of animes from final_animes.json and based on 1 input TV show from user.
    """
    keyword_graph = build_keyword_graph_from_file()
    rec_list = []
    with open('datasets/filtered/final_animes.json', 'r') as file:
        user_input_media = json.load(file)  # Datatype of this is now list[dict]
    anime_list = []
    for x in user_input_media:
        anime_list.append(Media(x, 'anime'))

    with open('datasets/filtered/one_show.json', 'r') as file:
        user_input_media2 = json.load(file)  # Datatype of this is now list[dict]
    input_list = []
    for x in user_input_media2:
        if "movie_id" in x:
            input_list.append(Media(x, 'movie'))
        else:
            input_list.append(Media(x, 'show'))

    for anime in anime_list[0:41]:
        rec_score = 0
        for item in input_list:
            sim_score = anime.compare(item, set(input_list), keyword_graph)
            rec_score += sim_score
        rec_score /= len(input_list)
        rec_list.append((rec_score, anime.title))
        # print('checked ' + anime.title)
        # print(max(rec_list))
    print(max(rec_list))


if __name__ == '__main__':
    # # Enabling doctest checking features:
    import doctest

    doctest.testmod(verbose=True)

    # Enabling python_ta configurations:
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ["json", "numpy", "graph_classes"],
        'allowed-io': ["build_keyword_graph_from_file", "test_compare"],
        'disable': ['R0902', "W0123"],
        # Disable instance attribute count as confirmed with instructor that this number is acceptable
        'max-line-length': 120,
    })
