import os
from flask import Flask, session, request, redirect, render_template, abort
from flask_session import Session
from src.models.flask_route_utils import redirect_to_sign_in_if_not_auth
import spotipy
from dotenv import load_dotenv

load_dotenv()

lesserafim = 'spotify:artist:4SpbR6yFEvexJuaBpgAU5p'

app = Flask(__name__)
app.config['SPOTIPY_CLIENT_ID'] = os.environ.get('SPOTIPY_CLIENT_ID')
app.config['SPOTIPY_CLIENT_SECRET'] = os.environ.get('SPOTIPY_CLIENT_SECRET')
app.config['SPOTIPY_REDIRECT_URI'] = os.environ.get('SPOTIPY_REDIRECT_URI')

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

REQUIRED_SCOPES = ['user-modify-playback-state', 'user-read-playback-state']

@app.get('/signin')
def get_signin():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=REQUIRED_SCOPES,
                                               cache_handler=cache_handler,
                                               show_dialog=True)
    return render_template('signin.html', redirect_url=auth_manager.get_authorize_url())

@app.route('/')
def index():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=REQUIRED_SCOPES,
                                               cache_handler=cache_handler,
                                               show_dialog=True)
    if request.args.get("code"):
        # Step 2. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/signin')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 1. Display sign in link when no token
        return get_signin()
    
    # Step 3. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    users_name = spotify.me()["display_name"]

    return render_template('index.html', name=users_name)



@app.get('/callback')
def callback():
    scope = 'user-modify-playback-state'
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope,
                                               cache_handler=cache_handler,
                                               show_dialog=True)
    if request.args.get("code"):
        # Step 2. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')
    else:
        return abort(400)


@app.post('/currently-playing')
def post_currently_playing():
    scope = 'user-read-playback-state'
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope, cache_handler=cache_handler)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    print(f'{track=}')
    # redirect_to_sign_in_if_not_auth(auth_manager, cache_handler)
    return render_template('index.html', currently_playing_track=track)


if __name__ == '__main__':
    app.run(threaded=True,
    port=int(os.environ.get("SPOTIPY_REDIRECT_URI", 8080).split(":")[-1].split("/")[0]))