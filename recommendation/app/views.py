from django.shortcuts import render
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
import json
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

  movie_input = request.POST['movie-input']
  movie_trailer = get_movie_trailer_url(movie_input)
  recommended_data = get_recommended_movie_data(movie_input)

  # populate return data
  data["movie"] = request.POST["movie-input"]
  data["movie_trailer"] = movie_trailer
  data["image"] = "/app/images/" + average_colors("originalmovie", movie_trailer)
  data["recommended"] = recommended_data

  # clear downloads folder
  downloads_dir = staticfiles_storage.path('downloads/')
  frames_dir = staticfiles_storage.path('downloads/frames/')
  for file in os.listdir(frames_dir):
    os.remove(os.path.join(frames_dir, file))

  return render(request, 'app/index.html', {"data": json.dumps(data)})

  
    
  


