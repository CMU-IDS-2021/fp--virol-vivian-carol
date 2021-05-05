from django.shortcuts import render
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
import json
import os
import pandas as pd
import altair as alt

import recommendation.settings as settings
from app.utils import *

from vega_datasets import data

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
  
  # movie_data = get_movie_api_data(request.POST['movie-input'])

  data["movie_trailer"] = movie_trailer
  data["image"] = "/app/images/" + average_colors("originalmovie", movie_trailer)
  data["recommended"] = recommended_data

  # clear downloads folder
  downloads_dir = staticfiles_storage.path('downloads/')
  frames_dir = staticfiles_storage.path('downloads/frames/')
  for file in os.listdir(frames_dir):
    os.remove(os.path.join(frames_dir, file))

  # chart stuff
  context = {}

  # budget vs. revenue chart
  df_dict = {}
  df_dict['movie'] = []
  # df_dict['budget'] = []
  # df_dict['revenue'] = []
  df_dict['popularity'] = []
  df_dict['release date'] = []

  for r in recommended_data:
    r_data = r['data']
    print(r_data)

    df_dict['movie'].append(r['title'])

    # df_dict['budget'].append(r_data['budget'])
    # df_dict['revenue'].append(r_data['revenue'])

    df_dict['popularity'].append(r_data['popularity'])
    df_dict['release date'].append(r_data['release date'][0:4]) # get year of release date

  print(df_dict)
  chart_data = pd.DataFrame(df_dict)

  chart = alt.Chart(chart_data, title="popularity vs. release date").mark_circle().encode(
    alt.X('release date:T',
      scale=alt.Scale(zero=False),
      axis=alt.Axis(title='release date'),
      type='ordinal'
    ),
    alt.Y('popularity:Q',
      scale=alt.Scale(zero=True),
      axis=alt.Axis(title='popularity'),
      type='quantitative'
    ),
    color=alt.Color('movie', legend=alt.Legend(orient="right")),
  ).properties(
    width=500,
    height=350
  ).interactive()

  context['chart'] = chart
  context['data'] = json.dumps(data)

  return render(request, 'app/index.html', context)

  
    
  


