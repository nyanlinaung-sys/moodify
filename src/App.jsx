import React, { useState, useEffect } from 'react';
import musicAnimation from "./assets/astronaut.json";

function App() {
  const [mood, setMood] = useState('');
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeSong, setActiveSong] = useState(null);

  useEffect(() => {
    if (!document.querySelector('script[src*="lottie-player"]')) {
      const script = document.createElement('script');
      script.src = "https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js";
      script.async = true;
      document.body.appendChild(script);
    }
  }, []);

  const getPlaylist = async () => {
    if (!mood) return alert("Please enter a mood!");
    setLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/recommend?user_mood=${encodeURIComponent(mood)}`);
      const data = await response.json();
      setSongs(data.playlist || []);
      // Auto-select the first song
      if (data.playlist && data.playlist.length > 0) {
        setActiveSong(data.playlist[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // CLEAN EMBED LOGIC: Converts standard Spotify link to Embed link
  const getEmbedUrl = (spotifyUrl) => {
    if (!spotifyUrl) return "";
    // Replaces 'track/' with 'embed/track/' and handles clean URL structure
    return spotifyUrl.replace("open.spotify.com/track/", "open.spotify.com/embed/track/");
  };

  return (
    <div style={{ backgroundColor: '#121212', color: 'white', minHeight: '100vh', width: '100vw', margin: 0, padding: '20px', boxSizing: 'border-box', fontFamily: 'sans-serif', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      
      {/* HEADER SECTION */}
      <div style={{ width: '100%', maxWidth: '1200px', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
        <h1 style={{ color: '#1DB954', fontSize: '3rem', margin: '0' }}>Moodify</h1>
        
        <div style={{ width: '180px', height: '180px' }}>
          <lottie-player src={JSON.stringify(musicAnimation)} background="transparent" speed="1" style={{ width: '100%', height: '100%' }} loop autoplay></lottie-player>
        </div>
        
        <div style={{ display: 'flex', gap: '10px', marginBottom: '40px' }}>
          <input 
            type="text" value={mood} onChange={(e) => setMood(e.target.value)} placeholder="What's the vibe?"
            style={{ padding: '12px 20px', width: '250px', borderRadius: '30px', border: 'none', outline: 'none' }}
          />
          <button onClick={getPlaylist} style={{ padding: '12px 30px', borderRadius: '30px', backgroundColor: '#1DB954', color: 'white', border: 'none', fontWeight: 'bold', cursor: 'pointer' }}>
            {loading ? '...' : 'Go'}
          </button>
        </div>
      </div>

      {/* TWO COLUMN CONTENT */}
      <div style={{ display: 'flex', width: '100%', maxWidth: '1100px', gap: '40px', flexWrap: 'wrap', justifyContent: 'center' }}>
        
        {/* LIST COLUMN */}
        <div style={{ flex: '1.2', minWidth: '350px' }}>
          <h3 style={{ borderBottom: '1px solid #333', paddingBottom: '10px', color: '#b3b3b3' }}>Playlist</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {songs.map((song, index) => (
              <div 
                key={index} 
                onClick={() => setActiveSong(song)}
                style={{ 
                  backgroundColor: activeSong?.spotify_url === song.spotify_url ? '#282828' : '#181818', 
                  borderRadius: '8px', padding: '12px', display: 'flex', alignItems: 'center', 
                  gap: '15px', cursor: 'pointer', transition: '0.2s',
                  border: activeSong?.spotify_url === song.spotify_url ? '1px solid #1DB954' : '1px solid transparent'
                }}
              >
                <img src={song.image} alt="" style={{ width: '45px', height: '45px', borderRadius: '4px' }} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>{song.name}</div>
                  <div style={{ color: '#b3b3b3', fontSize: '0.8rem' }}>{song.artist}</div>
                </div>
                {activeSong?.spotify_url === song.spotify_url ? (
                  <span style={{ color: '#1DB954', fontSize: '0.8rem', fontWeight: 'bold' }}>SELECTED</span>
                ) : (
                  <div style={{ color: '#555' }}>▶</div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* PLAYER COLUMN */}
        <div style={{ flex: '0.8', minWidth: '350px', position: 'sticky', top: '20px' }}>
          <h3 style={{ borderBottom: '1px solid #333', paddingBottom: '10px', color: '#b3b3b3' }}>Player</h3>
          <div style={{ backgroundColor: '#181818', borderRadius: '15px', padding: '10px', minHeight: '352px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {activeSong ? (
              <iframe 
                src={getEmbedUrl(activeSong.spotify_url)} 
                width="100%" 
                height="352" 
                frameBorder="0" 
                allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
                style={{ borderRadius: '12px' }}
              ></iframe>
            ) : (
              <p style={{ color: '#444' }}>Select a track to play</p>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;