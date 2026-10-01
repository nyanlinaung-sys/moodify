import csv
import logging
import os
from datetime import datetime, timezone

import spotipy
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from spotipy.oauth2 import SpotifyClientCredentials
from textblob import TextBlob

# ---------------------------------------------------------------
# Setup
# ---------------------------------------------------------------
load_dotenv()  # reads SPOTIPY_CLIENT_ID / SPOTIPY_CLIENT_SECRET from .env

logger = logging.getLogger("uvicorn.error")

CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    logger.warning("Spotify credentials are missing. Check your .env file.")

app = FastAPI(title="Moodify API")

# Only allow your own frontend (Vite dev server) instead of "*".
# When you deploy, add your real site URL to this list.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Create the Spotify client once, not on every request.
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET
    )
)

MOOD_LOG = "mood_log.csv"  # add this file to .gitignore


# ---------------------------------------------------------------
# Sentiment -> mood label -> Spotify search terms
# ---------------------------------------------------------------
def mood_from_score(score: float) -> str:
    """Convert a TextBlob polarity score (-1 to 1) into a mood label."""
    if score <= -0.3:
        return "sad"
    if score < -0.05:
        return "melancholy"
    if score <= 0.05:
        return "neutral"
    if score < 0.4:
        return "good"
    return "happy"


SEARCH_TERMS = {
    "sad": "sad emotional songs",
    "melancholy": "mellow melancholy songs",
    "neutral": "chill lofi relax",
    "good": "feel good pop",
    "happy": "happy upbeat dance hits",
}


def log_mood(label: str, score: float) -> None:
    """Save the mood result (not the user's text) so you can analyze it later."""
    try:
        new_file = not os.path.exists(MOOD_LOG)
        with open(MOOD_LOG, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if new_file:
                writer.writerow(["timestamp_utc", "mood", "polarity"])
            writer.writerow(
                [datetime.now(timezone.utc).isoformat(), label, round(score, 3)]
            )
    except OSError as e:
        logger.error(f"Could not write mood log: {e}")


# ---------------------------------------------------------------
# Route
# ---------------------------------------------------------------
@app.get("/recommend")
async def recommend(user_mood: str):
    user_mood = user_mood.strip()
    if not user_mood:
        return {"mood": None, "polarity": None, "playlist": [],
                "error": "Please enter how you feel."}

    try:
        # 1. Sentiment analysis (TextBlob lexicon-based polarity)
        score = TextBlob(user_mood).sentiment.polarity # type: ignore
        label = mood_from_score(score)
        log_mood(label, score)

        # 2. Search Spotify using the detected mood
        results = sp.search(
            q=SEARCH_TERMS[label], type="track", limit=10, market="US"
        )
        assert results is not None
        tracks = results.get("tracks", {}).get("items", [])

        # 3. Format output
        playlist = [
            {
                "name": t["name"],
                "artist": t["artists"][0]["name"],
                "image": t["album"]["images"][0]["url"]
                if t["album"]["images"]
                else "",
                "spotify_url": t["external_urls"]["spotify"],
            }
            for t in tracks
        ]

        return {"mood": label, "polarity": round(score, 2), "playlist": playlist}

    except Exception as e:
        logger.error(f"Recommend failed: {e}")
        return {"mood": None, "polarity": None, "playlist": [],
                "error": "Something went wrong. Please try again."}