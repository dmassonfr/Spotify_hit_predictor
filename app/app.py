import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import plotly.express as px
import scipy.io.wavfile as wavfile
import numpy as np
import requests
import json
 

# initialize Spotify client (once and store)
@st.cache_resource
def init_spotipy(spotify_client_id, spotify_client_secret):
  spotify = spotipy.Spotify(client_credentials_manager=
                          SpotifyClientCredentials(spotify_client_id, 
                                                   spotify_client_secret))
  return spotify

spotify = init_spotipy(spotify_client_id = st.secrets['SPOTIPY_CLIENT_ID'], 
                       spotify_client_secret = st.secrets['SPOTIPY_CLIENT_SECRET'])

# Sidebar for user input
st.image('https://cdn-icons-png.flaticon.com/512/408/408748.png', width=100)
st.title('Spotify Hit Predictor')

query = st.text_input('Search on Spotify:', '')

@st.cache_resource
def get_search_results(query):
  result = spotify.search(query, limit=1, type='track')['tracks']['items'][0]
  track_data = {}
  #artist
  track_data['artist_name'] = result['artists'][0]['name'],
  track_data['artist_uri'] = result['artists'][0]['uri'],
  
  #track
  track_data['track_name'] = result['name'],
  track_data['track_uri'] = result['uri']
  track_data['track_url'] = result['external_urls']['spotify']
  track_data['preview_url'] = result['preview_url']
  track_data['explicit'] = result['explicit']
  track_data['popularity'] = result['popularity'] # target!
  track_data['duration_ms'] = result['duration_ms']
  track_data['duration_norm'] = np.log10(track_data['duration_ms']/1000000)/3+1
  track_data['explicit_num'] = float(track_data['explicit'])
  
  #date 
  track_data['release_date'] = result['album']['release_date']
  track_data['delta_days'] = pd.Timestamp.today() - pd.to_datetime(track_data['release_date'], format = '%Y-%m-%d')
  track_data['delta_days'] = track_data['delta_days'].days
  
  track_data['album_name'] = result['album']['name']
  track_data['album_link'] = result['album']['external_urls']['spotify']
  track_data['image_url'] = result['album']['images'][0]['url']
  
  #audio features
  audio_features = spotify.audio_features(result['id'])[0]
  if audio_features['loudness'] > 0:
    audio_features['loudness'] = 0
  audio_features['loudness_norm'] = np.exp(1+ audio_features['loudness']/15)/np.e
  if audio_features['tempo'] > 200:
    audio_features['tempo'] = 200
  if audio_features['tempo'] < 50:
    audio_features['tempo'] = 50
  audio_features['tempo_norm'] = (audio_features['tempo'] - 50)/150
  
  #artist features
  artist_features = spotify.artist(result['artists'][0]['uri'])
  artist_features['followers_norm'] = np.log10(artist_features['followers']['total']+1)/10
  
  return track_data, audio_features, artist_features

if st.button('Search Track'):
  track_data, audio_features, artist_features = get_search_results(query)

  st.markdown("# [:green[" + track_data['track_name'][0] + "]](" +
              track_data['track_url'] + ")")
  
  col1, col2 = st.columns([1, 2])
  with col1:
    st.image(track_data['image_url'])
  with col2:
    st.markdown("by **[:green[" + track_data['artist_name'][0] 
                + "]](" + artist_features['external_urls']['spotify'] + ")**" + 
                " on **[:green[" + track_data['album_name'] + "]](" 
                + track_data['album_link'] + ")**" +
                " (" + str(track_data['release_date']) + ")")
    if track_data['preview_url']:
      st.audio(track_data['preview_url'])
    else:
      st.write('no audio preview available')
    
  col1, col2, col3, col4, col5 = st.columns(5)
  with col1:
    st.metric("popularity score", track_data['popularity'])
  with col2:
    st.metric('danceability:', audio_features['danceability'])
  with col3:
    st.metric('tempo:', audio_features['tempo'])
  with col4:
    st.metric('valence:', audio_features['valence'])
  with col5:
    st.metric('energy:', audio_features['energy'])
  
  col1, col2, col3, col4, col5 = st.columns(5)
  with col1:
    if track_data['explicit'] == True:
      st.markdown(':red[explicit!]')
  with col2:
    st.metric('loudness:', audio_features['loudness'])
  with col3:
    st.metric('speechiness:', audio_features['speechiness'])
  with col4:
    st.metric('acousticness:', audio_features['acousticness'])
  with col5:
    st.metric('liveness:', audio_features['liveness'])
    
  col1, col2, col3, col4, col5 = st.columns(5)
  with col1:
    st.metric('days old:', track_data['delta_days']) 
  with col2:
    st.metric('loudness (norm):', audio_features['tempo_norm'])
  with col3:
    st.metric('artist popularity:', artist_features['popularity'])
  with col4:
    st.metric('artist followers:', artist_features['followers']['total'])
  with col5:
    st.metric('followers (norm):', artist_features['followers_norm'])
  
  # plot a feature chart
  features_norm = pd.melt(pd.DataFrame(audio_features, index=[0]).drop(
    columns=["type", "id", "uri", "track_href", "analysis_url", "tempo", 
             "time_signature", "key", "duration_ms", "mode", "loudness"]))
  
  fig = px.line_polar(features_norm, r='value', theta='variable', 
                      template="plotly_dark", line_close=True, range_r = (0,1))
  fig.update_traces(fill='toself', line_color='#90ee90')
  fig.update_layout(font_size=15)
  st.plotly_chart(fig, use_container_width=True, sharing="streamlit", theme="streamlit")
  
  # call the fastapi
  
  fastapi = "http://127.0.0.1:8000/predict"
  
  features = [
    {
      "explicit":track_data['explicit_num'],
      "artist_popularity":artist_features['popularity']/100,
      "danceability": audio_features['danceability'],
      "energy": audio_features['energy'],
      "speechiness": audio_features['speechiness'],
      "acousticness": audio_features['acousticness'],
      "instrumentalness": audio_features['instrumentalness'],
      "liveness": audio_features['liveness'],
      "valence": audio_features['valence'],
      "delta_days": track_data['delta_days'],
      "loudness_norm": audio_features['loudness_norm'],
      "tempo_norm": audio_features['tempo_norm'],
      "followers_norm":artist_features['followers_norm'],
      "duration_norm": track_data['duration_norm']
    }
  ]
  
  st.write(features)

  
  response = requests.post(url=fastapi, json=features)
  st.write(response.json())
  #st.metric('Model prediction:', round(float(response.text['0']) * 100, 3))