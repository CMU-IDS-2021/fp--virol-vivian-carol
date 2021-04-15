import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import requests

MOVIEDB_API_URL = 'https://api.themoviedb.org/3'
MOVIEDB_API_KEY = '8bab42520fb79424d47245ab1e5406cf'

def get_moviedb_data(query_url):
  """
  Given the rest of the url, makes a GET request to moviedb API and returns data as JSON
  """
  url = f'{MOVIEDB_API_URL}{query_url}'
  r = requests.get(url)
  r.raise_for_status()
  data = r.json()
  return data

def get_person_id(name):
  """
  Returns moviedb api ID of person from producer/actor name.
  """
  data = get_moviedb_data(f'/search/person?api_key={MOVIEDB_API_KEY}&query={name}')
  person_id = data['results'][0]['id'] # select first result and get id

  return person_id

def get_api_data(name):
  """
  Returns dictionary of bio, works from producer/actor name.
  """
  result = {} # initialize result dict
  result['biography'] = ''
  result['works'] = {}

  person_id = get_person_id(name) # get person id by name
  data = get_moviedb_data(f'/person/{person_id}?api_key={MOVIEDB_API_KEY}')

  # add biography
  biography = data['biography']
  result['biography'] = biography

  # add list of works, sorted by popularity (descending)
  works_data = get_moviedb_data(f'/person/1614/combined_credits?api_key={MOVIEDB_API_KEY}')
  cast_list = works_data['cast']
  crew_list = works_data['crew']

  sorted_cast_list = sorted(cast_list, key = lambda i: i['popularity'], reverse=True)
  sorted_crew_list = sorted(crew_list, key = lambda i: i['popularity'], reverse=True)
  
  result['works']['cast'] = sorted_cast_list
  result['works']['crew'] = sorted_crew_list

  return result

def get_genre_by_id(genre_id):
  """
  Returns genre name from moviedb API given genre id
  """
  # get movie genres
  movie_genres_url = f'/genre/movie/list?api_key={MOVIEDB_API_KEY}'
  movie_genres_data = get_moviedb_data(movie_genres_url)

  # get tv genres
  tv_genres_url = f'/genre/tv/list?api_key={MOVIEDB_API_KEY}'
  tv_genres_data = get_moviedb_data(tv_genres_url)

  genres = movie_genres_data['genres'] + tv_genres_data['genres']

  for g in genres:
    if g['id'] == genre_id:
      return g['name']

  raise ValueError(f"Genre with ID {genre_id} not found.")

