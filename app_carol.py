import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import requests
from utils import *


def without_result():
  pass
  st.markdown("We couldnt find the result!")

def with_result(data):
#biography
  name = data['name']
  st.markdown('# '+name)
  col1, col2, col3, col4 = st.beta_columns((1,1,1,1))
  birthday = data['birthday']
  col1.markdown('**Birthday**')
  col1.markdown(birthday)
  place_of_birth = data['place_of_birth']
  col2.markdown('**Place of Birth**')
  col2.markdown(place_of_birth)
  popularity = data['popularity']
  col3.markdown('**Popularity**')
  col3.markdown(popularity)
  col4.markdown('**Number of works**')
  col4.markdown('23')#need to calculate  
  with st.beta_expander("Show me the biography!"):
    col1, col2 = st.beta_columns((1,2))
    bio = data['biography']
    pic_url = 'https://image.tmdb.org/t/p/w300/'
    profile_path = data['profile_path']
    profile_path = pic_url + profile_path
    col1.image(profile_path)
    col2.markdown(bio)

  works = data['works']['cast']

  #name = data['works']['cast']
  df=pd.DataFrame(works)

  #data preperation - line chart
  df.loc[:, 'imdb_id'] = df.id.apply(lambda x:handle_get_moviedb_imdb_id(x))
  new_arr = []
  for index, row in df.iterrows():
    imdb_id = row['imdb_id']
    if imdb_id:
      res = get_OMDB_data(imdb_id)
      row['imdbRating'] = res.get('imdbRating', 'N/A')
      row['BoxOffice'] = res.get('BoxOffice', 'N/A')
      row['Year'] = res.get('Year', 'N/A')

      res = handle_get_moviedb_movie_detail(row['id'])
      if res:
        row['revenue'] = res.get('revenue', 0)
        row['runtime'] = res.get('runtime', 0)
        row['budget'] = res.get('budget', 0)

      new_arr.append(row)

  related_movies_df = pd.DataFrame(new_arr)
  revenue_mean = related_movies_df[related_movies_df.revenue > 0].revenue.mean()
  box_office_mean = related_movies_df[related_movies_df.BoxOffice != 'N/A'].BoxOffice.str.replace('$', '').str.replace(',', '').astype(float, errors='ignore').mean()
  imdb_rate_mean = related_movies_df[related_movies_df.imdbRating != 'N/A'].imdbRating.astype(float, errors='ignore').mean()
  budget_mean = related_movies_df[related_movies_df.budget > 0].budget.mean()
  imdb_rate_mean = round(imdb_rate_mean, 2)
  budget_mean = round(budget_mean,2)
  box_office_mean = round(box_office_mean,2)
  revenue_mean = round(revenue_mean,2)
  st.markdown('### Average numbers of the works:')
  col1, col2, col3, col4 = st.beta_columns((1,1,1,1))
  col1.markdown('**Avg Revenue**')
  col1.markdown(f'{revenue_mean}')
  col2.markdown('**Avg Budget**')
  col2.markdown(f'{budget_mean}')
  col3.markdown('**Avg Box Office**')
  col3.markdown(f'{box_office_mean}')
  col4.markdown('**Avg IMDB Rate**')
  col4.markdown(f'{imdb_rate_mean}')#need to calculate 
 

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
  #st.markdown(f'movie_genre_df shape: {movie_genre_df.shape}')
  movie_genre_summary = movie_genre_df.groupby(['genres']).agg({'movie': ['count' , 'unique']}).reset_index()
  movie_genre_summary.columns = ['Genres', 'Count', 'Movie']
  movie_genre_summary.loc[:, 'Movie'] = movie_genre_summary.Movie.apply(lambda x: x if isinstance(x, str) else ', '.join(x.tolist()))
 
  #bar chart-description
  st.header("Bar Chart - Genres/Counts")
  st.subheader(":clapper: What genres are the works in?")
  st.markdown("Instructions: Hover on the bar to see the list of the movies.")
  with st.beta_expander("See the dataframe."):
    st.dataframe(movie_genre_df)
 
  
  #bar chart-genres count
  df_bar=movie_genre_summary.copy()
  #st.dataframe(df)
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

  #line chart-description
  st.header("Line Chart - IMDB Rating v.s BoxOffice/Budget/Revenue")
  st.subheader(":clapper: What genres are the works in?")
  st.markdown("Instructions: Hover on the bar to see the list of the movies.")
  with st.beta_expander("See the dataframe."):
    st.dataframe(movie_genre_df)


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


def main():

  st.markdown('# :popcorn:Film Producer/Actor Data Jam!')
  st.markdown('This platform allows you to explore the film producer/actor by their works.')
  
  add_textinput = st.text_input("Search for film producer/actor:", "Ang Lee")
  
  data = get_api_data(add_textinput)
  print(data)
  if data and data.get('works', {}).get('cast'):
    with_result(data)
  else:
    without_result()


if __name__ == '__main__':
  main()
