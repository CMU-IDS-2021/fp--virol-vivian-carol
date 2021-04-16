import requests
import csv
from django.contrib.staticfiles.storage import staticfiles_storage

from app.colors import *

MOVIEDB_API_URL = 'https://api.themoviedb.org/3'
MOVIEDB_API_KEY = '8bab42520fb79424d47245ab1e5406cf'

OMDB_API_KEY = 'e6dd17dc'

YOUTUBE_CSV_FILE = "ml-youtube.csv"

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
  moviedb_data = get_movie_api_data(title)
  data = get_moviedb_data(f'/movie/{moviedb_data["id"]}?api_key={MOVIEDB_API_KEY}')  
  title = f"{data['original_title']} ({data['release_date'][0:4]})"

  # search for youtube id in csv file
  csv_url = staticfiles_storage.path(YOUTUBE_CSV_FILE)
  csv_file = csv.reader(open(csv_url, 'r'), delimiter=',')

  for row in csv_file:
    # print(row)
    if title == row[2]:
      youtube_id = row[0]
      return f'https://www.youtube.com/watch?v={youtube_id}'

  return ''

def get_recommended_movie_data(title):
  results = []

  moviedb_data = get_movie_api_data(title)
  rec_data = get_moviedb_data(f'/movie/{moviedb_data["id"]}/similar?api_key={MOVIEDB_API_KEY}')  

  for rec_movie in rec_data['results'][0:10]:
    rec_dict = {}

    # get movie title in ml-youtube.csv format
    original_title = rec_movie['original_title']
    print('\n\n' + original_title)
    title = f"{original_title} ({rec_movie['release_date'][0:4]})"
    # search for youtube id in csv file
    csv_url = staticfiles_storage.path(YOUTUBE_CSV_FILE)
    csv_file = csv.reader(open(csv_url, 'r'), delimiter=',')

    youtube_found = False
    youtube_id = ''

    # find youtube id in csv file
    for row in csv_file:
      # print(row)
      if title == row[2]:
        youtube_id = row[0]
        youtube_found = True

    # get youtube video
    if youtube_found:
      youtube_url = f"https://www.youtube.com/watch?v={youtube_id}"
      print(youtube_url)

      # get average color
      colors_img = average_colors(original_title, youtube_url)

      if colors_img and colors_img != "":
        rec_dict['title'] = title
        rec_dict['trailer url'] = youtube_url
        # rec_dict['data'] = rec_movie
        rec_dict['image'] = '/app/images/' + colors_img
        print(colors_img)

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

