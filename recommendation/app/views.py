from django.shortcuts import render
from django.contrib.staticfiles.storage import staticfiles_storage
import os

import recommendation.settings as settings
from app.utils import *

# Create your views here.
def get_page(request):
  if request.method == 'GET':
    data = {}
    data['movie'] = 'the avengers'
    data['movie_trailer'] = ""
    data['recommended'] = []
    data['image'] = ""
    return render(request, 'app/index.html', data)

  # process input
  data = {}
  # print(request.POST)

  movie_input = request.POST['movie-input']
  movie_trailer = get_movie_trailer_url(movie_input)
  print(movie_trailer)
  recommended_data = get_recommended_movie_data(movie_input)

  for r in recommended_data:
    print(r)
    # print(r['colors img'])

  data['movie'] = request.POST['movie-input']
  data['movie_trailer'] = movie_trailer
  data['image'] = '/app/images/' + average_colors('originalmovie', movie_trailer)
  data['recommended'] = recommended_data

  # clear downloads folder
  downloads_dir = staticfiles_storage.path('downloads/')
  frames_dir = staticfiles_storage.path('downloads/frames/')
  for file in os.listdir(frames_dir):
    os.remove(os.path.join(frames_dir, file))

  return render(request, 'app/index.html', data)

  
    
  


