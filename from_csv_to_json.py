import json
import os

import pandas as pd


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


def from_csv_to_json_with_ids(csv_path, json_path):
    preds_csv = pd.read_csv(csv_path, index_col=0)
    preds_json_top_n = get_top_n_predictions(preds_csv)
    preds_json_w_ids = rename_filepaths(preds_json_top_n)
    with open(json_path, "w") as f:
        json.dump(preds_json_w_ids, f, indent=4)
    return


if __name__ == "__main__":

    csv_path = "/Users/hadfor/Workplace/NetEase/NetEase_gsheet/predictions/E1_spec.csv"
    json_path = "/Users/hadfor/Workplace/NetEase/NetEase_gsheet/predictions/E1_spec.json"
    from_csv_to_json_with_ids(csv_path, json_path)
