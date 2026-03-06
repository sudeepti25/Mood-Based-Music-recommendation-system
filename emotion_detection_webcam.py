"""
Emotion Detection from Webcam using Random Forest Classifier
Detects facial emotions in real-time and predicts mood categories
"""

import cv2
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

# Load the trained Random Forest mood classifier
print("Loading Random Forest mood classifier...")
rf_data = joblib.load('random_forest_mood_model.joblib')
rf_model = rf_data['model']
label_encoder = rf_data['label_encoder']
feature_names = rf_data['features']
scaler = rf_data.get('scaler', None)  # Load scaler if available
print(f"Loaded model. Mood categories: {list(label_encoder.classes_)}")
print(f"Features used: {feature_names}")
if scaler:
    print("✅ Feature scaler loaded")

# Load face detection cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def extract_audio_features_from_face(face_roi):
    """
    Extract audio-like features from facial appearance
    Maps visual features to audio features (valence, energy, danceability, tempo, loudness)
    """
    # Convert to grayscale for analysis
    gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
    
    # Feature 1: Brightness (correlates with valence - brighter = more positive)
    brightness = np.mean(gray_face)
    valence = np.clip(0.3 + (brightness - 100) / 300, 0.0, 1.0)
    
    # Feature 2: Contrast/variance (correlates with energy - more variation = more energy)
    contrast = np.std(gray_face)
    energy = np.clip(0.3 + contrast / 100, 0.0, 1.0)
    
    # Feature 3: Edge density (correlates with danceability - more edges = more movement/dance)
    edges = cv2.Canny(gray_face, 50, 150)
    edge_density = np.count_nonzero(edges) / edges.size
    danceability = np.clip(edge_density * 2, 0.0, 1.0)
    
    # Feature 4: Tempo (based on energy level)
    tempo = 70 + (energy * 100)  # Range: 70-170 BPM
    
    # Feature 5: Loudness (based on brightness and contrast)
    loudness = -15 + (brightness / 25) + (contrast / 10)  # Range: approximately -15 to -3
    loudness = np.clip(loudness, -20, 0)
    
    features = [valence, energy, danceability, tempo, loudness]
    return features

def main():
    # Initialize webcam
    print("\nStarting webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    print("Webcam started successfully!")
    print("\nControls:")
    print("  - Press 'q' to quit")
    print("  - Press 's' to save current frame\n")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break
        
        frame_count += 1
        display_frame = frame.copy()
        
        # Detect faces
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
        
        for (x, y, w, h) in faces:
            # Extract face ROI
            face_roi = frame[y:y+h, x:x+w]
            
            # Extract audio features from facial appearance
            audio_features = extract_audio_features_from_face(face_roi)
            
            # Scale features if scaler is available
            features_array = np.array(audio_features).reshape(1, -1)
            if scaler:
                features_array = scaler.transform(features_array)
            
            # Predict mood category using Random Forest
            mood_pred = rf_model.predict(features_array)
            mood_proba = rf_model.predict_proba(features_array)
            mood_category = label_encoder.inverse_transform(mood_pred)[0]
            mood_confidence = np.max(mood_proba)
            
            # Draw rectangle around face
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Display mood prediction
            y_offset = y - 10
            text = f"Mood: {mood_category}"
            cv2.putText(display_frame, text, (x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            y_offset -= 25
            
            text = f"Confidence: {mood_confidence:.2f}"
            cv2.putText(display_frame, text, (x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_offset -= 25
            
            # Display feature values (for debugging)
            feature_text = f"V:{audio_features[0]:.2f} E:{audio_features[1]:.2f}"
            cv2.putText(display_frame, feature_text, (x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # Display instructions
        cv2.putText(display_frame, "Press 'q' to quit", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Show frame
        cv2.imshow('Emotion Detection - Mood Prediction', display_frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nQuitting...")
            break
        elif key == ord('s'):
            filename = f'emotion_capture_{frame_count}.jpg'
            cv2.imwrite(filename, display_frame)
            print(f"Saved frame to {filename}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("Webcam closed. Goodbye!")

if __name__ == "__main__":
    main()
