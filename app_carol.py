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
  st.markdown('# We present you:'+name)
  st.markdown('''<a id="title">:popcorn: Basic Bio </a>''', unsafe_allow_html=True)
  
  with st.beta_expander("Show me the detail biography!"):
    col1, col2 = st.beta_columns((1,2))
    bio = data['biography']
    pic_url = 'https://image.tmdb.org/t/p/w300/'
    profile_path = data['profile_path']
    profile_path = pic_url + profile_path
    col1.image(profile_path)
    col2.markdown(bio)

  works = data['works']['cast']
  df=pd.DataFrame(works)

  #data preperation - line chart
  df.loc[:, 'imdb_id'] = df.id.apply(lambda x:handle_get_moviedb_imdb_id(x))
  new_arr = []
  for index, row in df.iterrows():
    imdb_id = row['imdb_id']
    if imdb_id:
      res = get_OMDB_data(imdb_id)
      row['imdbRating'] = get_number(res.get('imdbRating', 0))
      row['BoxOffice'] = get_number(res.get('BoxOffice', 0))
      row['Year'] = res.get('Year', 0)
      res = handle_get_moviedb_movie_detail(row['id'])
      if res:
        row['revenue'] = res.get('revenue', 0)
        row['runtime'] = res.get('runtime', 0)
        row['budget'] = res.get('budget', 0)

      new_arr.append(row)

  related_movies_df = pd.DataFrame(new_arr)
  related_movies_df.loc[:, 'runtime'] = related_movies_df.runtime.fillna(0)
  related_movies_df = related_movies_df[related_movies_df.media_type == 'movie']
  non_zero_related_movies_df = related_movies_df[(related_movies_df.BoxOffice > 0) & (related_movies_df.revenue > 0) & (related_movies_df.budget > 0)]
  movie_count = related_movies_df.shape[0]
  revenue_mean = related_movies_df[related_movies_df.revenue > 0].revenue.mean()
  box_office_mean = related_movies_df[related_movies_df.BoxOffice > 0].BoxOffice.mean()
  imdb_rate_mean = related_movies_df[related_movies_df.imdbRating > 0].imdbRating.mean()
  runtime_mean = related_movies_df[related_movies_df.runtime > 0].runtime.mean()
  budget_mean = related_movies_df[related_movies_df.budget > 0].budget.mean()
  imdb_rate_mean = round(imdb_rate_mean, 2)
  runtime_mean = round(runtime_mean,2)
  box_office_mean = round(box_office_mean,2)
  revenue_mean = round(revenue_mean,2)


  # add mean value column
  related_movies_df = related_movies_df.assign(
    imdbRating_mean=imdb_rate_mean,
    runtime_mean=runtime_mean
    )

  # add ratio column
  non_zero_related_movies_df = add_portion_columns(non_zero_related_movies_df)

  d_avg = {'revenue mean': [revenue_mean], 'box office mean': [box_office_mean],'imdbRating': [imdb_rate_mean], 'budget mean': [budget_mean], 'runtime': [runtime_mean]}
  #4 column biography
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
  col4.markdown('**Number of movies**')
  col4.markdown(movie_count)
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
  movie_genre_summary = movie_genre_df.groupby(['genres']).agg({'movie': ['count' , 'unique']}).reset_index()
  movie_genre_summary.columns = ['Genres', 'Count', 'Movie']
  movie_genre_summary.loc[:, 'Movie'] = movie_genre_summary.Movie.apply(lambda x: x if isinstance(x, str) else ', '.join(x.tolist()))
 
  #bar chart-description
  st.markdown('''<a id="title">:popcorn: What genres are the works in? </a>''', unsafe_allow_html=True)
  st.markdown("You can interact with the chart by hovering on the bar.")
  with st.beta_expander("See the dataframe."):
    st.markdown("movie and genres is in a one-to-many relationship.")
    st.dataframe(movie_genre_df)
 
  #bar chart-genres count
  df_bar=movie_genre_summary.copy()
  #st.dataframe(df)
  bar_genres = alt.Chart(df_bar).mark_bar(color='#0D26C4', opacity=0.8).encode(
    alt.X('Genres:O',
      sort={"field": "Genres", "order": "ascending"},
      #title="(V)The correspondent decade of albums Issued Date"  
      ),
    alt.Y('Count:Q',
      scale=alt.Scale(zero=True),
      axis=alt.Axis(tickMinStep=1)
      #title='(V)Average_'+ option +'_by_Decade'
      ),
    tooltip=['Count', 'Movie'],

  ).properties(
    width=600,
    height=600
  )
  with st.beta_expander("See the Chart."):
    st.write(bar_genres)

  #avg_bar chart-description
  st.markdown('''<a id="title">:popcorn: What's the financial structure of the works? </a>''', unsafe_allow_html=True)
  st.markdown("You can interact with the chart by")
  st.markdown("1. Select checkbox to layer the attributes.")
  st.markdown("2. Hover on the bar for the detail.")  
  df_z = pd.DataFrame(non_zero_related_movies_df)
  with st.beta_expander("See the dataframe."):
    st.dataframe(df_z)
  #avg bar chart
  st.markdown("<div id='comparison'>", unsafe_allow_html=True)
  base = alt.Chart(df_z).encode(
        x=alt.X('title', sort=alt.EncodingSortField(field='release_date', order='ascending'),title="The title of films order by issued date")
  )
  boxoffice_chart= base.mark_bar(color='#0D26C4', opacity=0.5, thickness=5).encode(
    alt.Y('BoxOffice',
      scale=alt.Scale(zero=True),
      axis=alt.Axis(tickMinStep=1),
      #title='(V)Average_'+ option +'_by_Decade'
      ),
    tooltip=['BoxOffice', 'boxoffice_of_revenue', 'boxoffice_of_budget'],

  ).properties(
    width=600,
    height=600
  )
  revenue_chart= base.mark_bar(color='#64AF65', opacity=0.7, thickness=5).encode(
    alt.Y('revenue',
      scale=alt.Scale(zero=True),
      axis=alt.Axis(tickMinStep=1),
      #title='(V)Average_'+ option +'_by_Decade'
      ),
    tooltip=['revenue','revenue_of_budget','boxoffice_of_revenue'],

  ).properties(
    width=600,
    height=600
  )
  budget_chart= base.mark_bar(color='#FF5800', opacity=0.6, thickness=5).encode(
    alt.Y('budget',
      scale=alt.Scale(zero=True),
      axis=alt.Axis(tickMinStep=1),
      #title='(V)Average_'+ option +'_by_Decade'
      ),
    tooltip=['budget','revenue_of_budget','boxoffice_of_budget'],

  ).properties(
    width=600,
    height=600
  )

  with st.beta_expander("See the Chart."):

    col1, col2, col3 = st.beta_columns((1,1,1))
    
    #checkbox
    agree1 = col1.checkbox('box office')
    agree2 = col2.checkbox('revenue')
    agree3 = col3.checkbox('budget')
    if agree1:
      if agree1 and agree2:
        if agree1 and agree2 and agree3:
          st.write(revenue_chart+budget_chart+boxoffice_chart)
        else:
          st.write(boxoffice_chart+revenue_chart)          
      elif agree1 and agree3:
        st.write(boxoffice_chart+budget_chart)
      else:
        st.write(boxoffice_chart)
    elif agree2:
      if agree2 and agree3:
        st.write(revenue_chart+budget_chart) 
      else:
        st.write(revenue_chart)   
    elif agree3:
        st.write(budget_chart)

    




  #line chart-description
  st.markdown('''<a id="title">:popcorn: How is IMDB Rating/runtime distributes across the works? </a>''', unsafe_allow_html=True)
  st.markdown("You can interact with the chart by:")
  st.markdown("1. Select the attribute in the dropdown.")
  st.markdown("2. Hover on the line to see the numbers.")
  st.markdown("3. Compare with the average value with checkbox.")

   #select-feature
  option = st.selectbox(
  'Select one attribute you would like to see.',
  ('imdbRating','runtime'))
  #line chart  
  nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=['title'], empty='none')

  df = pd.DataFrame(related_movies_df)
  with st.beta_expander("See the dataframe."):
    st.dataframe(df)
    st.dataframe(d_avg)

  base = alt.Chart(df).encode(
        x=alt.X('title', sort=alt.EncodingSortField(field='release_date', order='ascending'),title="The title of films order by issued date")
  )
  line_A = base.mark_line(color='#0D26C4').encode(
    alt.Y(option, axis=alt.Axis(titleColor='#5276A7')),
  ).properties(
    width=600,
    height=600
  )
  # Transparent selectors across the chart. This is what tells us
  # the x-value of the cursor
  selectors = base.mark_point().encode(
    x=alt.X('title', sort=alt.EncodingSortField(field='release_date', order='ascending')),
    opacity=alt.value(0),
  ).add_selection(
    nearest
  )
  # Draw points on the line, and highlight based on selection
  points_A = line_A.mark_point(color='#0D26C4').encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
  )
  # Draw text labels near the points, and highlight based on selection
  text_A = line_A.mark_text(color='#0D26C4',align='left', dx=5, dy=-5).encode(
    text=alt.condition(nearest, option, alt.value(' '))
  )

  # Draw a rule at the location of the selection
  rules = alt.Chart(df).mark_rule(color='gray').encode(
    x=alt.X('title', sort=alt.EncodingSortField(field='release_date', order='ascending')),
  ).transform_filter(
    nearest
  )

  line_B = base.mark_line(color='#FF5800').encode(
    alt.Y(option+'_mean', axis=alt.Axis(titleColor='#5276A7')),
  ).properties(
    width=600,
    height=600
  )
  # Draw points on the line, and highlight based on selection
  points_B = line_B.mark_point(color='#FF5800').encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
  )
  # Draw text labels near the points, and highlight based on selection
  text_B = line_B.mark_text(align='left', dx=10, dy=-5, color='#FF5800').encode(
    text=alt.condition(nearest, option+'_mean', alt.value(' '))
  )   
  
  chart1 = alt.layer(line_A,points_A,text_A)
  #chart1 = alt.layer(chart1).resolve_scale(y='independent')
  chart1 = alt.layer(chart1,selectors,rules,line_B,points_B,text_B)
  chart2 = alt.layer(line_A,points_A,text_A)  
  chart2 = alt.layer(chart2).resolve_scale(y='independent')
  chart2 = alt.layer(chart2,selectors,rules)


  with st.beta_expander("See the Chart."):
    
    compare = st.checkbox('Compare with the average of the works.')
    if compare:
      st.write(chart1)
    else:  
      st.write(chart2)
def main():
  # use custom css
  with open('./styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    st.markdown('''<a id="header">:clapper:Film Producer/Actor Data Jam</a>''', unsafe_allow_html=True)
    st.markdown('This platform allows you to learn about the film producer/actor and their works.')

    st.markdown("""
    <img src="https://user-images.githubusercontent.com/7588145/117094736-908c0e80-ad32-11eb-8821-f5ee0fa6df02.png" id="bowie-img">
  """,unsafe_allow_html=True)

  with st.beta_expander("What is in the platform?"):
    st.markdown("This platform is consists of five parts:")
    st.markdown('''
              <ul id="project-parts-list">
              <li><a class="link" href="#basic-bio">1. Director/Actor's biography</a></li>
              <li><a class="link" href="#what-genres-are-the-works-in">2. Chart - What genres are the works in?</a></li>
              <li><a class="link" href="#what-s-the-financial-structure-of-the-works">3. Chart - What's the financial structure of the works?</a></li>
              <li><a class="link" href="#how-is-imdb-rating-runtime-distributes-across-the-works">4. Chart - How is IMDB Rating/runtime distributed across the works?</a></li>
              <li><a class="link" href="">5. Recommendation System</a></li>
              </ul>
              ''', unsafe_allow_html=True)  
    st.markdown("")
    st.markdown("<span class='small'>This project was completed by <strong>Vivian Young</strong> and <strong>Carol Ho</strong> for the Interactive Data Science (Spring 2021) course taught by Professors Adam Perer and Hendrik Strobelt.</span>", unsafe_allow_html=True)
    st.write("Original Dataset from the OMDB API and themoviedb API.")
    st.write("Photo by Denise Jans on Unsplash")
  add_textinput = st.text_input("Search for film producer/actor:", "Ang Lee")
      

  data = get_api_data(add_textinput)
  print(data)
  if data and data.get('works', {}).get('cast'):
    with_result(data)
  else:
    without_result()


if __name__ == '__main__':
  main()
