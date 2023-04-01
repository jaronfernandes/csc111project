"""Makes sure this file is only run after 'datasets/filtered/keyword_graph.txt' is made"""
# TODO: media dataclass, compare function, other helper functions, read keywords graph function
from __future__ import annotations
from typing import Optional
import json
# NEW IMPORT
import numpy as np
import graph_classes


# Commented out this code as we have yet to generate keyword edges
# with open('datasets/filtered/keyword_graph.txt', 'r') as f:
#     lines = f.readlines()
# keyword_graph = graph_classes.Graph()
# edges = eval(lines[1])
# keyword_graph.add_all_edges(edges)

# # This section of the code is responsible for opening a json file and converting its contents to a dict
# with open('datasets/filtered/sample_input_mix.json', 'r') as file:
#     user_watch_list = json.load(file)


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
    recommendation: Optional[set[tuple[set[Media], float]]]

    def __init__(self, entry: dict, form: str) -> None:
        """
        Preconditions:
        - The entry is a dictionary from a finalized json dataset that conforms with the naming scheme
        - form is either 'TV' or 'movie' or 'anime'
        """
        self.title = entry['title']
        self.type = form
        # self.genres = set(entry['genre'].split())
        self.genres = entry['genre']
        self.rating = float(entry['rating'])
        self.date = int(entry['release_date'][:4])
        self.synopsis = entry['plot_summary']
        self.keywords = set(entry['keywords'])  # Originally, entry['keywords'] was a list
        self.recommendation = set()

    def __str__(self) -> str:
        """
        Returns a string representation of a Media object
        """
        return f"Media({self.title}, {self.type}, {self.genres}, " \
               f"{self.rating}, {self.date}, {self.synopsis}, {self.keywords}, {self.recommendation})"

    def compare(self, other: Media, parent_set: set[Media]) -> float:
        """compares itself to another media with 4 assessments,
        and mutates its recommendation accordingly

        Preconditions:
        - other in parent_set
        """
        sim_scores = (0, 0, 0, 0)
        mul = (0.1, 0.2, 0.3, 0.4)  # this should be subject to change (and tweaking will majorly affect results)
        # 1. date comparison

        # 2. rating comparison

        # 3. genre comparison

        # 4. keyword comparison

        # balancing comparison values
        assert sum(sim_scores) <= 4  # 4 would be if it gets perfect scores in each
        assert len(sim_scores) == len(mul)
        perfect_score = 4 * sum(mul)
        return sum(sim_scores[x] * mul[x] for x in range(0, len(sim_scores))) / perfect_score

    # TODO: Need to arrange function calls and structure of method (see the # ISSUE in function body)
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
            variation.
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
        self: Refers to the Media object of reference
        other: Refers to comparison Media object
        list_of_media: Refers to the list of input media objects
        """
        # ISSUE: Similar to date_comparison()

        # Step 3: Get mean rating from list of user-input shows (this is used for z score calculation)
        mean_rating = calculating_mean_rating(list_of_media)

        # Step 3: Get IQR date range from list of user-input shows
        iqr_of_ratings = calculating_iqr_of_ratings(list_of_media)

        # Step 4: Get the standard deviation and z score of the recommendation
        standard_dev_of_ratings = calculating_s_d_ratings(list_of_media)
        z_score_of_recommend = (other.rating - mean_rating) / standard_dev_of_ratings

        # Step 4: If the recommended show's date falls within the range dictated by the values in iqr_of_dates...
        # ... then the show is a good fit "date wise" with the user inputs.
        if other.rating >= iqr_of_ratings[0] and other.rating <= iqr_of_ratings[1]:
            return 1.0
        elif z_score_of_recommend < 1:
            return 0.0
        elif z_score_of_recommend == 0.0:
            return 0.5
        else:  # Reaching here implies z_score_of_recommend > 0.0:
            return 0.5 + z_score_of_recommend

    # TODO: Need to arrange function calls and structure of method (see the # ISSUE in function body)
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
            variation.
            3. Calculating abs((recommended show date - mean date) / standard deviation). We take the absolute value
            because z-scores can be negative, and as mentioned prior, we do not care about directionality.

        The higher the z-score, the further away the recommended show date is from the mean show date from the input
        set. Therefore, the higher the z-score, the lower the date score should be.

        So, if the abs(z-score) is < 1, we would consider that a good fit and also return the maximum score (1.0)
        Otherwise, we would return 1/abs(z-score).

        Arguments:
        self: Refers to the Media object of reference
        other: Refers to comparison Media object
        list_of_media: Refers to the list of input media objects
        """
        # ISSUE: There is a lot of redundant calling in this method, as for each time date_comparison()...
        # ... is called, calculating_median_date and calculating_iqr_of_dates must be ran each time
        # ... ideally each of the 2 methods should be called once, but I ran into weird scope issues when
        # ... trying to store these function results in a variable outside of this Media class
        # # Step 1: Calculate difference in dates.  UPDATE: We probably don't need this
        # date_difference = abs(self.date - other.date)

        # Step 2: Get median date from list of user-input shows. UPDATE: Z score calculations use mean, not median
        # median_date = calculating_median_date(list_of_media)

        # Step 3: Get mean date from list of user-input shows (this is used for z score calculation)
        mean_date = calculating_mean_date(list_of_media)

        # Step 3: Get IQR date range from list of user-input shows
        iqr_of_dates = calculating_iqr_of_dates(list_of_media)

        # Step 4: Get the standard deviation and z score of the recommendation
        standard_dev_of_dates = calculating_s_d_dates(list_of_media)
        abs_z_score_of_recommend = abs((other.date - mean_date) / standard_dev_of_dates)

        # Step 4: If the recommended show's date falls within the range dictated by the values in iqr_of_dates...
        # ... then the show is a good fit "date wise" with the user inputs.
        if other.date in range(iqr_of_dates[0], iqr_of_dates[1]) or abs_z_score_of_recommend < 1:
            return 1.0
        else:
            return 1 / abs_z_score_of_recommend

    def genre_comparison(self, other: Media) -> float:
        """
        Compute the fraction of shared genres between itself (a Media object) and another Media object
        """
        num_genre_shared = len(self.genres.intersection(other.genres))
        return num_genre_shared / len(other.genres)


def converting_show_to_media_obj(user_input_file_path: str) -> list[Media]:
    """
    Reads a json file (with name
    user_input_file_name) containing all user input media and converts it to a list of dictionaries
    with each dictionary entry representing an individual media entry.
    Then, take this list of USER INPUT MEDIA that the user has watched. For each input SHOW OR MOVIE
    , converts it into a Media object and stores it BACK to list user_input_media. Thus, this
    is a mutating method
    """
    # This section of the code is responsible for opening a json file and converting its contents to a dict
    with open(user_input_file_path, 'r') as file:
        user_input_media = json.load(file)  # Datatype of this is now list[dict]

    for index in range(len(user_input_media)):
        if "movie_id" not in user_input_media[index]:  # This means that encountered entry is a SHOW
            user_input_media[index] = Media(user_input_media[index], 'show')  # Assigning attribute "type" to "show"
            user_input_media[index].genres = set(user_input_media[index].genres.split(", "))
            # In the line above, since input shows have all genres listed as 1 string, needed to split entries
        else:  # If there is a key called "movie_id" in the entry, then the entry is A MOVIE
            user_input_media[index] = Media(user_input_media[index], 'movie')
            user_input_media[index].genres = set(user_input_media[index].genres)
            # by default, genres for movie entries stored in a list. Needed to convert to a set
    return user_input_media


# def calculating_median_date(user_input_media: list[Media]) -> int:
#     """
#     Calculates the median date of a user input media list
#     """
#     all_input_show_dates = np.array([user_input_media[index].date for index in range(len(user_input_media))])
#     return int(np.median(all_input_show_dates))
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
    return float(np.std(all_input_show_dates))


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


if __name__ == '__main__':
    # Enabling doctest checking features:

    import doctest

    doctest.testmod(verbose=True)

    # Enabling python_ta configurations:
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ["json", "numpy", "graph_classes"],
        'allowed-io': ["converting_show_to_media_obj"],
        'disable': ['R0902'],
        'max-line-length': 120,
    })
