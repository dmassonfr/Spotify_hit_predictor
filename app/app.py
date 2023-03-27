import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import plotly.express as px

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
st.sidebar.image('https://cdn-icons-png.flaticon.com/512/408/408748.png', width=100)
st.sidebar.title('Spotify Hit Predictor')

query = st.sidebar.text_input('Search on Spotify:', '')

@st.cache_resource
def get_search_results(query):
  result = spotify.search(query, limit=1, type='track')['tracks']['items'][0]
  track_data = {}
  track_data['artist_name'] = result['artists'][0]['name'],
  track_data['artist_uri'] = result['artists'][0]['uri'],
  track_data['track_name'] = result['name'],
  track_data['track_uri'] = result['uri']
  track_data['album_name'] = result['album']['name']
  track_data['image_url'] = result['album']['images'][0]['url']
  track_data['preview_url'] = result['preview_url']
  track_data['popularity'] = result['popularity']
  audio_features = spotify.audio_features(result['id'])[0]
  return track_data, audio_features

if st.sidebar.button('Search Track'):
  track_data, audio_features = get_search_results(query)

  st.markdown("# :green[" + track_data['track_name'][0] + "]")
  col1, col2 = st.columns([1, 2])
  with col1:
    st.image(track_data['image_url'])
  with col2:
    st.markdown("by **:green[" + track_data['artist_name'][0] + "]**" + " on **:green[" + track_data['album_name'] + "]**")
    if track_data['preview_url']:
      st.audio(track_data['preview_url'])
    else:
      st.write('no audio preview available')
    
  col1, col2, col3, col4, col5 = st.columns(5)
  with col1:
    st.metric("Popularity Score", track_data['popularity'])
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
    pass
  with col2:
    st.metric('loudness:', audio_features['loudness'])
  with col3:
    st.metric('speechiness:', audio_features['speechiness'])
  with col4:
    st.metric('acousticness:', audio_features['acousticness'])
  with col5:
    st.metric('liveness:', audio_features['liveness'])
  
  features_norm = pd.melt(pd.DataFrame(audio_features, index=[0]).drop(
    columns=["type", "id", "uri", "track_href", "analysis_url", "tempo", "time_signature", "key", "duration_ms", "mode", "loudness"]))
  
  fig = px.line_polar(features_norm, r='value', theta='variable', template="plotly_dark", line_close=True, range_r = (0,1))
  fig.update_traces(fill='toself')
  fig.update_layout(font_size=15)
  st.plotly_chart(fig, use_container_width=True, sharing="streamlit", theme="streamlit")