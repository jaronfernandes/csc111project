"""thing """
import csv
import json

json_file = []
for line in open('datasets/IMDB_movie_details.json', 'r'):
    json_file.append(json.loads(line))

# with open('datasets/IMDB_movie_details.json') as f:
#     movie_details = json.load(f)
#
#     print(movie_details)


def check_in_thing() -> dict:
    """help"""
    json_dict = {}

    for movie in json_file:
        json_dict[movie['movie_id']] = movie

    return json_dict


movie_id_dict = check_in_thing()


with open("datasets/title.basics.tsv") as fd:
    rd = csv.reader(fd, delimiter="\t", quotechar='"')
    next(rd)
    # for row in rd:
    #     print(row)
    row_list = []

    for row in rd:
        if row[0][0:2] == 'tt' and row[1] == 'movie' and row[0] in movie_id_dict:
            movie_id_dict[row[0]]['title'] = row[3]
            movie_id_dict[row[0]].pop('plot_summary')
            movie_id_dict[row[0]].pop('duration')
        elif row[0][0:2] == 'tt' and row[0] in movie_id_dict:
            movie_id_dict.pop(row[0])

    with open('datasets/final_movies.json', 'w') as outfile:
        json.dump(list(movie_id_dict.values()), outfile, indent=4)
# print(movie_id_dict)

    # with open("datasets/filtered_basics.txt", 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerows(row_list)

# with open('datasets/title.basics.tsv') as f:
#     basics = {str.strip(line.lower()) for line in f}
#
#     basics = basics[:-9900000]
#     print(basics)
