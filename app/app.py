import streamlit as st
import time

st.sidebar.image('https://cdn-icons-png.flaticon.com/512/2424/2424869.png', width=60)
st.sidebar.title('Spotify Music Search')

query = st.sidebar.text_input('Please enter your search query and hit Enter.', key="input")

# lz_uri = 'spotify:artist:0IVcLMMbm05VIjnzPkGCyp' # J Dilla
# lz_uri = 'spotify:artist:6P7H3ai06vU1sGvdpBwDmE'# Steele Dan
lz_uri = 'spotify:artist:0kbYTNQb4Pb1rPbbaF0pT4'# Miles Davis


spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET))
results = spotify.artist_top_tracks(lz_uri)


for track in results['tracks'][:10]:
    print('track    : ' + track['name'])
    if track['preview_url']:
      print('audio    : ' + track['preview_url'])
      file = wget.download(track['preview_url'])
    else:
      print('### no audio preview available ###')
    print('cover art: ' + track['album']['images'][0]['url'])
    print()