"""Data cleaning utilities."""
import pandas as pd
from config import Config
from sqlalchemy import create_engine


def get_engine():
    return create_engine(
        f'mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@'
        f'{Config.DB_HOST}/{Config.DB_NAME}?charset=utf8mb4'
    )


def load_video_data():
    engine = get_engine()
    return pd.read_sql_table('videodata', engine)


def load_comment_data():
    engine = get_engine()
    return pd.read_sql_table('danmakudata', engine)


def clean_video_data(df):
    """Remove rows with missing critical fields, fill defaults."""
    df = df.dropna(subset=['bvid', 'title'])
    numeric_cols = ['view_count', 'like_count', 'coin_count', 'favorite_count',
                    'comment_count', 'danmaku_count', 'share_count']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(int)
    if 'duration' in df.columns:
        df['duration'] = df['duration'].fillna(0).astype(int)
    return df
