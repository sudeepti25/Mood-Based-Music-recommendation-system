"""
Quick test script to verify mood categories in dataset
Run this to ensure your dataset has all the required mood categories
"""

import pandas as pd

# Load the dataset
DATA_PATH = r"C:\Users\dyash\OneDrive\Desktop\Mood-Based-Music-recommendation-system\dataset_with_moods_full.csv"
df = pd.read_csv(DATA_PATH)

# Check what mood categories exist
print("=" * 60)
print("MOOD CATEGORIES IN DATASET:")
print("=" * 60)
mood_counts = df['MoodCategory'].value_counts()
print(mood_counts)
print()

# Check what the emotion mapping expects
print("=" * 60)
print("EXPECTED MOOD CATEGORIES FROM EMOTION MAPPING:")
print("=" * 60)

emotion_to_moodcat = {
    'happy': ['Happy / Energetic (Pleasant)', 'Happy / Energetic (High Beat Party)', 'Uplifting / Positive', 'High Energy / Excited'],
    'sad': ['Sad / Negative', 'Low Energy / Calm'],
    'angry': ['High Energy / Excited', 'Happy / Energetic (High Beat Party)'],
    'surprise': ['High Energy / Excited', 'Uplifting / Positive'],
    'neutral': ['Mixed / Uncategorized', 'Balanced / Neutral', 'Low Energy / Calm']
}

all_expected_moods = set()
for emotion, moods in emotion_to_moodcat.items():
    for mood in moods:
        all_expected_moods.add(mood)

print("Expected moods:")
for mood in sorted(all_expected_moods):
    count = len(df[df['MoodCategory'] == mood])
    if count > 0:
        print(f"  ✅ {mood}: {count} songs")
    else:
        print(f"  ❌ {mood}: NOT FOUND IN DATASET!")

print()
print("=" * 60)
print("TESTING EACH EMOTION:")
print("=" * 60)

for emotion, moods in emotion_to_moodcat.items():
    filtered = df[df["MoodCategory"].isin(moods)]
    print(f"{emotion.upper()}: {len(filtered)} songs available")
    if len(filtered) == 0:
        print(f"  ⚠️ WARNING: No songs for {emotion}!")
        print(f"  Looking for moods: {moods}")

print()
print("✅ Test complete!")
