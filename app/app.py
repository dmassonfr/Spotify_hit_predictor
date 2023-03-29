import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import plotly.express as px
import numpy as np
import requests 

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
      st.markdown('no audio preview available')
    
    col1, col2 = st.columns(2)
    with col1:
      st.metric("Popularity (actual)", track_data['popularity'])
    with col2:
      if track_data['explicit'] == True:
        st.image('https://img.icons8.com/color/512/18-plus.png', width=80)
  
  # call the fastapi
  
  fastapi = "https://spotify-project-api-spjvgnnqdq-ew.a.run.app/predict"
  
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

  response = requests.post(url=fastapi, json=features)
  
  st.markdown(' ')
  col1, col2 = st.columns([4,1])
  with col1:
    st.markdown('#### :green[Model Inputs:]')
  with col2:
    st.markdown('#### :green[Output:]')
    
  col1, col2 = st.columns([4,1])
  with col1:
    # plot a feature chart
    # assemble all features to display
    polar_audio_features = pd.DataFrame(audio_features, index=[0]).drop(
      columns=["type", "id", "uri", "track_href", "analysis_url", "tempo", 
              "time_signature", "key", "duration_ms", "mode", "loudness"])
    polar_audio_features.rename(columns={'tempo_norm':'tempo',
                                        'loudness_norm':'loudness'}, inplace=True)
    polar_other_features =pd.DataFrame({'artist popularity':artist_features['popularity']/100,
                                        'artist followers':artist_features['followers_norm'],
                                        'track length': track_data['duration_norm']}, index=[0])
    
    features_norm = pd.melt(pd.concat([polar_audio_features, polar_other_features], axis=1))
    
    fig = px.line_polar(features_norm, r='value', theta='variable', 
                        template="plotly_dark", line_close=True, range_r = (0,1))
    fig.update_traces(fill='toself', line_color='#90ee90')
    fig.update_layout(font_size=15)
    st.plotly_chart(fig, use_container_width=True, sharing="streamlit", theme="streamlit")
  with col2:
    st.metric("Popularity (predicted)", round(response.json()[0], 3)*100)
  
  st.markdown('### API (model backend)')
  st.markdown('print request and response of prediction model')
  st.markdown('#### :green[Request]')
  st.write(features)
  
  st.markdown('#### :green[Response (Prediction)]')
  st.write(response.json())
  