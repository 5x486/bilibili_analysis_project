# Bilibili Data Analysis Project — Design Specification

**Date:** 2026-05-30  
**Status:** Draft  
**Reference project:** `D:\python_study\pycharm_python\tiktok_analysis_project`

---

## 1. Overview

A comprehensive Bilibili (B站) data analysis platform built with Django + Tailwind CSS + ECharts. Designed to surpass the existing TikTok analysis project in every dimension — more data sources, richer analysis, modern UI, and upgraded AI/ML capabilities.

### 1.1 Project Goal

Build a data dashboard that can:
- Collect Bilibili video data via official APIs (keyword search, UP主 videos, rankings)
- Analyze video performance, danmaku (弹幕), UP主 growth, and trending content
- Provide AI-powered insights via DeepSeek API
- Predict video performance with machine learning models
- Present everything in a visually stunning neon-anime themed dashboard

### 1.2 Key Principles

- **Compliance first**: Use Bilibili's open APIs, no reverse-engineering, no cracking encryption
- **Better than TikTok project**: More modules, deeper analysis, modern UI, better code structure
- **Learning-oriented**: Keep Django architecture similar to TikTok project for comparison

---

## 2. Tech Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| Backend | Django 6.0 | Same as TikTok project, easy comparison |
| Database | MySQL | Same as TikTok project |
| Frontend CSS | Tailwind CSS 3.x | Modern, utility-first, highly customizable |
| Charts | ECharts 5.x | Best Chinese data visualization library |
| Animations | GSAP + Particles.js | Apple-smooth animations + neon particle effects |
| AI | DeepSeek API (openai-compatible) | Cost-effective, strong Chinese capabilities |
| ML | scikit-learn + XGBoost + joblib | Multi-model comparison |
| NLP | jieba + SnowNLP | Chinese word segmentation + sentiment analysis |
| Python | 3.10+ | Modern Python features |

---

## 3. Project Structure

```
bilibili_analysis_project/
├── manage.py
├── config.py                    # Database & API configuration
├── util.py                      # Database utility functions
├── requirements.txt
├── bilibili_analyses/           # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── video/                       # Main Django app
│   ├── models.py                # Data models (VideoData, UpData, DanmakuData, RankingData, User)
│   ├── views.py                 # View logic
│   ├── urls.py                  # URL routing
│   └── templates/               # HTML templates (8 pages)
├── data/                        # Data collection & processing
│   ├── fetcher.py               # Bilibili API data fetching
│   ├── data_clean.py            # Data cleaning
│   ├── data_analysis.py         # Statistical analysis → MySQL tables
│   ├── nlp.py                   # Sentiment analysis + word segmentation
│   └── word_cloud.py            # Word cloud generation
├── ai/                          # AI analysis module
│   ├── deepseek_client.py       # DeepSeek API wrapper
│   ├── video_analyzer.py        # Single video analysis
│   ├── up_analyzer.py           # UP主 operations report
│   └── content_generator.py     # Title/copy suggestions
├── ml/                          # Machine learning module
│   ├── build_model.py           # Model training (LR, RF, XGBoost)
│   └── predict.py               # Prediction interface
├── static/                      # Static assets
│   ├── css/                     # Tailwind CSS + custom neon theme
│   ├── js/                      # ECharts + GSAP + Particles.js + custom scripts
│   └── img/                     # Images, character silhouettes
└── media/                       # User uploads (avatars)
```

**Improvements over TikTok project:**
- Modular separation: `data/`, `ai/`, `ml/` each have clear responsibilities
- AI module independent with dedicated DeepSeek client
- Config externalized in `config.py`
- No sprawling spider files with hardcoded cookies

---

## 4. Data Models

### 4.1 VideoData (视频信息)

| Field | Type | Description |
|-------|------|-------------|
| avid | BigIntegerField | B站视频avid |
| bvid | CharField | B站视频bvid |
| title | TextField | 标题 |
| description | TextField | 视频描述 |
| duration | IntegerField | 时长(秒) |
| publish_time | DateTimeField | 发布时间 |
| partition | CharField | 分区 |
| tags | TextField | 标签(JSON) |
| view_count | BigIntegerField | 播放数 |
| like_count | BigIntegerField | 点赞数 |
| coin_count | BigIntegerField | 投币数 |
| favorite_count | BigIntegerField | 收藏数 |
| comment_count | BigIntegerField | 评论数 |
| danmaku_count | BigIntegerField | 弹幕数 |
| share_count | BigIntegerField | 分享数 |
| up_mid | BigIntegerField | UP主mid |
| cover_url | URLField | 视频封面URL |

### 4.2 UpData (UP主信息)

| Field | Type | Description |
|-------|------|-------------|
| mid | BigIntegerField | UP主mid (unique) |
| name | CharField | 昵称 |
| signature | TextField | 简介 |
| avatar | URLField | 头像URL |
| follower_count | BigIntegerField | 粉丝数 |
| following_count | BigIntegerField | 关注数 |
| video_count | IntegerField | 总视频数 |
| total_views | BigIntegerField | 总播放数 |
| total_likes | BigIntegerField | 总获赞数 |
| level | IntegerField | 等级 |
| official_verify | TextField | 认证信息 |

### 4.3 DanmakuData (弹幕数据)

| Field | Type | Description |
|-------|------|-------------|
| content | TextField | 弹幕内容 |
| send_time | DateTimeField | 发送时间 |
| video_time | FloatField | 视频时间点(秒) |
| dm_type | IntegerField | 弹幕类型(0-3) |
| color | IntegerField | 颜色 |
| font_size | FloatField | 字体大小 |
| avid | BigIntegerField | 所属视频avid |

### 4.4 RankingData (排行数据)

| Field | Type | Description |
|-------|------|-------------|
| avid | BigIntegerField | 视频avid |
| rank | IntegerField | 排名 |
| list_type | CharField | 榜单类型 |
| score | IntegerField | 综合得分 |
| date | DateField | 上榜日期 |

### 4.5 User (用户)

| Field | Type | Description |
|-------|------|-------------|
| username | CharField | 用户名 |
| password | CharField | 密码 |
| avatar | ImageField | 头像 |
| create_time | DateField | 创建时间 |

---

## 5. Data Collection Strategy

### 5.1 Bilibili Open APIs (no login required)

| API Endpoint | Purpose |
|-------------|---------|
| `api.bilibili.com/x/web-interface/search` | Keyword search videos |
| `api.bilibili.com/x/space/wbi/arc/search` | UP主 video list |
| `api.bilibili.com/x/web-interface/card` | Video basic info (views/likes etc.) |
| `api.bilibili.com/x/player/pagelist` | Video multi-part info |
| `api.bilibili.com/x/space/wbi/acc/info` | UP主 info |
| `api.bilibili.com/x/web-interface/ranking` | Rankings |
| `api.bilibili.com/x/v1/dm/list.so` | Danmaku data (XML) |
| `api.bilibili.com/x/web-interface/popular` | Popular videos |

### 5.2 Rate Limiting

- Max 5 requests/second to avoid rate limiting
- Use `time.sleep()` between batches (not random, predictable)
- No cookie forging or parameter cracking

---

## 6. Feature Modules

### 6.1 Module Comparison: TikTok vs Bilibili

| Module | TikTok Project | Bilibili Project | Upgrade |
|--------|---------------|------------------|---------|
| Data Collection | Douyin internal API reverse | Bilibili open API | Compliant, stable |
| Basic Analysis | 4 dimensions (part1-5) | 8-10 dimensions | 3x more |
| Danmaku Analysis | ❌ None | ✅ Sentiment + density + heatmap | **NEW** |
| UP主 Analysis | ❌ None | ✅ Growth + timing + competition | **NEW** |
| NLP | SnowNLP + word cloud | Upgraded sentiment + keyword extraction | Model upgrade |
| ML | Linear regression only | Multi-model comparison (LR + RF + XGBoost) | Scientific approach |
| AI | Qwen (single video) | DeepSeek (video + UP主 + content gen) | **3x features** |

### 6.2 Basic Analysis Dimensions

1. Play count distribution
2. Interaction rate leaderboard
3. Coin/favorite/like correlation
4. Best posting time analysis
5. Partition competition heatmap
6. Tag effectiveness analysis
7. Fan count distribution
8. Comment/share correlation
9. Duration vs. engagement analysis
10. View growth trend

### 6.3 Danmaku Analysis Dimensions

1. Danmaku density curve (video timeline hot spots)
2. Danmaku sentiment distribution (positive/neutral/negative)
3. High-frequency danmaku word cloud
4. Danmaku user activity levels
5. Danmaku peak moment extraction

### 6.4 UP主 Analysis Dimensions

1. Follower growth trend chart
2. Video performance comparison (all videos)
3. Partition competitiveness assessment
4. Post frequency vs. view count correlation
5. Best posting hour heatmap
6. Average engagement rate over time

### 6.5 AI Analysis (DeepSeek)

| Function | Input | Output |
|----------|-------|--------|
| Video Diagnosis | Video metrics (views, likes, coins, etc.) | Performance assessment + optimization suggestions |
| UP主 Report | UP主 aggregate data + all videos | Growth strategy + content direction + timing optimization |
| Content Generation | Video topic/partition/target audience | Title suggestions + cover descriptions + tag recommendations |

Model: `deepseek-chat` via `api.deepseek.com` (OpenAI-compatible SDK).

### 6.6 ML Prediction

| Model | Purpose |
|-------|---------|
| Linear Regression | Baseline |
| Random Forest | View count / engagement rate prediction |
| XGBoost | Higher accuracy prediction |

Train all three, compare R² scores, select best model for production predictions.

---

## 7. Frontend Design

### 7.1 Visual Style

**Theme:** Neon Anime × Bilibili Style (霓虹二次元 × B站风)

| Element | Specification |
|---------|--------------|
| Background | Dark (#0a0a1a) with grid pattern + floating particles |
| Primary | Bilibili Pink (#FB7299) neon glow |
| Accent | Cyan (#00d4ff) neon |
| Cards | Glassmorphism + pink neon border + breathing glow |
| Icons | Custom anime-style SVG icons |
| Typography | Rounded Chinese font + monospace numbers |
| Decorations | 22/33娘 silhouettes + particle field |

### 7.2 Animations (Full mode)

| Trigger | Animation |
|---------|-----------|
| Page load | Bilibili girl running animation + neon progress bar |
| Card entry | Staggered fade-up with elastic ease-out (GSAP) |
| Button hover | Neon glow spread + micro scale |
| Chart render | ECharts data fade-in, bar wave rise |
| Danmaku page | Real danmaku scrolling with gradient neon colors |
| Rankings | Top 3 special: gold/silver/bronze glow + particle rise |
| AI output | Typewriter effect, cursor blink |
| Page transition | Smooth slide + pink light sweep |
| Background | Continuous pink/cyan particle float, mouse-attracted |

### 7.3 Pages (8 total)

| Page | Route | Content |
|------|-------|---------|
| Login | `/home/login/` | Card-style login with neon accents |
| Register | `/home/register/` | Registration with anime decorations |
| Dashboard | `/home/index/` | Overview: total videos, views, TOP5 UP主, collection status |
| Video Analysis | `/home/video/` | Search → data table → detail radar chart |
| UP主 Analysis | `/home/up/` | UP主 search → growth curve, video comparison, timing heatmap |
| Danmaku Analysis | `/home/danmaku/` | Video select → density curve, sentiment pie, word cloud |
| Rankings | `/home/ranking/` | Tab switch (popular/weekly/partition) → table + trend |
| AI Analysis | `/home/ai/` | Input data → DeepSeek report / title / copy generation |
| Prediction | `/home/predict/` | Input params → predicted views, engagement rate |
| Profile | `/home/changeInfo/` | User profile editing |

### 7.4 Sidebar Navigation

```
🎀 BiliAnalytics
─────────────────
📊 数据概览
📹 视频分析
👤 UP主分析
💬 弹幕分析
🏆 排行榜
🤖 AI分析
🔮 预测模型
─────────────────
⚙ 个人设置
🚪 退出登录
```

### 7.5 Tech Implementation

| Layer | Tech |
|-------|------|
| CSS Framework | Tailwind CSS + custom neon theme |
| Charts | ECharts (dark + neon color theme) |
| Animation Engine | GSAP (Apple-smooth) + Particles.js (background) |
| Danmaku Sim | Custom canvas engine (gradient neon colors) |
| Icons | Custom SVG + anime-style icon set |

---

## 8. Design Quality Standards

Active use of installed frontend skills during implementation:
- `design-taste-frontend` — Anti-generic design direction
- `high-end-visual-design` — Premium fonts, spacing, shadows, animations
- `impeccable` — Code/UI quality refinement
- `impeccable@animate` — Animation polish

---

## 9. Self-Review Checklist

- [x] No placeholder/TODO sections
- [x] Architecture matches feature descriptions
- [x] Scope is focused — single deployable project
- [x] No ambiguous requirements
- [x] All 7 modules have clear scope
- [x] Frontend style defined with concrete specifications
- [x] Data models cover all analysis dimensions
- [x] API endpoints identified
