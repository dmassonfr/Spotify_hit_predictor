import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
import pandas as pd

spotify_client_id = st.secrets['SPOTIPY_CLIENT_ID']
spotify_client_secret = st.secrets['SPOTIPY_CLIENT_SECRET']

st.sidebar.image('https://cdn-icons-png.flaticon.com/512/2424/2424869.png', width=60)
st.sidebar.title('Spotify Music Search')

#query = st.sidebar.text_input('Please enter your search query and hit Enter.', key="input")

@st.cache_data
def get_select_box_data():

    return pd.DataFrame({
          'artist': ['J Dilla', 'Steele Dan', 'Miles Davis'],
          'lz_uri': ['spotify:artist:0IVcLMMbm05VIjnzPkGCyp', 
                            'spotify:artist:6P7H3ai06vU1sGvdpBwDmE', 
                            'spotify:artist:0kbYTNQb4Pb1rPbbaF0pT4']
        })

df = get_select_box_data()

option = st.sidebar.selectbox('Select an artist', df['artist'])

#filtered_df = df[df['artist'] == option]
#st.write(filtered_df)

lz_uri = df[df['artist'] == option]['lz_uri'].to_string(index = False)
artist_name = df[df['artist'] == option]['artist'].to_string(index = False)


spotify = spotipy.Spotify(client_credentials_manager=
                          SpotifyClientCredentials(spotify_client_id, 
                                                   spotify_client_secret))
results = spotify.artist_top_tracks(lz_uri)

st.write('# TOP3 Tracks for ' + artist_name)
for track in results['tracks'][:3]:
  col1, col2 = st.columns([1, 2])
  with col1:
    st.image(track['album']['images'][0]['url'])
  with col2:
    st.write('### ' + track['name'])
    st.write('by ' + artist_name)
    if track['preview_url']:
      st.audio(track['preview_url'])
    else:
      st.write('no audio preview available')
  st.write(' ')
  st.write(' ')