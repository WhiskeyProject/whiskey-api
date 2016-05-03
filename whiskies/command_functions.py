import numpy as np
import pandas as pd
import math

from whiskies.models import Whiskey, TagSearch, Tag, TagTracker


def euclidean_distance(v1, v2):
    squares = (v1 - v2) ** 2
    return math.sqrt(squares.sum())

tags = Tag.objects.all()


def get_tag_counts(whiskey, tags):
    # use all tagtrackers to create a tag:count dict.
    # Then loop through tag_list

    trackers = TagTracker.objects.filter(whiskey=whiskey).values()
    count_dict = {t["tag_id"]: t["count"] for t in trackers}
    counts = []
    for tag in tags:
        count = count_dict.get(tag.id, 0)
        counts.append(count)
    return np.array(counts)


def create_features_dict(whiskies, tags):
    # whiskies will be all whiskies of a certain type (ie. Scotch, Bourbon)

    # Return a dict of {whiskey_id: np.array([<tag counts>])}

    whisky_features = {}
    for whisky in whiskies:
        counts = get_tag_counts(whisky, tags)
        whisky_features[whisky.id] = counts
    return whisky_features


def create_scores(whiskey_ids, whiskey_features):

    results = []
    for column_whiskey in whiskey_ids:
        cell = {}

        for row_whiskey in whiskey_ids:
            if column_whiskey == row_whiskey:
                cell[row_whiskey] = np.nan
            else:
                distance = euclidean_distance(whiskey_features[column_whiskey],
                                              whiskey_features[row_whiskey])
                cell[row_whiskey] = distance
        results.append(cell)
    return results


def main_scores(whiskies, tags):
    # Create pandas dataframe distance matrix for all whiskies and tags
    # that are passed in.
    # Whiskies will usually be a filtered for a specific type.

    whiskey_features = create_features_dict(whiskies, tags)
    whiskey_ids = list(whiskey_features.keys())

    df = pd.DataFrame(create_scores(whiskey_ids, whiskey_features))

    df.index = whiskey_ids

    return df


def clear_saved(whiskey):

    for comp in whiskey.comparables.all():
        whiskey.comparable.remove(comp)


def update_whiskey_comps(number_comps=3):
    tags = Tag.objects.all()

    # Filter by region once we get those straightened out
    whiskies = Whiskey.objects.all()

    score_df = main_scores(whiskies, tags)

    for whiskey in whiskies:
        scores = score_df[whiskey.id].copy()
        scores.sort()

        clear_saved(whiskey)

        for pk in scores.index[:number_comps]:
            whiskey.comparable.add(Whiskey.objects.get(pk=pk))
