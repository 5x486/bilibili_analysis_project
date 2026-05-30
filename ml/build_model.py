"""Train prediction models: LinearRegression, RandomForest, XGBoost."""
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
from xgboost import XGBRegressor
from data.data_clean import load_video_data


def prepare_features(df):
    """Prepare feature columns from raw video data."""
    df = df.copy()
    if 'publish_time' in df.columns:
        df['publish_time'] = pd.to_datetime(df['publish_time'])
        df['publish_hour'] = df['publish_time'].dt.hour
    df['interaction'] = (
        df['like_count'] + df['coin_count'] + df['comment_count'] + df['danmaku_count']
    )
    df['interaction_rate'] = df['interaction'] / df['view_count'].replace(0, float('nan'))
    feature_cols = [
        'duration', 'favorite_count', 'coin_count',
        'comment_count', 'danmaku_count', 'share_count',
        'interaction_rate', 'publish_hour',
    ]
    df = df.dropna(subset=feature_cols + ['view_count'])
    df = df.replace([float('inf'), float('-inf')], float('nan')).dropna()
    return df[feature_cols], df['view_count']


def train_models():
    """Train three models and save the best one."""
    df = load_video_data()
    X, y = prepare_features(df)

    if len(X) < 10:
        print("Not enough data to train models (need >= 10 rows).")
        return

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    models = {
        'LinearRegression': LinearRegression(),
        'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
        'XGBoost': XGBRegressor(n_estimators=100, random_state=42),
    }
    best_model = None
    best_score = -float('inf')

    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        print(f"{name}: R²={r2:.3f}, MAE={mae:.0f}")
        if r2 > best_score:
            best_score = r2
            best_model = (name, model)

    if best_model:
        name, model = best_model
        joblib.dump(model, f'ml/{name}_model.joblib')
        joblib.dump(scaler, 'ml/scaler.joblib')
        print(f"\nBest model: {name} (R²={best_score:.3f})")


if __name__ == '__main__':
    train_models()
