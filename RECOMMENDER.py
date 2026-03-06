import pandas as pd
import random

# Load your Spotify dataset once
def load_spotify_data(path="dataset_with_moods_full.csv"):
    df = pd.read_csv(path)
    df = df.dropna(subset=["MoodCategory", "track_name", "artists"])
    return df

# Map emotion → MoodCategory → recommended tracks
def recommend_songs(df, emotion_label, top_n=10):
    emotion_to_moodcat = {
        'happy': ['Happy / Energetic', 'Positive / Excited'],
        'sad': ['Sad / Negative', 'Low Energy / Calm'],
        'angry': ['Intense / Aggressive', 'Energetic / Tense'],
        'fear': ['Tense / Dark', 'Sad / Negative'],
        'disgust': ['Intense / Aggressive'],
        'surprise': ['Positive / Excited'],
        'neutral': ['Mixed / Uncategorized', 'Low Energy / Calm']
    }

    moods = emotion_to_moodcat.get(emotion_label.lower(), [])
    if not moods:
        return pd.DataFrame()

    # Filter by matching MoodCategory
    filtered = df[df["MoodCategory"].isin(moods)]
    if filtered.empty:
        return pd.DataFrame()

    # Sample random top_n
    recs = filtered.sample(n=min(top_n, len(filtered)), random_state=random.randint(0,1000))
    return recs[["track_name", "artists", "track_genre", "MoodCategory", "valence", "energy"]]