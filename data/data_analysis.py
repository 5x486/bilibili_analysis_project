"""Data analysis functions. Each writes results to a database table."""
import pandas as pd
from config import Config
from sqlalchemy import create_engine
from data.data_clean import load_video_data


def get_engine():
    return create_engine(
        f'mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@'
        f'{Config.DB_HOST}/{Config.DB_NAME}?charset=utf8mb4'
    )


def run_all_analyses():
    """Run all 10 analysis functions."""
    try: part1()
    except Exception as e: print(f"part1 error: {e}")
    try: part2()
    except Exception as e: print(f"part2 error: {e}")
    try: part3()
    except Exception as e: print(f"part3 error: {e}")
    try: part4()
    except Exception as e: print(f"part4 error: {e}")
    try: part5()
    except Exception as e: print(f"part5 error: {e}")
    try: part6()
    except Exception as e: print(f"part6 error: {e}")
    try: part7()
    except Exception as e: print(f"part7 error: {e}")
    try: part8()
    except Exception as e: print(f"part8 error: {e}")
    try: part9()
    except Exception as e: print(f"part9 error: {e}")
    try: part10()
    except Exception as e: print(f"part10 error: {e}")


def part1():
    """UP主播放量排行"""
    engine = get_engine()
    df = load_video_data()
    result = df.groupby('up_name').agg(
        total_views=('view_count', 'sum'),
        video_count=('bvid', 'count'),
        avg_views=('view_count', 'mean'),
    ).sort_values('total_views', ascending=False).head(20).reset_index()
    result.columns = ['up_name', 'total_views', 'video_count', 'avg_views']
    result.to_sql('part1', engine, if_exists='replace', index=False)


def part2():
    """点赞投币收藏关联（TOP20视频）"""
    engine = get_engine()
    df = load_video_data()
    result = df[['title', 'like_count', 'coin_count', 'favorite_count', 'view_count']] \
        .sort_values('like_count', ascending=False).head(20)
    result['coin_rate'] = result['coin_count'] / result['view_count'].replace(0, 1)
    result['like_rate'] = result['like_count'] / result['view_count'].replace(0, 1)
    result.to_sql('part2', engine, if_exists='replace', index=False)


def part3():
    """分区分布"""
    engine = get_engine()
    df = load_video_data()
    result = df['partition'].value_counts().reset_index()
    result.columns = ['partition', 'count']
    result.to_sql('part3', engine, if_exists='replace', index=False)


def part4():
    """UP主粉丝数排行"""
    engine = get_engine()
    up_df = pd.read_sql_table('updata', engine)
    result = up_df[['name', 'follower_count', 'video_count', 'total_views']] \
        .sort_values('follower_count', ascending=False).head(20)
    result.to_sql('part4', engine, if_exists='replace', index=False)


def part5():
    """评论与弹幕关联"""
    engine = get_engine()
    df = load_video_data()
    result = df[['title', 'comment_count', 'danmaku_count', 'share_count']] \
        .sort_values('comment_count', ascending=False).head(20)
    result.to_sql('part5', engine, if_exists='replace', index=False)


def part6():
    """发布时间分布（按小时）"""
    engine = get_engine()
    df = load_video_data()
    if 'publish_time' in df.columns:
        df['publish_hour'] = pd.to_datetime(df['publish_time']).dt.hour
        result = df['publish_hour'].value_counts().sort_index().reset_index()
        result.columns = ['hour', 'count']
        result.to_sql('part6', engine, if_exists='replace', index=False)


def part7():
    """视频时长分布"""
    engine = get_engine()
    df = load_video_data()
    bins = [0, 60, 180, 300, 600, 1800, float('inf')]
    labels = ['<1分钟', '1-3分钟', '3-5分钟', '5-10分钟', '10-30分钟', '>30分钟']
    df['duration_range'] = pd.cut(df['duration'], bins=bins, labels=labels)
    result = df['duration_range'].value_counts().sort_index().reset_index()
    result.columns = ['duration_range', 'count']
    result.to_sql('part7', engine, if_exists='replace', index=False)


def part8():
    """互动率分析"""
    engine = get_engine()
    df = load_video_data()
    df['interaction'] = (
        df['like_count'] + df['coin_count'] + df['comment_count'] + df['danmaku_count']
    )
    df['interaction_rate'] = df['interaction'] / df['view_count'].replace(0, float('nan'))
    result = df[['title', 'view_count', 'interaction', 'interaction_rate']] \
        .sort_values('interaction_rate', ascending=False).head(20)
    result.to_sql('part8', engine, if_exists='replace', index=False)


def part9():
    """弹幕密度排行"""
    engine = get_engine()
    df = load_video_data()
    df['danmaku_rate'] = df['danmaku_count'] / df['view_count'].replace(0, float('nan'))
    result = df[['title', 'danmaku_count', 'view_count', 'danmaku_rate']] \
        .sort_values('danmaku_rate', ascending=False).head(20)
    result.to_sql('part9', engine, if_exists='replace', index=False)


def part10():
    """日均播放趋势"""
    engine = get_engine()
    df = load_video_data()
    if 'publish_time' in df.columns:
        df['publish_date'] = pd.to_datetime(df['publish_time']).dt.date
        result = df.groupby('publish_date').agg(
            video_count=('bvid', 'count'),
            total_views=('view_count', 'sum'),
            avg_views=('view_count', 'mean'),
        ).reset_index()
        result.columns = ['publish_date', 'video_count', 'total_views', 'avg_views']
        result.to_sql('part10', engine, if_exists='replace', index=False)


if __name__ == '__main__':
    run_all_analyses()
