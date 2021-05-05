import requests
import csv
from youtubesearchpython import VideosSearch
from django.contrib.staticfiles.storage import staticfiles_storage

from app.colors import *

MOVIEDB_API_URL = 'https://api.themoviedb.org/3'
MOVIEDB_API_KEY = '8bab42520fb79424d47245ab1e5406cf'

OMDB_API_KEY = 'e6dd17dc'


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

def get_person_api_data(name):
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

def get_movie_api_data(title):
  result = {} # initialize result dict
  result['genres'] = {'ids': [], 'strings': []}

  data = get_moviedb_data(f'/search/movie?api_key={MOVIEDB_API_KEY}&query={title}')
  movie = data['results'][0]

  result['id'] = movie['id']

  # add genres
  for genre_id in movie['genre_ids']:
    genre_string = get_genre_by_id(genre_id)
    result['genres']['ids'].append(genre_id)
    result['genres']['strings'].append(genre_string)

  return result

def get_movie_trailer_url(title):
  trailer_search_data = VideosSearch(title + 'trailer', limit = 1).result()
  youtube_url = trailer_search_data['result'][0]['link']
  return youtube_url

def get_recommended_movie_data(title):
  recCount = 5
  results = []

  moviedb_data = get_movie_api_data(title)
  rec_data = get_moviedb_data(f'/movie/{moviedb_data["id"]}/similar?api_key={MOVIEDB_API_KEY}')  

  for rec_movie in rec_data['results'][0:recCount]:
    rec_dict = {}

    original_title = rec_movie['original_title']
    print('\n\n' + original_title)

    rec_dict["title"] = original_title # add title

    # add moviedb data 
    rec_movie_id = rec_movie['id']
    rec_moviedb_data = get_moviedb_data(f'/movie/{rec_movie_id}?api_key={MOVIEDB_API_KEY}')

    rec_movie_data = {}
    rec_movie_data["revenue"] = rec_moviedb_data["revenue"]
    rec_movie_data["budget"] = rec_moviedb_data["budget"]
    rec_movie_data["overview"] = rec_moviedb_data["overview"]
    rec_movie_data["popularity"] = rec_moviedb_data["popularity"]
    rec_movie_data["release date"] = rec_moviedb_data["release_date"]

    rec_genres = []
    for g in rec_moviedb_data["genres"]:
      rec_genres.append(g["name"])
    rec_movie_data["genres"] = rec_genres

    # check if this image already exists
    if not os.path.isfile(f"app/static/app/images/{original_title}.png"):
      youtube_url = get_movie_trailer_url(original_title)
      print(youtube_url)

      if youtube_url:
        # get average color
        colors_img = average_colors(original_title, youtube_url)

        if colors_img and colors_img != "":
          rec_dict["trailer url"] = youtube_url
          rec_dict["image"] = '/app/images/' + colors_img
    else:
      print('image already exists')
      rec_dict["image"] = f'/app/images/{original_title}.png'

    rec_dict["data"] = rec_movie_data
    results.append(rec_dict)

  return results

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

