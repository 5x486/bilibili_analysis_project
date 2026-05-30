"""Analyze a single video's performance with AI."""
from ai.deepseek_client import chat


def analyze_video(video_data):
    """Generate AI analysis for a single video.

    video_data: dict with keys matching VideoData fields
    Returns: dict with 'analysis' (str) and 'metrics' (dict)
    """
    duration_sec = video_data.get('duration', 0)
    minutes = duration_sec // 60
    seconds = duration_sec % 60

    prompt = f"""
你是一个B站内容策略专家，请分析以下视频信息数据，并提供优化建议。

=== 视频基础信息 ===
- 标题：{video_data.get('title', '未知')}
- 分区：{video_data.get('partition', '未知')}
- 时长：{minutes}分{seconds}秒

=== 互动数据 ===
- 播放量：{video_data.get('view_count', 0):,}
- 点赞数：{video_data.get('like_count', 0):,}
- 投币数：{video_data.get('coin_count', 0):,}
- 收藏数：{video_data.get('favorite_count', 0):,}
- 评论数：{video_data.get('comment_count', 0):,}
- 弹幕数：{video_data.get('danmaku_count', 0):,}
- 分享数：{video_data.get('share_count', 0):,}

=== 关键指标 ===
- 点赞率：{video_data.get('like_count', 0) / max(video_data.get('view_count', 1), 1) * 100:.2f}%
- 投币率：{video_data.get('coin_count', 0) / max(video_data.get('view_count', 1), 1) * 100:.2f}%

请按以下结构返回分析：

=== 表现评估 ===
[分析该视频的各项指标表现如何]

=== 优化建议 ===
1. [内容方向调整建议]
2. [互动设计建议]
3. [标签/标题优化建议]
"""

    system = "你是一个专业的B站视频数据分析师，擅长从数据中发现优化机会。请用中文回复。"
    analysis = chat(prompt, system_prompt=system)

    return {
        "analysis": analysis,
        "metrics": {
            "like_rate": video_data.get('like_count', 0) / max(video_data.get('view_count', 1), 1) * 100,
            "coin_rate": video_data.get('coin_count', 0) / max(video_data.get('view_count', 1), 1) * 100,
            "duration_sec": duration_sec,
        }
    }
