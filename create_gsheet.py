import json

import pygsheets
from pygsheets import Cell

NUM_LABELS_TO_SHOW = 5
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1TD7wIucHERHqlw0xgpY8oQhpR0gUJroD67I9hAPPg9c/edit?usp=sharing"
GSHEET_TAB_NAME = "Feuille 1"


def output_labels(Y, n=5):
    Y = list(sorted(Y, key=lambda x: x[1], reverse=True))[:n]
    return "\n".join([y[0] for y in Y if y[1] > 9])


def output_scores(Y, n=5):
    Y = list(sorted(Y, key=lambda x: x[1], reverse=True))[:n]
    return "\n".join(["100%" if y[1] > 99.9 else f"{y[1]:.0f}%" for y in Y if y[1] > 9])


def add_label_cell(cells, y, cell_idx, column_idx):
    cells.append(Cell(pos=(cell_idx, column_idx), val=output_labels(y, n=NUM_LABELS_TO_SHOW)))
    cells.append(Cell(pos=(cell_idx, column_idx + 1), val=output_scores(y, n=NUM_LABELS_TO_SHOW)))
    return cells


if __name__ == "__main__":

    track_id_to_metadata = json.load(open("export/track_id_to_metadata.json", "r"))
    track_genres = json.load(open("export/track_genres.json", "r"))
    track_subgenres = json.load(open("export/track_subgenres.json", "r"))
    track_genres_14 = json.load(open("export/track_genres_14.json", "r"))
    track_voices = json.load(open("export/track_voices.json", "r"))
    track_moods = json.load(open("export/track_moods.json", "r"))
    track_situations = json.load(open("export/track_situations.json", "r"))

    gc = pygsheets.authorize(service_file="compact-buckeye-195911-c16e69961bdd.json")
    s = gc.open_by_url(GSHEET_URL)
    worksheet = s.worksheet_by_title(GSHEET_TAB_NAME)

    cells = []

    for idx, (track_id, (artist, title)) in enumerate(track_id_to_metadata.items()):
        genre = track_genres[track_id]
        sub_genre = track_subgenres[track_id]
        genre_14 = track_genres_14[track_id]
        voice = track_voices[track_id]
        mood = track_moods[track_id]
        situation = track_situations[track_id]

        # Display post processing rules
        # subgenre_names = [n[0] for n in sub_genre]
        # subgenre_values = [v[1] for v in sub_genre]

        # build the gsheet
        cells.append(Cell(pos=(idx + 2, 1), val=track_id))

        cells.append(Cell(pos=(idx + 2, 2), val=artist))

        cells.append(Cell(pos=(idx + 2, 3), val=title))

        cells = add_label_cell(cells, situation, idx + 2, 4)
        cells = add_label_cell(cells, mood, idx + 2, 7)
        cells = add_label_cell(cells, genre, idx + 2, 10)
        cells = add_label_cell(cells, sub_genre, idx + 2, 13)
        cells = add_label_cell(cells, genre_14, idx + 2, 16)
        cells = add_label_cell(cells, voice, idx + 2, 19)

    worksheet.update_cells(cells)
