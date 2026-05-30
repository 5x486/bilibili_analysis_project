"""Generate content suggestions (titles, tags, cover descriptions)."""
from ai.deepseek_client import chat


def generate_titles(topic, count=5):
    """Generate optimized video titles for a given topic."""
    prompt = f"""
你是一个B站标题优化专家。请为「{topic}」主题生成{count}个吸引人的视频标题。

要求：
- 结合B站风格，可适当使用网络流行语
- 长度控制在15-30字
- 考虑SEO和点击率
- 每个标题后面用括号标注适合的分区

请直接输出标题列表，每行一个。
"""
    return chat(prompt)


def generate_tags(topic, count=10):
    """Generate optimized tags for a video."""
    prompt = f"""
你是一个B站标签优化专家。请为「{topic}」主题生成{count}个高流量标签。

要求：
- 包含热门标签和长尾标签
- 按流量从高到低排列
- 适合B站搜索算法

请直接输出标签，用#开头，每行一个。
"""
    return chat(prompt)


def generate_cover_desc(video_title, style="吸引眼球"):
    """Generate cover image description for video."""
    prompt = f"""
你是一个视频封面设计师。请为标题为「{video_title}」的B站视频设计封面描述。

要求：
- 风格：{style}
- 描述封面视觉元素、配色、文字排版
- 50-100字
"""
    return chat(prompt)
