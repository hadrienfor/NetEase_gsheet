import os
from collections import defaultdict

import pandas as pd
import pygsheets
from pygsheets import Cell

from categories import genre_labels, mood_labels, situation_labels, voice_labels
from genre_hierarchy import subgenre_to_genre

NUM_LABELS_TO_SHOW = 5
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1TD7wIucHERHqlw0xgpY8oQhpR0gUJroD67I9hAPPg9c/edit?usp=sharing"
GSHEET_TAB_NAME = "Feuille 1"


def rename_filepaths(predictions):
    df = pd.read_excel("tracks.xlsx")
    df["filepath_name"] = df["audio_url"].apply(lambda url: url.split("/")[-1])
    d = {
        os.path.split(name)[-1]: track_id
        for name, track_id in zip(df["filepath_name"].to_list(), df["track_id"].to_list())
    }
    new = {}
    for filepath in predictions:
        new[d[os.path.split(filepath)[-1]]] = predictions[filepath]
    return new


def get_top_n_predictions(predictions_df: pd.DataFrame, top_n: int = 5, cut_off_percent_value: int = 10):
    predictions_df = predictions_df.apply(pd.Series.nlargest, axis=1, n=top_n)
    predictions = {}
    for file_path, track_predictions in predictions_df.iterrows():
        predictions[str(file_path)] = dict(
            sorted(
                {
                    k: 100 * v
                    for k, v in track_predictions.dropna().to_dict().items()
                    if 100 * v >= cut_off_percent_value
                }.items(),
                key=lambda x: x[1],
                reverse=True,
            )
        )
    return predictions


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

    csv_path = "/Users/hadfor/Workplace/NetEase/NetEase_gsheet/predictions/E5.csv"
    preds_csv = pd.read_csv(csv_path, index_col=0)
    genre_results = get_top_n_predictions(preds_csv, top_n=5, cut_off_percent_value=10)

    analysis_results = pd.read_csv("a0c2d2ed-c144-4185-8d2b-7a096377dd08_1671035462660_part_0.csv")
    m = pd.read_csv("Enhance 1.4 Lexicology - lexicology.csv")
    track_metadata = pd.read_csv("tracks.csv")

    mappings = {"Situation": {}, "Mood": {}, "Voice Family": {}, "Genre": {}}
    all_labels = set(mood_labels + situation_labels + voice_labels + genre_labels)

    for _, row in m.iterrows():
        if row[2] in mappings.keys() and row[3] in all_labels:
            mappings[row[2]][row[0]] = row[3]

    track_situations = defaultdict(list)
    track_moods = defaultdict(list)
    track_voices = defaultdict(list)
    track_genres_14 = defaultdict(list)

    for _, row in analysis_results.iterrows():
        if row[2] in mappings["Situation"]:
            track_situations[str(row[0])].append((mappings["Situation"][row[2]], row[3]))
        elif row[2] in mappings["Mood"]:
            track_moods[str(row[0])].append((mappings["Mood"][row[2]], row[3]))
        elif row[2] in mappings["Voice Family"]:
            track_voices[str(row[0])].append((mappings["Voice Family"][row[2]], row[3]))
        elif row[2] in mappings["Genre"]:
            track_genres_14[str(row[0])].append((mappings["Genre"][row[2]], row[3]))

    track_id_to_metadata = {}
    for _, row in track_metadata.iterrows():
        track_id = str(row[1])
        if (
            track_id in track_situations.keys()
            and track_id in track_moods.keys()
            and track_id in track_voices.keys()
            and track_id in track_genres_14.keys()
            and track_id in genre_results.keys()
        ):
            track_id_to_metadata[track_id] = (row[3], row[2])

    track_subgenres = {track_id: [(k, v) for k, v in genres.items()] for track_id, genres in genre_results.items()}

    track_genres = {
        track_id: list(sorted([(subgenre_to_genre[vv[0]], vv[1]) for vv in v], key=lambda x: x[1], reverse=True))
        for track_id, v in track_subgenres.items()
    }

    # remove duplicate and keep max score (genre postprocessing)
    for k, v in track_genres.items():
        curr_genres = []
        new_list = []
        for vv in v:
            if vv[0] not in curr_genres and vv[1] >= 50.0:
                new_list.append(vv)
            curr_genres.append(vv[0])
        if len(new_list) > 2:
            new_list = new_list[:2]
        track_genres[k] = new_list

    gc = pygsheets.authorize(service_file="compact-buckeye-195911-c16e69961bdd.json")
    s = gc.open_by_url(GSHEET_URL)
    worksheet = s.worksheet_by_title(GSHEET_TAB_NAME)

    cells = []

    for idx, (track_id, (artist, title)) in enumerate(track_id_to_metadata.items()):
        genre = track_genres[track_id]
        sub_genre = track_subgenres[track_id]
        print(sub_genre)
        genre_14 = track_genres_14[track_id]
        voice = track_voices[track_id]
        mood = track_moods[track_id]
        situation = track_situations[track_id]

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
