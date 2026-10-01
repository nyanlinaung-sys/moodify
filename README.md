# Moodify

Type how you feel, and Moodify turns it into a Spotify playlist.

The app runs sentiment analysis on your text, maps the result to a mood, and searches Spotify for tracks that match that mood. You can pick a song from the list and play it in the embedded Spotify player.

![Moodify screenshot](docs/screenshot.png)

## How it works

1. **You type a mood or a sentence** (for example, "I am sad" or "best day ever").
2. **The FastAPI backend scores the text** with TextBlob, which gives a polarity score from -1 (very negative) to +1 (very positive).
3. **The score is mapped to one of five moods:**

   | Polarity score | Mood | Spotify search terms |
   |---|---|---|
   | -1.0 to -0.3 | sad | sad emotional songs |
   | -0.3 to -0.05 | melancholy | mellow melancholy songs |
   | -0.05 to 0.05 | neutral | chill lofi relax |
   | 0.05 to 0.4 | good | feel good pop |
   | 0.4 to 1.0 | happy | happy upbeat dance hits |

4. **The backend searches the Spotify Web API** (through Spotipy) for 10 tracks and returns the name, artist, cover art, and link for each.
5. **The React frontend** shows the playlist and plays the selected track in a Spotify player.

The API response looks like this:

```json
{
  "mood": "sad",
  "polarity": -0.5,
  "playlist": [
    { "name": "...", "artist": "...", "image": "...", "spotify_url": "..." }
  ]
}
```

## Tech stack

- **Frontend:** React, Vite
- **Backend:** Python, FastAPI, Uvicorn
- **Sentiment analysis:** TextBlob
- **Music data:** Spotify Web API via Spotipy (client credentials flow)
- **Config:** python-dotenv for API credentials

## Run it locally

You need Python 3.9+, Node.js, and a free [Spotify Developer](https://developer.spotify.com/dashboard) app to get a Client ID and Client Secret.

### 1. Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a file named `.env` in the project root:

```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
```

Start the API:

```bash
uvicorn main:app --reload
```

Try it at `http://127.0.0.1:8000/docs`, or open `http://127.0.0.1:8000/recommend?user_mood=I am happy`.

### 2. Frontend

In a second terminal:

```bash
npm install
npm run dev
```

Open `http://localhost:5173`.

## Mood log

Each request saves the detected mood, polarity score, and a timestamp to `mood_log.csv`. The text you type is not saved. The file is ignored by git and is meant for simple analysis later, such as charting how moods are distributed.

## Limitations and next steps

- **Sentiment is lexicon-based.** TextBlob scores words from a fixed dictionary, so it works best on short, clear sentences and misses sarcasm or slang.
- **Search matches keywords, not audio.** Spotify's search looks at track titles and metadata, so a search for "sad" can return songs with "Emotional" or "Sad" in the title rather than songs that actually sound sad.
- **Planned improvements:**
  - Use a stronger emotion model instead of a single polarity score
  - Recommend by audio characteristics (valence, energy) instead of title keywords
  - Chart the mood log in a small dashboard
  - Deploy the app with a live demo link

## Notes

- Never commit your `.env` file. It is listed in `.gitignore`.
- If you see an `invalid_client` error from Spotify, check that your `.env` values come from the same Spotify app, and that no old `SPOTIPY_` variables are set in your terminal.

## Author

Nyan Lin Aung | [GitHub](https://github.com/nyanlinaung-sys) | [Portfolio](https://nyanlinaung.com)
