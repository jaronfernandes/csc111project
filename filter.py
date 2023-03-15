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


def check_in_thing() -> set[str]:
    """help"""
    set_thing = set()

    for x in json_file:
        set_thing.add(x['movie_id'])

    return set_thing


movie_id_set = check_in_thing()


with open("datasets/title.basics.tsv") as fd:
    rd = csv.reader(fd, delimiter="\t", quotechar='"')
    next(rd)
    # for row in rd:
    #     print(row)
    row_list = []

    for row in rd:
        if row[0][0:2] == 'tt' and row[0] in movie_id_set:
            row_list.append(row)

    with open("datasets/filtered_basics.txt", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(row_list)

# with open('datasets/title.basics.tsv') as f:
#     basics = {str.strip(line.lower()) for line in f}
#
#     basics = basics[:-9900000]
#     print(basics)
