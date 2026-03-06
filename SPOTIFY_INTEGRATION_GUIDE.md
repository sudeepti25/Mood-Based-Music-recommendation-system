# 🎵 Spotify Integration Setup Guide

## Overview
This guide will help you integrate Spotify playback into your Mood-Based Music Recommendation System.

---

## ✅ Features Implemented

### 1. **30-Second Preview Player** (No Premium Required)
- Plays 30-second previews of songs directly in the app
- Uses Spotify's free preview URLs
- Works for ~80% of tracks

### 2. **"Open in Spotify" Button**
- Opens the full song in Spotify app/web
- Works for all tracks
- Users can play full songs with their Spotify account

### 3. **Track ID Integration**
- Uses `track_id` from your `dataset_with_moods_full.csv`
- Creates Spotify URIs: `spotify:track:{track_id}`
- Ready for future Spotify Web Playback SDK integration

---

## 🚀 Setup Instructions

### Step 1: Get Spotify API Credentials (FREE)

1. **Go to Spotify Developer Dashboard**
   - Visit: https://developer.spotify.com/dashboard
   - Log in with your Spotify account (free account is fine)

2. **Create an App**
   - Click "Create app"
   - Fill in:
     - **App name**: "Mood Music Recommender" (or any name)
     - **App description**: "Emotion-based music recommendation"
     - **Redirect URI**: `http://localhost:8501` (for Streamlit)
     - **APIs used**: Check "Web API"
   - Accept terms and click "Save"

3. **Get Your Credentials**
   - Click on your newly created app
   - Click "Settings"
   - Copy your:
     - **Client ID**
     - **Client Secret** (click "View client secret")

### Step 2: Configure Your App

Choose ONE of these methods:

#### **Method A: Environment Variables (Recommended for Development)**

**Windows (PowerShell):**
```powershell
$env:SPOTIFY_CLIENT_ID = "your_client_id_here"
$env:SPOTIFY_CLIENT_SECRET = "your_client_secret_here"
```

**Windows (Command Prompt):**
```cmd
set SPOTIFY_CLIENT_ID=your_client_id_here
set SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

Then run your app:
```powershell
cd FRONTEND
streamlit run app_with_spotify.py
```

#### **Method B: Streamlit Secrets (Recommended for Production)**

1. Create a secrets file:
   ```powershell
   mkdir .streamlit -Force
   New-Item -Path ".streamlit\secrets.toml" -ItemType File -Force
   ```

2. Edit `.streamlit/secrets.toml` and add:
   ```toml
   SPOTIFY_CLIENT_ID = "your_client_id_here"
   SPOTIFY_CLIENT_SECRET = "your_client_secret_here"
   ```

3. Update `app_with_spotify.py` to read from secrets:
   ```python
   # Replace this line:
   SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
   
   # With:
   SPOTIFY_CLIENT_ID = st.secrets.get("SPOTIFY_CLIENT_ID", os.environ.get("SPOTIFY_CLIENT_ID", ""))
   ```

### Step 3: Install Dependencies

```powershell
pip install spotipy requests
```

Or install all requirements:
```powershell
pip install -r requirements.txt
```

### Step 4: Run the App

```powershell
cd FRONTEND
streamlit run app_with_spotify.py
```

---

## 🎮 Usage

1. **Detect Emotion**: Take a photo with your webcam
2. **Get Recommendations**: Songs matching your mood appear
3. **Listen to Previews**: Click on a song to hear a 30-second preview
4. **Play Full Song**: Click "🎧 Open in Spotify" to play the full track

---

## 📊 What Works Without API Credentials

Even without Spotify API setup, the app will:
- ✅ Detect emotions
- ✅ Recommend songs
- ✅ Show "Open in Spotify" buttons (opens web/app)
- ❌ 30-second previews won't work

---

## 🎵 Advanced: Full Playback (Premium Required)

For **full playback control** in your app, you need:

### Option 1: Spotify Web Playback SDK (JavaScript)

**Requirements:**
- Spotify Premium account
- Web-based player integration

**Implementation:**
1. Add JavaScript to your Streamlit app using `components.html()`
2. Use Spotify Web Playback SDK
3. Control playback directly from your app

Example component:
```python
import streamlit.components.v1 as components

spotify_player_html = f"""
<script src="https://sdk.scdn.co/spotify-player.js"></script>
<script>
window.onSpotifyWebPlaybackSDKReady = () => {{
  const player = new Spotify.Player({{
    name: 'Mood Music Player',
    getOAuthToken: cb => {{ cb('YOUR_ACCESS_TOKEN'); }}
  }});
  player.connect();
}};
</script>
<div id="player"></div>
"""
components.html(spotify_player_html, height=300)
```

### Option 2: Spotify OAuth + Web API Playback

**Requirements:**
- Spotify Premium account
- OAuth authentication flow

**Features:**
- Start/pause/skip playback
- Control user's active Spotify device
- Create and manage playlists

This requires additional OAuth setup with redirect URLs.

---

## 🔧 Troubleshooting

### "Spotify API Not Configured" Warning
- Check that your environment variables are set correctly
- Verify Client ID and Secret are correct
- Make sure you're running the app in the same terminal where you set the variables

### "No Preview Available"
- ~20% of tracks don't have preview URLs
- Users can still click "Open in Spotify" to play the full song
- This is a Spotify API limitation, not your app

### Preview Player Not Loading
- Check internet connection
- Verify the `track_id` in your CSV is valid
- Some older tracks may not have previews

---

## 📝 File Structure

```
FRONTEND/
├── app.py                    # Original app
├── app_with_spotify.py       # NEW: App with Spotify integration
└── .streamlit/
    └── secrets.toml          # Spotify credentials (gitignored)
```

---

## 🌟 Alternative Solutions

If Spotify integration doesn't work for you:

### 1. **YouTube Music API**
- Similar to Spotify
- Uses video URLs instead of audio
- Free tier available

### 2. **Local Music Player**
- Use HTML5 audio player
- Requires local music files
- No internet needed

### 3. **Embed Spotify Widget**
- Use Spotify's embed player
- No API needed
- Limited control

### 4. **Create Playlist Links**
- Generate shareable playlist URLs
- Users can save to their Spotify
- No playback control

---

## 📚 Resources

- **Spotify Web API Docs**: https://developer.spotify.com/documentation/web-api
- **Spotipy Library**: https://spotipy.readthedocs.io/
- **Spotify Web Playback SDK**: https://developer.spotify.com/documentation/web-playback-sdk
- **Streamlit Components**: https://docs.streamlit.io/library/components

---

## 💡 Tips

1. **Rate Limits**: Free Spotify API has rate limits (typically 1000 requests/day)
2. **Caching**: The app caches preview URLs to reduce API calls
3. **Premium vs Free**: Preview playback works for all users; full playback requires Premium
4. **Track IDs**: Make sure your CSV has valid Spotify track IDs

---

## 🎯 Next Steps

1. ✅ Set up Spotify API credentials
2. ✅ Test preview playback
3. ⬜ Add OAuth for user-specific playlists
4. ⬜ Implement Spotify Web Playback SDK for full control
5. ⬜ Create "Save to Spotify" playlist feature

Enjoy your mood-based music experience! 🎵✨
