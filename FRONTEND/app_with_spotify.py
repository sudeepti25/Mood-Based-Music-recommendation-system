import streamlit as st
import cv2
import numpy as np
import pandas as pd
import time
from tensorflow.keras.models import load_model
import os
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

# -----------------------------
# CONFIG
# -----------------------------
MODEL_PATH = r"C:\Users\dyash\OneDrive\Desktop\Mood-Based-Music-recommendation-system\MODELS\cnn_model2.h5"
DATA_PATH = r"C:\Users\dyash\OneDrive\Desktop\Mood-Based-Music-recommendation-system\final_dataset.csv"
TARGET_SIZE = (48, 48)  # FER2013 image size
FRAME_SKIP = 3

EMOTIONS = ['angry','happy','sad','neutral']

# Mapping emotion → mood category in dataset
# Updated to match actual mood categories in dataset_with_moods_full.csv
emotion_to_moodcat = {
    'happy': ['Happy / Energetic (High Beat Party)'],
    'sad': ['Calm / Peaceful'],
    'angry': ['Uplifting / Positve'],  # Note: Keep typo if it exists in dataset
    'neutral': ['Balanced / Neutral', 'Balnaced / Neutral']  # Handle both spellings
}

# -----------------------------
# SPOTIFY CONFIGURATION
# -----------------------------
# You need to set these in Streamlit secrets or environment variables
# Get them from: https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")

# -----------------------------
# UTILITY FUNCTIONS
# -----------------------------

@st.cache_resource
def load_emotion_model(path=MODEL_PATH):
    if not os.path.exists(path):
        st.error(f"❌ Model not found at {path}")
        st.stop()
    model = load_model(path)
    return model

@st.cache_data
def load_spotify_data(path=DATA_PATH):
    if not os.path.exists(path):
        st.error(f"❌ Spotify dataset not found at {path}")
        st.stop()
    df = pd.read_csv(path)
    df = df.dropna(subset=["MoodCategory", "track_name", "artists"])
    return df

@st.cache_resource
def init_spotify_client():
    """Initialize Spotify client with credentials"""
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        return None
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        return sp
    except Exception as e:
        st.warning(f"⚠️ Spotify API initialization failed: {e}")
        return None

def get_track_preview_url(sp, track_id):
    """Get 30-second preview URL for a track"""
    if sp is None:
        return None
    try:
        track = sp.track(track_id)
        return track.get('preview_url'), track.get('external_urls', {}).get('spotify')
    except Exception as e:
        print(f"Error fetching track {track_id}: {e}")
        return None, None

def preprocess_face(face_img, target_size=TARGET_SIZE):
    # Ensure RGB format (3 channels) for the model
    if len(face_img.shape) == 2:
        face_img = cv2.cvtColor(face_img, cv2.COLOR_GRAY2RGB)
    elif face_img.shape[2] == 4:
        face_img = cv2.cvtColor(face_img, cv2.COLOR_BGRA2RGB)
    elif face_img.shape[2] == 3:
        face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    
    face_resized = cv2.resize(face_img, target_size)
    face_resized = face_resized.astype('float32') / 255.0
    face_resized = np.expand_dims(face_resized, axis=0)
    return face_resized

def predict_emotion(model, face_crop):
    x = preprocess_face(face_crop)
    preds = model.predict(x, verbose=0)[0]
    idx = np.argmax(preds)
    label = EMOTIONS[idx]
    confidence = float(preds[idx])
    return {"label": label, "confidence": confidence}

def recommend_songs(df, emotion_label, top_n=10):
    moods = emotion_to_moodcat.get(emotion_label.lower(), [])
    if not moods:
        st.warning(f"⚠️ No mood mapping found for emotion: {emotion_label}")
        return pd.DataFrame()
    
    # Debug: Show what we're looking for
    st.info(f"🔍 Looking for moods: {moods} in dataset")
    
    filtered = df[df["MoodCategory"].isin(moods)]
    
    # Debug: Show available mood categories if filtering fails
    if filtered.empty:
        available_moods = df["MoodCategory"].unique().tolist()
        st.warning(f"⚠️ No songs found for moods: {moods}")
        st.info(f"📋 Available mood categories in dataset: {available_moods}")
        return pd.DataFrame()
    
    # Filter by popularity >= 50
    if 'popularity' in filtered.columns:
        filtered = filtered[filtered['popularity'] >= 50]
    
    if filtered.empty:
        st.warning(f"⚠️ No songs found for moods: {moods} with popularity 50+")
        return pd.DataFrame()
    
    # Sort by popularity (descending) to prioritize more popular songs
    filtered = filtered.sort_values('popularity', ascending=False)
    
    recs = filtered.sample(n=min(top_n, len(filtered)), random_state=random.randint(0,1000))
    
    # Include popularity in the returned columns
    return recs[["track_id", "track_name", "artists", "track_genre", "MoodCategory", "valence", "energy", "popularity"]]

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(
    page_title="Mood-Based Music Recommender",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Mood-Based Music Recommender\nDetect emotions and get personalized song recommendations with Spotify playback!"
    }
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #1DB954 0%, #191414 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .emotion-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1DB954;
        margin: 1rem 0;
    }
    .song-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .song-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .stButton>button {
        border-radius: 8px;
        height: 3rem;
        font-weight: 600;
    }
    .spotify-button {
        background-color: #1DB954;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        text-decoration: none;
        display: inline-block;
        margin: 0.25rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🎧 Mood-Based Music Recommender</h1><p>Detect your facial emotion and get personalized song recommendations with Spotify playback</p></div>', unsafe_allow_html=True)

# Load model and data
with st.spinner("🔄 Loading AI models and music database..."):
    model = load_emotion_model()
    spotify_df = load_spotify_data()
    spotify_client = init_spotify_client()

# Initialize session state
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'emotion_detected' not in st.session_state:
    st.session_state.emotion_detected = None
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown("---")
    
    # Spotify Status
    st.subheader("🎵 Spotify Integration")
    if spotify_client:
        st.success("✅ Spotify API Connected")
    else:
        st.warning("⚠️ Spotify API Not Configured")
        with st.expander("📖 How to enable Spotify"):
            st.markdown("""
            **Steps to enable Spotify playback:**
            
            1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
            2. Create an app (free)
            3. Copy Client ID and Client Secret
            4. Set environment variables:
               - `SPOTIFY_CLIENT_ID`
               - `SPOTIFY_CLIENT_SECRET`
            
            Or use Streamlit secrets (.streamlit/secrets.toml):
            ```toml
            SPOTIFY_CLIENT_ID = "your_client_id"
            SPOTIFY_CLIENT_SECRET = "your_client_secret"
            ```
            """)
    
    st.markdown("---")
    st.subheader("📊 Model Configuration")
    confidence_threshold = st.slider(
        "Confidence Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.4,
        step=0.05,
        help="Minimum confidence required for emotion detection"
    )
    
    num_songs = st.slider(
        "Number of Recommendations",
        min_value=5,
        max_value=20,
        value=10,
        step=1,
        help="How many songs to recommend"
    )
    
    st.markdown("---")
    st.subheader("📈 Dataset Info")
    st.metric("Total Songs", len(spotify_df))
    st.metric("Emotion Classes", len(EMOTIONS))
    
    st.markdown("---")
    st.subheader("🎭 Available Emotions")
    for emotion in EMOTIONS:
        st.text(f"• {emotion.capitalize()}")
    
    st.markdown("---")
    st.info("💡 **Tip:** Ensure good lighting and face the camera directly for best results!")

# Main Layout - 3 column design
col1, col2, col3 = st.columns([2, 1, 2])

# LEFT COLUMN - Camera Feed
with col1:
    st.markdown("### 📸 Camera Feed")
    
    # Button controls
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
    with btn_col1:
        if st.button("▶️ Start Camera", use_container_width=True, type="primary"):
            st.session_state.camera_active = True
    with btn_col2:
        if st.button("⏹️ Stop Camera", use_container_width=True, type="secondary"):
            st.session_state.camera_active = False
    with btn_col3:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.emotion_detected = None
            st.session_state.recommendations = None
            st.rerun()
    
    st.markdown("---")
    camera_placeholder = st.empty()

# MIDDLE COLUMN - Emotion Detection Result
with col2:
    st.markdown("### 🧠 Detected Emotion")
    emotion_card = st.container()
    
    with emotion_card:
        if st.session_state.emotion_detected:
            emotion = st.session_state.emotion_detected
            st.markdown(f"""
                <div class="emotion-card">
                    <h1 style="text-align: center; margin: 0;">{emotion['emoji']}</h1>
                    <h2 style="text-align: center; color: #1DB954;">{emotion['label'].upper()}</h2>
                    <p style="text-align: center; font-size: 1.1rem;">
                        <strong>Confidence:</strong> {emotion['confidence']:.1%}
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("👈 Start camera and take a photo to detect your emotion")
    
    st.markdown("---")
    st.markdown("#### 📊 Quick Stats")
    stats_placeholder = st.empty()

# RIGHT COLUMN - Song Recommendations
with col3:
    st.markdown("### 🎵 Recommended Songs")
    reco_placeholder = st.empty()
    
    if st.session_state.recommendations is not None and not st.session_state.recommendations.empty:
        with reco_placeholder.container():
            st.success(f"✅ Found {len(st.session_state.recommendations)} songs for you!")
            
            for idx, row in enumerate(st.session_state.recommendations.itertuples(), 1):
                with st.expander(f"🎵 {idx}. {row.track_name}", expanded=(idx <= 3)):
                    st.markdown(f"""
                    **Artist:** {row.artists}  
                    **Genre:** {row.track_genre}  
                    **Mood:** {row.MoodCategory}  
                    **Popularity:** {row.popularity}/100 {'🔥' if row.popularity >= 70 else '⭐'}
                    
                    **Audio Features:**
                    - 💖 Valence: {row.valence:.2f}
                    - ⚡ Energy: {row.energy:.2f}
                    """)
                    
                    # Spotify Integration
                    col_a, col_b = st.columns(2)
                    
                    # Get track ID
                    track_id = row.track_id
                    spotify_url = f"https://open.spotify.com/track/{track_id}"
                    
                    with col_a:
                        st.link_button("🎧 Open in Spotify", spotify_url, use_container_width=True)
                    
                    with col_b:
                        # Try to get preview
                        if spotify_client:
                            preview_url, _ = get_track_preview_url(spotify_client, track_id)
                            if preview_url:
                                st.audio(preview_url, format='audio/mp3')
                            else:
                                st.caption("⚠️ No preview available")
                        else:
                            st.caption("⚠️ Configure Spotify API")
                    
                    st.markdown("---")
                    st.caption(f"Track ID: `{track_id}`")
    else:
        if st.session_state.emotion_detected:
            reco_placeholder.warning(f"⚠️ No songs found for emotion: {st.session_state.emotion_detected['label']}. This might be a mood mapping issue.")
        else:
            reco_placeholder.info("🎵 Your personalized playlist will appear here after emotion detection")

# Load Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# -----------------------------
# SNAPSHOT MODE - CAMERA INPUT
# -----------------------------
if st.session_state.camera_active:
    with camera_placeholder.container():
        st.info("📸 Take a photo to detect your emotion!")
        
        # Use Streamlit's camera_input for snapshot
        camera_photo = st.camera_input("Click to capture 📷")
        
        if camera_photo is not None:
            # Convert uploaded image to OpenCV format
            file_bytes = np.asarray(bytearray(camera_photo.read()), dtype=np.uint8)
            frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            
            if frame is None:
                st.error("❌ Failed to read image from camera.")
            else:
                # Process the image
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 5)
                
                if len(faces) > 0:
                    # Get the largest face
                    (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
                    pad = int(0.1 * w)
                    x1, y1 = max(0, x - pad), max(0, y - pad)
                    x2, y2 = min(frame.shape[1], x + w + pad), min(frame.shape[0], y + h + pad)
                    face_crop = frame[y1:y2, x1:x2]
                    
                    # Draw rectangle on frame
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    
                    # Predict emotion
                    with st.spinner("🧠 Analyzing your emotion..."):
                        pred = predict_emotion(model, face_crop)
                        final_emotion = pred["label"]
                        confidence = pred["confidence"]
                    
                    # Debug: Show prediction details
                    st.write(f"**Debug Info:**")
                    st.write(f"- Detected emotion: `{final_emotion}`")
                    st.write(f"- Confidence: `{confidence:.2%}`")
                    
                    # Display result with face detection
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption="✅ Face Detected", use_container_width=True)
                    
                    # Emoji mapping
                    emotion_emojis = {
                        'happy': '😊',
                        'sad': '😢',
                        'angry': '😠',
                        'surprise': '😮',
                        'neutral': '😐',
                        'fear': '😨',
                        'disgust': '🤢'
                    }
                    
                    # Store in session state
                    st.session_state.emotion_detected = {
                        'label': final_emotion,
                        'confidence': confidence,
                        'emoji': emotion_emojis.get(final_emotion, '😐')
                    }
                    
                    # Get song recommendations
                    recommendations = recommend_songs(spotify_df, final_emotion, top_n=num_songs)
                    st.session_state.recommendations = recommendations
                    
                    # Update stats
                    with stats_placeholder:
                        st.metric("Detection Status", "✅ Complete")
                        st.metric("Faces Found", len(faces))
                    
                    # Display recommendations in right column
                    if not recommendations.empty:
                        with reco_placeholder.container():
                            st.success(f"✅ Found {len(recommendations)} songs for you!")
                            
                            for idx, row in enumerate(recommendations.itertuples(), 1):
                                with st.expander(f"🎵 {idx}. {row.track_name}", expanded=(idx <= 3)):
                                    st.markdown(f"""
                                    **Artist:** {row.artists}  
                                    **Genre:** {row.track_genre}  
                                    **Mood:** {row.MoodCategory}  
                                    **Popularity:** {row.popularity}/100 {'🔥' if row.popularity >= 70 else '⭐'}
                                    
                                    **Audio Features:**
                                    - 💖 Valence: {row.valence:.2f}
                                    - ⚡ Energy: {row.energy:.2f}
                                    """)
                                    
                                    # Spotify Integration
                                    col_a, col_b = st.columns(2)
                                    
                                    # Get track ID
                                    track_id = row.track_id
                                    spotify_url = f"https://open.spotify.com/track/{track_id}"
                                    
                                    with col_a:
                                        st.link_button("🎧 Open in Spotify", spotify_url, use_container_width=True)
                                    
                                    with col_b:
                                        # Try to get preview
                                        if spotify_client:
                                            preview_url, _ = get_track_preview_url(spotify_client, track_id)
                                            if preview_url:
                                                st.audio(preview_url, format='audio/mp3')
                                            else:
                                                st.caption("⚠️ No preview available")
                                        else:
                                            st.caption("⚠️ Configure Spotify API")
                                    
                                    st.markdown("---")
                                    st.caption(f"Track ID: `{track_id}`")
                    else:
                        reco_placeholder.warning("⚠️ No songs found for this emotion. Try adjusting the confidence threshold.")
                        
                else:
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)
                    st.error("**NO FACE DETECTED** 😞")
                    st.warning("Please ensure your face is clearly visible and well-lit.")
else:
    with camera_placeholder.container():
        st.markdown("""
        <div style='text-align: center; padding: 3rem; background-color: #f0f2f6; border-radius: 10px;'>
            <h3>📷 Camera Ready</h3>
            <p>Click 'Start Camera' to begin emotion detection</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 1rem;'>
    <p style='color: #666;'>
        Made with ❤️ using Streamlit & Spotify API | 
        <a href='https://developer.spotify.com/documentation/web-api' target='_blank'>Spotify Web API Docs</a>
    </p>
</div>
""", unsafe_allow_html=True)
