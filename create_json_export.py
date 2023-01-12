import json
from collections import defaultdict

import pandas as pd

from categories import (genre_labels, mood_labels, situation_labels,
                        voice_labels)
from genre_hierarchy import subgenre_to_genre

if __name__ == "__main__":
    analysis_results = pd.read_csv('a0c2d2ed-c144-4185-8d2b-7a096377dd08_1671035462660_part_0.csv')
    m = pd.read_csv('Enhance 1.4 Lexicology - lexicology.csv')
    track_metadata = pd.read_csv('tracks.csv')
    # genre_results = json.load(open('predictions/transformer_new.json', 'r'))
    # genre_results = json.load(open('predictions/transformer_old_new.json', 'r'))
    # genre_results = json.load(open('predictions/multirescnn_new.json', 'r'))
    # genre_results = json.load(open('predictions/multirescnn_old_new.json', 'r'))
    # genre_results = json.load(open('predictions/multirescnn_musico_old_new.json', 'r'))
    # genre_results = json.load(open('predictions/multirescnn_round2_old_new.json', 'r'))
    genre_results = json.load(open('predictions/E1_spec.json', 'r'))
    
    
    
    mappings = {
        'Situation': {},
        'Mood': {},
        'Voice Family': {},
        'Genre': {}
    }
    all_labels = set(mood_labels + situation_labels + voice_labels + genre_labels)

    for _, row in m.iterrows():
        if row[2] in mappings.keys() and row[3] in all_labels:
            mappings[row[2]][row[0]] = row[3]

    track_situations = defaultdict(list)
    track_moods = defaultdict(list)
    track_voices = defaultdict(list)
    track_genres_14 = defaultdict(list)
    
    for _, row in analysis_results.iterrows():
        if row[2] in mappings['Situation']:
            track_situations[str(row[0])].append((mappings['Situation'][row[2]], row[3]))
        elif row[2] in mappings['Mood']:
            track_moods[str(row[0])].append((mappings['Mood'][row[2]], row[3]))
        elif row[2] in mappings['Voice Family']:
            track_voices[str(row[0])].append((mappings['Voice Family'][row[2]], row[3]))
        elif row[2] in mappings['Genre']:
            track_genres_14[str(row[0])].append((mappings['Genre'][row[2]], row[3]))
            
    track_id_to_metadata = {}
    for _, row in track_metadata.iterrows():
        track_id = str(row[1])
        if track_id in track_situations.keys() \
        and track_id in track_moods.keys() \
        and track_id in track_voices.keys() \
        and track_id in track_genres_14.keys() \
        and track_id in genre_results.keys():
            track_id_to_metadata[track_id] = (row[3], row[2])
    
    track_subgenres = {
        track_id: [(k, v) for k, v in genres.items()] for track_id, genres in genre_results.items()
    }
    
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
    
    # json.dump(track_id_to_metadata, open('export/track_id_to_metadata.json', 'w'))
    json.dump(track_genres, open('export/track_genres.json', 'w'))
    json.dump(track_subgenres, open('export/track_subgenres.json', 'w'))
    # json.dump(track_genres_14, open('export/track_genres_14.json', 'w'))
    # json.dump(track_genres, open('export/track_genres_multirescnn.json', 'w'))
    # json.dump(track_subgenres, open('export/track_subgenres_multirescnn.json', 'w'))
    # json.dump(track_voices, open('export/track_voices.json', 'w'))
    # json.dump(track_moods, open('export/track_moods.json', 'w'))
    # json.dump(track_situations, open('export/track_situations.json', 'w'))
    