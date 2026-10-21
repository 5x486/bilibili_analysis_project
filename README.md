# Bilibili 数据分析平台

一个基于 Django 的全栈 Web 应用，用于 B 站视频数据采集、多维统计分析和 AI 内容策略优化。

> ⚠️ **声明**：本代码仅供学习编程原理，严禁用于任何实际数据抓取或者商业用途。

## 数据现状与边界（先看这个）

当前库是 **2026-05-30 的一次采集快照**，不是 B 站全量，也不是长期监控：

| 项目 | 现状 |
|---|---|
| 样本量 | 65 个视频 / 58 位 UP 主 / 10,817 条弹幕 / 300 条榜单记录 |
| 累计播放 | 约 1.25 亿（124,993,759） |
| 样本偏差 | 关键词为「Python」，计算机技术分区占 45/65，结论不能外推到全站 |
| UP 主表 | `updata` 尚未灌入，UP 主分析页暂无明细；采集器已支持，运行 `fetch_and_save_up_videos` 即可补 |
| 投币字段 | 搜索接口返回的 `coin_count` 多为 0，投币相关分析暂不可用 |
| 模型 | `ml/` 下没有已训练模型文件，预测页在未训练时返回 0；先运行 `python -m ml.build_model` |
| 安全 | 用户密码使用 Django PBKDF2 哈希存储；历史明文数据会在首次登录时自动升级 |

## 功能模块

| 模块 | 说明 |
|------|------|
| 📊 **数据看板** | 总览统计：视频数、播放量、点赞数，Top10 柱状图，分区饼图，UP 主榜单 |
| 🎬 **视频分析** | 搜索视频，查看播放/点赞/投币/收藏/弹幕/分享数据，时长分布图 |
| 👤 **UP 主分析** | 搜索 UP 主，查看粉丝/关注/播放/点赞数据，发布时间分布图 |
| 💬 **弹幕分析** | Canvas 弹幕动画引擎、情感分析、词频统计、弹幕数据表格 |
| 🏆 **排行榜** | 全站排行 / 热门排行 / 每周排行，金银铜牌样式 |
| 🤖 **AI 分析** | 视频诊断、UP 主运营报告、标题生成、标签生成（DeepSeek） |
| 🔮 **ML 预测** | 输入视频特征，XGBoost 预测播放量 |

## 技术栈

| 层次 | 技术 |
|------|------|
| 后端框架 | Django 6.0 |
| 数据库 | MySQL（ORM + 原生 pymysql + SQLAlchemy） |
| 前端样式 | Tailwind CSS + 700 行自定义 CSS |
| 图表 | ECharts 5.5（柱状图/饼图/折线图） |
| 动画 | GSAP 3.12 + Particles.js |
| AI | DeepSeek API（OpenAI SDK，流式输出） |
| ML | scikit-learn + XGBoost（三模型对比取最优） |
| NLP | jieba 分词 + SnowNLP 情感分析 |
| 数据采集 | requests + B 站公开 API |

## 快速开始

### 环境要求

- Python 3.10+
- MySQL 5.7+

### 安装

```bash
git clone https://github.com/5x486/bilibili_analysis_project.git
cd bilibili_analysis_project

# 创建虚拟环境
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# 安装依赖
pip install django>=6.0,<6.1 pymysql pandas sqlalchemy \
            scikit-learn xgboost joblib jieba snownlp \
            openai requests pillow wordcloud

# 创建数据库
mysql -u root -p -e "CREATE DATABASE bili_analysis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 配置环境变量
export DB_HOST=localhost DB_NAME=bili_analysis DB_USER=root DB_PASSWORD=your_password
export DEEPSEEK_API_KEY=sk-your-key
export DJANGO_SECRET_KEY=your-secret-key

# 初始化
python manage.py makemigrations video
python manage.py migrate
```

### 采集数据（可选）

```bash
# 全量采集
python -c "from data.fetcher import collect_all; collect_all('Python', video_count=100, up_count=5)"

# 单独采集排行榜
python -c "from data.fetcher import fetch_and_save_ranking; fetch_and_save_ranking()"
```

### 运行分析

```bash
python -m data.data_analysis    # 10 维统计分析
python -m data.nlp               # NLP 情感分析
python -m ml.build_model         # ML 模型训练
python manage.py runserver       # 启动服务
```

打开 http://127.0.0.1:8000/ ，注册后即可使用。

## 项目结构

```
bilibili_analysis_project/
├── bilibili_analyses/           # Django 项目配置
├── video/                       # Django 主应用（models/views/urls）
├── data/                        # 数据管道
│   ├── fetcher.py               # B 站 API 采集（8 个接口）
│   ├── data_analysis.py         # 10 维统计分析
│   ├── data_clean.py            # 数据清洗
│   └── nlp.py                   # NLP 情感分析
├── ai/                          # AI 模块
│   ├── deepseek_client.py       # DeepSeek 流式客户端
│   ├── video_analyzer.py        # 视频诊断
│   ├── up_analyzer.py           # UP 主运营分析
│   └── content_generator.py     # 标题/标签生成
├── ml/                          # 机器学习
│   ├── build_model.py           # 训练（LinearRegression/RandomForest/XGBoost）
│   └── predict.py               # 播放量预测
├── templates/                   # 10 个页面模板
└── static/                      # CSS/JS 静态资源
    ├── css/custom.css           # 霓虹玻璃风格设计系统（653 行）
    ├── js/charts.js             # ECharts 图表工厂
    ├── js/danmaku.js            # Canvas 弹幕引擎
    └── js/main.js               # 粒子特效 + GSAP 动画
```

## 设计亮点

- **霓虹玻璃风格 UI**：暗色主题 `#0a0a1a`，B 站粉 `#FB7299` + 青色 `#00d4ff`，毛玻璃卡片
- **Canvas 弹幕引擎**：60fps 实时弹幕动画，随机霓虹色 + 发光效果
- **10 维统计分析**：预计算存入 MySQL，页面秒加载
- **AI 流式输出**：DeepSeek 四种分析模式，实时逐字显示
- **多模型自动选优**：三模型对比 R²，自动保存最优模型
- **B 站 API 全封装**：8 个公开接口，无需登录，自带限速和抖动

## 页面截图

10 个功能页面：登录 / 注册 / 数据看板 / 视频分析 / UP 主分析 / 弹幕分析 / 排行榜 / AI 分析 / ML 预测 / 个人中心
