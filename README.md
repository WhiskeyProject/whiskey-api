[![Coverage Status](https://coveralls.io/repos/github/WhiskeyProject/whiskey-api/badge.svg?branch=master)](https://coveralls.io/github/WhiskeyProject/whiskey-api?branch=master)
[![Build Status](https://travis-ci.org/WhiskeyProject/whiskey-api.svg?branch=master)](https://travis-ci.org/WhiskeyProject/whiskey-api)
# whiskey-project-api

This is an API for a whiskey recommendation site.

### Where does the data come from?

Approximately 15,000 whiskey reviews were scraped and analyzed as seed data to determine how whiskeys are most commonly described. From that list we selected about 70 of the most accessible descriptors; terms such as cherry, chocolate, or light. A PostgreSQL database of roughly 370 whiskeys was then put together, each whiskey with it's own profile based on how often it is described by each of those terms.


### How do the recommendations work?

There are two ways to discover new whiskeys with the API. The first is the shoot endpoint. Different tags, regions, and price ranges can be sent as a query string and a list of whiskeys will be returned, ordered by how closely they match the terms.

The other is with the comparable field that is on each whiskey. This is a list of the other whiskeys in the database that it most closely matches. These comparables are generated with the set_comps command which takes an array of each whiskeys' attributes, calculates the Euclidean Distance from every other array, and returns the most similar items.

All endpoints are listed and documented here: https://evening-citadel-85778.herokuapp.com/docs/


### Technologies used.

<b>Code:</b> Written in Python with the Django REST API framework.

<b>Data gathering and analysis:</b> PRAW, pandas, and numpy.

<b>Text search:</b> Elasticsearch.

<b>Image hosting:</b> Cloudinary.

<b>Continuous integration:</b> Travis and Coveralls.
