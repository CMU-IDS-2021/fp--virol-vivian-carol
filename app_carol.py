import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import requests
from utils import *


def main():

  data = get_api_data("Ang Lee")
  bio = data['biography']
  works = data['works']['cast']
  #name = data['works']['cast']
  df=pd.DataFrame(works)
  st.dataframe(df)
  #casts = data['cast']
  st.markdown(bio)

  #st.markdown(works)
  #st.markdown(name)

  #themoviedb API - search for movie by id
  response = requests.get("https://api.themoviedb.org/3/movie/310674?api_key=8bab42520fb79424d47245ab1e5406cf&language=en-US")
  r = response.json()
  #df=pd.DataFrame(r['cast'])
  st.markdown(r)
  st.dataframe(df)

  #OMDB API
  response = requests.get("http://www.omdbapi.com/?i=tt2294629&apikey=e6dd17dc")
  st.markdown(response.status_code)
  st.markdown(response.content)
  #sidebar_text
  add_text = st.sidebar.markdown("Which film producer/actor are you exploring?")
  add_textinput = st.sidebar.text_input(
    "such as Ang Lee",
  )

  #sidebar_slider
  add_text = st.sidebar.markdown("Which year range of works are you exploring?")  
  add_slider = st.sidebar.slider(
    'the data on the chart will change base on the range.',1900,2021,(1900,2021)
    )
  #sidebar_checkbox
  add_text = st.sidebar.markdown("Line Chart - What’s the imdb Rating by work")
  add_checkbox = st.sidebar.checkbox("budget")
  add_checkbox = st.sidebar.checkbox("revenue")
  add_text = st.sidebar.markdown("Bar Chart - How will the attribute distribute by origin and gender?")
  add_dropdown = st.sidebar.selectbox("select the attribute below",("imdb Rating","revenue","budget"))

  selector = alt.selection_single(empty='all', fields=['Count'])    

  #data preparation- genres count
  movie_genre_ids = df[~df.title.isnull()][['title', 'genre_ids']].to_dict(orient ='records')

  movie_genre = []
  for x in movie_genre_ids:
    if not x['genre_ids']:
      movie_genre.append({'movie': x['title'], 'genres': 'undefined'})
    for genre_id in x['genre_ids']:
      genre_name = get_genre_by_id(genre_id)
      movie_genre.append({'movie': x['title'], 'genres': genre_name})

  movie_genre_df = pd.DataFrame(movie_genre)
  movie_genre_summary = movie_genre_df.groupby(['genres']).agg({'movie': ['count' , pd.unique]}).reset_index()
  movie_genre_summary.columns = ['Genres', 'Count', 'Movie']
  movie_genre_summary.loc[:, 'Movie'] = movie_genre_summary.Movie.apply(lambda x: x if isinstance(x, str) else ', '.join(x.tolist()))
  
  #bar chart-genres count
  df_bar=movie_genre_summary.copy()
  st.dataframe(df)
  bar_genres = alt.Chart(df_bar).mark_bar(color='#8624F5', opacity=0.8, thickness=5).encode(
    alt.X('Genres:O',
      sort={"field": "Genres", "order": "ascending"},
      #title="(V)The correspondent decade of albums Issued Date"  
      ),
    alt.Y('Count:Q',
      scale=alt.Scale(zero=True),
      axis=alt.Axis(tickMinStep=1)
      #title='(V)Average_'+ option +'_by_Decade'
      ),
    tooltip=['Count','Genres', 'Movie'],

  ).properties(
    width=800,
    height=600
  )

  st.write(bar_genres)

  #data preperation - line
  def handle_get_moviedb_imdb_id(movie_id):
    try:
      result = get_moviedb_imdb_id(movie_id)
      return result
    except:
      pass
  df.loc[:, 'imdb_id'] = df.id.apply(lambda x:handle_get_moviedb_imdb_id(x))
  new_arr = []
  for index, row in df.iterrows():
    imdb_id = row['imdb_id']
    if imdb_id:
       res = get_OMDB_data(imdb_id)
       row['imdbRating'] = res['imdbRating']
       row['BoxOffice'] = res['BoxOffice']
       row['Year'] = res['Year']
       new_arr.append(row)
  #line chart
  # Create a selection that chooses the nearest point & selects based on x-value
  
  nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=['title'], empty='none')

  #test1 = {'Movie':['the blade runner','frozen','The Peanut Butter Falcon','Harry Potter and the Sorcerers Stone'],'IMDB':['7.4','8','6','5'],'revenue':['19999','14444','12000','16666'],'budget':['19999','19999','19999','19999'],'box-office':['19999','19999','19999','19999'],'year':['2010','2011','2012','2013']}
  #df=pd.DataFrame(test1)
  df = pd.DataFrame(new_arr)
  st.dataframe(df)
  base = alt.Chart(df).encode(
        alt.X('title')
  )
  line_A = base.mark_line(color='#5276A7').encode(
    alt.Y('imdbRating:Q', axis=alt.Axis(titleColor='#5276A7')),
  ).properties(
    width=800,
    height=600
  )

  line_B = base.mark_line(color='#F18727').encode(
    alt.Y('BoxOffice:O', axis=alt.Axis(titleColor='#F18727')),
  ).properties(
    width=800,
    height=600
  )
  # Transparent selectors across the chart. This is what tells us
  # the x-value of the cursor
  selectors = base.mark_point().encode(
    x='title',
    opacity=alt.value(0),
  ).add_selection(
    nearest
  )
  # Draw points on the line, and highlight based on selection
  points_A = line_A.mark_point().encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
  )
  # Draw text labels near the points, and highlight based on selection
  text_A = line_A.mark_text(align='left', dx=5, dy=-5).encode(
    text=alt.condition(nearest, 'imdbRating', alt.value(' '))
  )
  # Draw points on the line, and highlight based on selection
  points_B = line_B.mark_point(color='#F18727').encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
  )
  # Draw text labels near the points, and highlight based on selection
  text_B = line_B.mark_text(align='left', dx=10, dy=-5, color='#F18727').encode(
    text=alt.condition(nearest, 'BoxOffice', alt.value(' '))
  )  
  # Draw a rule at the location of the selection
  rules = alt.Chart(df).mark_rule(color='gray').encode(
    x='title',
  ).transform_filter(
    nearest
  )
  
  chart = alt.layer(line_A,points_A,text_A)
  chart = alt.layer(chart,line_B, points_B, text_B).resolve_scale(y='independent')
  chart = alt.layer(chart,selectors,rules)
  st.write(chart)
  #avg bar chart
  st.markdown("<div id='comparison'>", unsafe_allow_html=True)
  st.header("Bar Chart - David Bowie's albums with average features")
  st.subheader(":musical_note: How do the acoustic features of Bowie's albums differ from other songs in that decade?")
  st.markdown("Instructions: Click on the checkbox to compare with other songs from that decade. Click on the bar to highlight.")
  
  test2 = {'name':['AAA','BBB','CCC','DDD'],'type':['director','director','actor','actor'],'gender':['1','1','2','2'],'origin':['Asia','U.S','U.S','UK'],'avg budget':['19999','19999','19999','19999'],'avg box-office':['19999','19999','19999','19999'],'avg revenue':['19999','19999','19999','19999']}
  df=pd.DataFrame(test2)
  st.dataframe(df)
  test3 = {'Category':['Asia/Male','Asia/Female','U.S./Male','U.S./Female'],'type':['director','director','director','director'],'avg budget':['12222','19999','14444','17777'],'avg box-office':['19922','14444','19222','19999'],'avg revenue':['19999','19999','19999','19999']}
  df=pd.DataFrame(test3)
  st.dataframe(df)
  bar_avg = alt.Chart(df).mark_bar(color='#8624F5', opacity=0.8, thickness=5).encode(
    alt.X('Category:O',
      sort={"field": "Category", "order": "ascending"},
      #title="(V)The correspondent decade of albums Issued Date"  
      ),
    alt.Y('avg budget:Q',
      scale=alt.Scale(zero=True),
      axis=alt.Axis(tickMinStep=1)
      #title='(V)Average_'+ option +'_by_Decade'
      ),
    #tooltip=['Count','Genres', 'Movies'],

  ).properties(
    width=800,
    height=600
  )
  rule = alt.Chart(df).mark_rule(color='red').encode(
    y='mean(avg budget):Q'
  ).properties(
    width=800,
    height=600
  )

  st.write(bar_avg+rule)



main()
