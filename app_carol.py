import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import requests



def main():
  # use custom css
  #with open('./styles.css') as f:
    #st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
  #themoviedb API - search for keywords
  response = requests.get("https://api.themoviedb.org/3/search/person?api_key=8bab42520fb79424d47245ab1e5406cf&query=Ang+Lee")
  r = response.json()
  df=pd.DataFrame(r['results'])
  st.markdown(response.status_code)
  st.dataframe(df)
#themoviedb API - search for person bio by id
  response = requests.get("https://api.themoviedb.org/3/person/1614?api_key=8bab42520fb79424d47245ab1e5406cf&language=en-US")
  r = response.json()
  #df=pd.DataFrame(r['results'])
  st.markdown(response.status_code)
  st.markdown(r)

  #themoviedb API - search for person's work by id
  response = requests.get("https://api.themoviedb.org/3/person/1614/movie_credits?api_key=8bab42520fb79424d47245ab1e5406cf")
  r = response.json()
  df=pd.DataFrame(r['cast'])
  st.markdown(response.status_code)
  st.dataframe(df)
  #themoviedb API - search for movie by id
  response = requests.get("https://api.themoviedb.org/3/person/1614/movie_credits?api_key=8bab42520fb79424d47245ab1e5406cf")
  r = response.json()
  df=pd.DataFrame(r['cast'])
  st.markdown(response.status_code)
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
  add_text = st.sidebar.markdown("Movie Attributes")
  add_checkbox = st.sidebar.checkbox("budget")
  add_checkbox = st.sidebar.checkbox("genre")
  add_checkbox = st.sidebar.checkbox("revenue")
  add_checkbox = st.sidebar.checkbox("rating")



main()
