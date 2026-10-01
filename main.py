from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from spotipy.oauth2 import SpotifyClientCredentials, logger
from textblob import TextBlob
from datetime import datetime
import spotipy
import logging
import os
from dotenv import load_dotenv

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # This is the "Open All Gates" setting for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load variables from the .env file
load_dotenv()

# Get credentials securely from the environment
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

# 2. Initialize the official logger
logger = logging.getLogger("uvicorn.error")

@app.get("/recommend")
async def recommend(user_mood: str):
    try:
        # 1. AI Analysis
        analysis = TextBlob(user_mood)
        score = analysis.sentiment.polarity # type: ignore
        
        # 2. get the current year dynamically
        current_year = datetime.now().year
        vibe_query = f"{user_mood} {current_year}"

        auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # 3. SEARCH FOR TRACKS ONLY (Avoids 403 Errors)
        # market='US' ensures we get familiar, localized hits
        results = sp.search(q=vibe_query, type='track', limit=10, market='US')
        tracks = results.get('tracks', {}).get('items', []) # type: ignore         

        # 4. Format Output
        playlist_output = []
        for track in tracks:
            playlist_output.append({
                "name": track['name'],
                "artist": track['artists'][0]['name'],
                "image": track['album']['images'][0]['url'] if track['album']['images'] else "",
                "spotify_url": track['external_urls']['spotify']
            })
        
        return {"playlist": playlist_output}

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"playlist": []}