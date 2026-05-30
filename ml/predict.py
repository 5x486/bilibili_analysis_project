"""Prediction interface using the best trained model."""
import joblib
import pandas as pd

FEATURE_NAMES = [
    'duration', 'favorite_count', 'coin_count',
    'comment_count', 'danmaku_count', 'share_count',
    'interaction_rate', 'publish_hour',
]


def predict_views(input_data):
    """Predict view count from video features. Returns int."""
    import os
    model_path = 'ml/XGBoost_model.joblib'
    if not os.path.exists(model_path):
        # Fallback: try any model file
        import glob
        models = glob.glob('ml/*_model.joblib')
        if not models:
            return 0
        model_path = models[0]

    model = joblib.load(model_path)
    scaler = joblib.load('ml/scaler.joblib')
    features = [input_data.get(k, 0) for k in FEATURE_NAMES]
    df = pd.DataFrame([features], columns=FEATURE_NAMES)
    scaled = scaler.transform(df)
    prediction = model.predict(scaled)
    return max(0, round(prediction[0]))


if __name__ == '__main__':
    sample = {
        'duration': 300, 'favorite_count': 5000, 'coin_count': 3000,
        'comment_count': 1200, 'danmaku_count': 800, 'share_count': 600,
        'interaction_rate': 0.15, 'publish_hour': 19,
    }
    print(f"Predicted views: {predict_views(sample):,}")
