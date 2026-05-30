"""Generate AI-powered UP主 operations report."""
from ai.deepseek_client import chat


def analyze_up(up_info, video_stats):
    """Generate a comprehensive UP主 analysis report."""
    prompt = f"""
你是一个B站UP主运营顾问，请根据以下数据分析该UP主的运营状况并给出建议。

=== UP主信息 ===
- 昵称：{up_info.get('name', '未知')}
- 粉丝数：{up_info.get('follower_count', 0):,}
- 总视频数：{up_info.get('video_count', 0)}
- 总播放量：{up_info.get('total_views', 0):,}
- 总获赞数：{up_info.get('total_likes', 0):,}
- 等级：Lv{up_info.get('level', 0)}

=== 视频统计 ===
- 平均播放量：{video_stats.get('avg_views', 0):,.0f}
- 平均点赞数：{video_stats.get('avg_likes', 0):,.0f}
- 平均互动率：{video_stats.get('avg_interaction_rate', 0):.2%}
- 最高播放视频：{video_stats.get('top_video_title', '未知')}
- 最佳发布时间段：{video_stats.get('best_hour', '未知')}点

请按以下结构返回报告：

=== UP主现状评估 ===
[粉丝规模、内容影响力、增长潜力评估]

=== 内容策略建议 ===
1. [内容方向建议]
2. [发布频率和时机建议]
3. [粉丝互动策略]
4. [差异化竞争方向]
"""

    system = "你是一个专业的B站UP主运营顾问，擅长内容策略和增长分析。请用中文回复。"
    return chat(prompt, system_prompt=system)
