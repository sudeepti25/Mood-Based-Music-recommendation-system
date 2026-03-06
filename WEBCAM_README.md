# Emotion Detection Webcam - Mood Prediction

This script uses your webcam to detect faces and predict mood categories in real-time using the Random Forest classifier trained in `p3.ipynb`.

## Features

- **Real-time face detection** using OpenCV Haar Cascades
- **Mood prediction** using the trained Random Forest model (`random_forest_mood_model.joblib`)
- **Optional emotion detection** using CNN model (`mood_model.h5`) if available
- **Live video display** with mood labels and confidence scores
- **Save snapshots** by pressing 's'

## How It Works

1. **Face Detection**: Uses OpenCV's Haar Cascade to detect faces in the webcam feed
2. **Feature Extraction**: 
   - If `mood_model.h5` exists: Uses CNN to detect emotion (Happy, Sad, Angry, etc.) and maps it to audio features (valence, energy, danceability, tempo, loudness)
   - Otherwise: Uses simplified face analysis to estimate features
3. **Mood Prediction**: Feeds the features into your trained Random Forest classifier to predict mood category
4. **Display**: Shows the detected emotion and predicted mood on the video feed

## Requirements

Install required packages:

```powershell
pip install opencv-python numpy joblib scikit-learn tensorflow keras
```

Or use the requirements file:

```powershell
pip install -r requirements.txt
```

## Usage

1. Make sure you've trained the Random Forest model first (run `p3.ipynb` cells)
2. Run the script:

```powershell
python emotion_detection_webcam.py
```

3. Controls:
   - Press **'q'** to quit
   - Press **'s'** to save the current frame

## Emotion to Audio Feature Mapping

The script maps detected emotions to audio features as follows:

| Emotion | Valence | Energy | Danceability | Tempo | Loudness |
|---------|---------|--------|--------------|-------|----------|
| Happy   | 0.8     | 0.75   | 0.7          | 120   | -5       |
| Sad     | 0.2     | 0.3    | 0.3          | 70    | -12      |
| Angry   | 0.3     | 0.85   | 0.6          | 140   | -4       |
| Fear    | 0.25    | 0.7    | 0.4          | 110   | -8       |
| Surprise| 0.6     | 0.75   | 0.65         | 115   | -6       |
| Disgust | 0.25    | 0.5    | 0.4          | 85    | -9       |
| Neutral | 0.5     | 0.5    | 0.5          | 100   | -8       |

## Output

The script will display:
- Green rectangle around detected faces
- Emotion label with confidence (if CNN model available)
- Predicted mood category
- Prediction confidence

## Notes

- The emotion-to-audio-feature mapping is a heuristic approximation. For better results, you could train a model to learn this mapping from actual facial expressions and corresponding music preferences.
- Make sure your webcam is not being used by another application
- Good lighting improves face detection accuracy

## Troubleshooting

**"Could not open webcam"**: 
- Check if your webcam is connected
- Try changing the camera index in `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)` or higher

**"mood_model.h5 not found"**:
- This is normal if you haven't trained the CNN emotion model
- The script will fall back to simplified feature extraction

**Low accuracy**:
- Ensure good lighting on your face
- Face the camera directly
- Train the Random Forest model on more diverse data
