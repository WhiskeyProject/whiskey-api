import numpy as np
import pandas as pd
import math
import os, re, logging, base64
from django.forms import model_to_dict

from whiskies.models import Whiskey, Tag, TagTracker
from elasticsearch import Elasticsearch


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
        whiskey.comparables.remove(comp)


def update_whiskey_comps(whiskies, tags, number_comps=12):
    """
    score_df creates a matrix of Eulidean distances between all whiskies.
    """

    score_df = main_scores(whiskies, tags)

    for whiskey in whiskies:
        scores = score_df[whiskey.id].copy()
        scores.sort_values(inplace=True)

        clear_saved(whiskey)

        # Would like to store in reverse order they are added.
        for pk in scores.index[:number_comps]:
            whiskey.comparables.add(Whiskey.objects.get(pk=pk))


"""
Elastic search functions.
Some indexing and future tag search functions have been saved locally.
"""


def local_whiskey_search(searchstring):
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    search_body = {"query": {"terms": {"title": searchstring}}}


    # search_body = {
    #     "query": {
    #         "bool": {
    #             "must": [
    #                 {"term": {"tags.title": "sweet"}},
    #                 {"term": {"tags.title": "amber"}},
    #                 {"term": {"tags.title": "rich"}}
    #             ]
    #         }
    #     }
    # }

    return es.search(index="full_whiskies", body=search_body, size=400)


def heroku_search_whiskies(searchstring):
    """
    Main elasticsearch function.
    :param searchstring: A list of search terms, ie. ['term1', 'term2']
    """

    bonsai = os.environ['BONSAI_URL']

    auth = re.search('https\:\/\/(.*)\@', bonsai).group(1).split(':')
    host = bonsai.replace('https://%s:%s@' % (auth[0], auth[1]), '')

    es_header = [{
        'host': host,
        'port': 443,
        'use_ssl': True,
        'http_auth': (auth[0], auth[1])
    }]

    es = Elasticsearch(es_header)

    es.ping()

    search_body = {"query": {"terms": {"title": searchstring}}}
    return es.search(index="whiskies", body=search_body)

