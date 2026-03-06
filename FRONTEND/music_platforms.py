"""
Multi-Platform Music Player Integration
Supports: Spotify, YouTube Music, Apple Music, SoundCloud
Works WITHOUT any API setup!
"""

import streamlit as st
import urllib.parse

def get_spotify_url(track_id):
    """Get Spotify track URL"""
    return f"https://open.spotify.com/track/{track_id}"

def get_youtube_music_url(track_name, artist):
    """Search YouTube Music for track"""
    query = urllib.parse.quote(f"{track_name} {artist}")
    return f"https://music.youtube.com/search?q={query}"

def get_apple_music_url(track_name, artist):
    """Search Apple Music for track"""
    query = urllib.parse.quote(f"{track_name} {artist}")
    return f"https://music.apple.com/us/search?term={query}"

def get_soundcloud_url(track_name, artist):
    """Search SoundCloud for track"""
    query = urllib.parse.quote(f"{track_name} {artist}")
    return f"https://soundcloud.com/search?q={query}"

def get_youtube_url(track_name, artist):
    """Search regular YouTube for track"""
    query = urllib.parse.quote(f"{track_name} {artist} official audio")
    return f"https://www.youtube.com/results?search_query={query}"

def render_music_buttons(track_id, track_name, artist, platforms=['spotify', 'youtube', 'apple']):
    """
    Render music platform buttons
    
    Args:
        track_id: Spotify track ID
        track_name: Name of the track
        artist: Artist name
        platforms: List of platforms to show ['spotify', 'youtube', 'apple', 'soundcloud', 'youtube_music']
    """
    
    urls = {
        'spotify': get_spotify_url(track_id),
        'youtube': get_youtube_url(track_name, artist),
        'youtube_music': get_youtube_music_url(track_name, artist),
        'apple': get_apple_music_url(track_name, artist),
        'soundcloud': get_soundcloud_url(track_name, artist)
    }
    
    button_config = {
        'spotify': {'label': '🎧 Spotify', 'type': 'primary'},
        'youtube': {'label': '▶️ YouTube', 'type': 'secondary'},
        'youtube_music': {'label': '🎵 YT Music', 'type': 'secondary'},
        'apple': {'label': '🍎 Apple', 'type': 'secondary'},
        'soundcloud': {'label': '☁️ SoundCloud', 'type': 'secondary'}
    }
    
    # Create columns based on number of platforms
    cols = st.columns(len(platforms))
    
    for idx, platform in enumerate(platforms):
        if platform in urls:
            with cols[idx]:
                config = button_config[platform]
                st.link_button(
                    config['label'],
                    urls[platform],
                    use_container_width=True
                )

# Example usage in Streamlit:
if __name__ == "__main__":
    st.title("🎵 Multi-Platform Music Player")
    
    # Example track
    track_id = "5SuOikwiRyPMVoIQDJUgSV"
    track_name = "Comedy"
    artist = "Gen Hoshino"
    
    st.subheader(f"{track_name} - {artist}")
    
    # Show all platforms
    render_music_buttons(
        track_id=track_id,
        track_name=track_name,
        artist=artist,
        platforms=['spotify', 'youtube', 'apple', 'soundcloud']
    )
    
    st.markdown("---")
    
    # Or just Spotify + YouTube (most common)
    st.subheader("Simplified Version (2 buttons)")
    render_music_buttons(
        track_id=track_id,
        track_name=track_name,
        artist=artist,
        platforms=['spotify', 'youtube']
    )
