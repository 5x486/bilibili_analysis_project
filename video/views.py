"""Bilibili Analysis Platform — All View Functions."""
import json
from collections import Counter

import pandas as pd
from django.contrib.auth.hashers import check_password, identify_hasher, make_password
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages

import util
from video.models import User, VideoData, UpData, DanmakuData, RankingData


# ── Password Helpers ──
# 以前 User.password 存的是明文，登录时直接拿明文比对。
# 这在作品集里是硬伤：任何人拿到数据库就能看到密码，而且泄露后无法补救。
# 现在统一用 Django 的密码哈希（PBKDF2），并保留对历史明文数据的兼容：
# 老用户第一次登录成功后，会自动把明文升级成哈希，不需要重置密码。

def _is_hashed(value):
    """判断库里的密码是不是 Django 哈希（pbkdf2_sha256$... 这类格式）。"""
    try:
        identify_hasher(value or "")
        return True
    except Exception:
        return False


def verify_password(raw_password, stored_password):
    """校验密码：哈希按 Django 规则校验，历史明文按等值比较。"""
    if not stored_password:
        return False
    if _is_hashed(stored_password):
        return check_password(raw_password or "", stored_password)
    return stored_password == (raw_password or "")


# ── Auth Views ──

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = User.objects.filter(username=username).first()
        if user and verify_password(password, user.password):
            # 历史明文数据：登录成功后顺手升级为哈希，用户无感知。
            if not _is_hashed(user.password):
                user.password = make_password(password)
                user.save(update_fields=['password'])
            request.session['username'] = username
            request.session['uid'] = user.id
            return redirect('/home/index/')
        messages.error(request, '用户名或密码错误')
        return HttpResponseRedirect('/home/login/')
    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            messages.error(request, '用户名和密码不能为空')
            return HttpResponseRedirect('/home/register/')
        if len(password) < 6:
            messages.error(request, '密码长度不能少于6位')
            return HttpResponseRedirect('/home/register/')
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户已存在')
            return HttpResponseRedirect('/home/register/')
        User.objects.create(username=username, password=make_password(password))
        messages.success(request, '注册成功，请登录')
        return HttpResponseRedirect('/home/login/')
    return render(request, 'register.html')


def logout(request):
    request.session.flush()
    return redirect('/home/login/')


# ── Dashboard ──

def index(request):
    """Main dashboard with overview stats and charts."""
    total_videos = VideoData.objects.count()

    total_views_val = 0
    total_likes = 0
    for v in VideoData.objects.all():
        total_views_val += (v.view_count or 0)
        total_likes += (v.like_count or 0)

    max_views_video = VideoData.objects.order_by('-view_count').first()

    top_videos = VideoData.objects.order_by('-view_count')[:10]
    chart_titles = [v.title[:15] + '...' if v.title and len(v.title) > 15 else (v.title or '') for v in top_videos]
    chart_views = [v.view_count or 0 for v in top_videos]

    # Partition distribution
    try:
        partition_data = util.query("SELECT * FROM part3 LIMIT 10")
        partition_names = [r[0] for r in partition_data]
        partition_counts = [r[1] for r in partition_data]
    except Exception:
        partition_names = []
        partition_counts = []

    # Top UP主
    try:
        top_ups = util.query("SELECT * FROM part4 LIMIT 5")
    except Exception:
        top_ups = []

    page = request.GET.get('page', 1)
    all_data = VideoData.objects.all().order_by('-id')
    paginator = Paginator(all_data, 10)
    page_obj = paginator.get_page(page)

    content = {
        'total_videos': total_videos,
        'total_views': total_views_val,
        'total_likes': total_likes,
        'max_views': max_views_video.view_count if max_views_video else 0,
        'chart_titles': json.dumps(chart_titles, ensure_ascii=False),
        'chart_views': json.dumps(chart_views),
        'partition_names': json.dumps(partition_names, ensure_ascii=False),
        'partition_counts': json.dumps(partition_counts),
        'top_ups': top_ups,
        'page_obj': page_obj,
    }
    return render(request, 'index.html', content)


# ── Video Analysis ──

def video_analysis(request):
    """Video analysis page."""
    keyword = request.GET.get('keyword', '')
    videos = []
    video_detail = None

    if keyword:
        videos = VideoData.objects.filter(title__icontains=keyword)[:50]

    video_id = request.GET.get('id')
    if video_id:
        try:
            video_detail = VideoData.objects.get(id=video_id)
        except VideoData.DoesNotExist:
            pass

    try:
        duration_data = util.query("SELECT * FROM part7")
        duration_names = [r[0] for r in duration_data]
        duration_counts = [r[1] for r in duration_data]
    except Exception:
        duration_names = []
        duration_counts = []

    content = {
        'keyword': keyword,
        'videos': videos,
        'video_detail': video_detail,
        'duration_names': json.dumps(duration_names, ensure_ascii=False),
        'duration_counts': json.dumps(duration_counts),
    }
    return render(request, 'video.html', content)


# ── UP主 Analysis ──

def up_analysis(request):
    """UP主 analysis page."""
    keyword = request.GET.get('keyword', '')
    up_list = []
    up_detail = None

    if keyword:
        up_list = UpData.objects.filter(name__icontains=keyword)[:20]

    up_id = request.GET.get('id')
    if up_id:
        try:
            up_detail = UpData.objects.get(id=up_id)
        except UpData.DoesNotExist:
            pass

    try:
        hour_data = util.query("SELECT * FROM part6")
        hour_labels = [f"{r[0]}点" for r in hour_data]
        hour_counts = [r[1] for r in hour_data]
    except Exception:
        hour_labels = []
        hour_counts = []

    content = {
        'keyword': keyword,
        'up_list': up_list,
        'up_detail': up_detail,
        'hour_labels': json.dumps(hour_labels, ensure_ascii=False),
        'hour_counts': json.dumps(hour_counts),
    }
    return render(request, 'up.html', content)


# ── Danmaku Analysis ──

def danmaku_analysis(request):
    """Danmaku analysis page."""
    import os

    # Auto-run NLP analysis if danmaku data exists but result CSV hasn't been generated
    nlp_csv = 'data/nlp_result.csv'
    if not os.path.exists(nlp_csv):
        danmaku_count = DanmakuData.objects.count()
        if danmaku_count > 0:
            try:
                from data.nlp import analyze_danmaku_sentiment
                analyze_danmaku_sentiment()
            except Exception as e:
                print(f"Auto NLP analysis failed: {e}")

    try:
        from data.word_cloud import get_word_frequencies
        word_data = get_word_frequencies(top_n=100)
    except Exception:
        word_data = []

    try:
        df = pd.read_csv(nlp_csv)
        positive = int((df['score'] > 0.5).sum())
        negative = int((df['score'] < 0.5).sum())
        neutral = int((df['score'] == 0.5).sum())
    except Exception:
        positive, negative, neutral = 0, 0, 0

    page = request.GET.get('page', 1)
    danmaku_list = DanmakuData.objects.all().order_by('-id')
    paginator = Paginator(danmaku_list, 20)
    page_obj = paginator.get_page(page)

    content = {
        'word_data': json.dumps(word_data, ensure_ascii=False),
        'positive': positive,
        'negative': negative,
        'neutral': neutral,
        'page_obj': page_obj,
    }
    return render(request, 'danmaku.html', content)


# ── Rankings ──

def ranking(request):
    """Ranking page."""
    list_type = request.GET.get('type', 'all')
    rankings = RankingData.objects.filter(list_type=list_type).order_by('rank')

    content = {
        'list_type': list_type,
        'rankings': rankings,
    }
    return render(request, 'ranking.html', content)


# ── AI Analysis ──

def ai_analysis(request):
    """AI analysis page with DeepSeek integration."""
    result = None
    analysis_type = None

    if request.method == 'POST':
        analysis_type = request.POST.get('analysis_type', 'video')

        if analysis_type == 'video':
            from ai.video_analyzer import analyze_video
            video_data = {
                'title': request.POST.get('title', ''),
                'partition': request.POST.get('partition', ''),
                'duration': int(request.POST.get('duration', 0)),
                'view_count': int(request.POST.get('view_count', 0)),
                'like_count': int(request.POST.get('like_count', 0)),
                'coin_count': int(request.POST.get('coin_count', 0)),
                'favorite_count': int(request.POST.get('favorite_count', 0)),
                'comment_count': int(request.POST.get('comment_count', 0)),
                'danmaku_count': int(request.POST.get('danmaku_count', 0)),
                'share_count': int(request.POST.get('share_count', 0)),
            }
            result = analyze_video(video_data)

        elif analysis_type == 'up':
            from ai.up_analyzer import analyze_up
            up_info = {
                'name': request.POST.get('up_name', ''),
                'follower_count': int(request.POST.get('follower_count', 0)),
                'video_count': int(request.POST.get('video_count', 0)),
                'total_views': int(request.POST.get('total_views', 0)),
                'total_likes': int(request.POST.get('total_likes', 0)),
                'level': int(request.POST.get('level', 0)),
            }
            video_stats = {
                'avg_views': int(request.POST.get('avg_views', 0)),
                'avg_likes': int(request.POST.get('avg_likes', 0)),
                'avg_interaction_rate': float(request.POST.get('avg_interaction_rate', 0)),
                'top_video_title': request.POST.get('top_video_title', ''),
                'best_hour': request.POST.get('best_hour', ''),
            }
            result = {'analysis': analyze_up(up_info, video_stats)}

        elif analysis_type == 'title':
            from ai.content_generator import generate_titles
            topic = request.POST.get('topic', '')
            result = {'analysis': generate_titles(topic)}

        elif analysis_type == 'tags':
            from ai.content_generator import generate_tags
            topic = request.POST.get('topic', '')
            result = {'analysis': generate_tags(topic)}

    content = {
        'result': result,
        'analysis_type': analysis_type,
    }
    return render(request, 'ai.html', content)


# ── ML Prediction ──

def predict(request):
    """ML prediction page."""
    pre_result = None
    input_data = None

    if request.method == 'POST':
        try:
            from ml.predict import predict_views
            input_data = {
                'duration': float(request.POST.get('duration', 0)),
                'favorite_count': float(request.POST.get('favorite_count', 0)),
                'coin_count': float(request.POST.get('coin_count', 0)),
                'comment_count': float(request.POST.get('comment_count', 0)),
                'danmaku_count': float(request.POST.get('danmaku_count', 0)),
                'share_count': float(request.POST.get('share_count', 0)),
                'interaction_rate': float(request.POST.get('interaction_rate', 0)),
                'publish_hour': int(request.POST.get('publish_hour', 12)),
            }
            pre_result = predict_views(input_data)
        except Exception as e:
            messages.error(request, f'预测失败: {e}')

    content = {
        'pre_result': pre_result,
        'input_data': input_data,
    }
    return render(request, 'predict.html', content)


# ── User Profile ──

def changeInfo(request):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/home/login/')

    try:
        userInfo = User.objects.get(id=uid)
    except User.DoesNotExist:
        return redirect('/home/login/')

    if request.method == 'POST':
        username = request.POST.get('username')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        avatar = request.FILES.get('avatar')

        if username and username != userInfo.username:
            if User.objects.filter(username=username).exclude(id=uid).exists():
                messages.error(request, '用户名已存在')
                return render(request, 'changeInfo.html', {'userInfo': userInfo})
            userInfo.username = username

        if new_password:
            if not old_password:
                messages.error(request, '修改密码需要输入旧密码')
                return render(request, 'changeInfo.html', {'userInfo': userInfo})
            if not verify_password(old_password, userInfo.password):
                messages.error(request, '旧密码不正确')
                return render(request, 'changeInfo.html', {'userInfo': userInfo})
            if new_password != confirm_password:
                messages.error(request, '两次密码不一致')
                return render(request, 'changeInfo.html', {'userInfo': userInfo})
            if len(new_password) < 6:
                messages.error(request, '密码长度不能少于6位')
                return render(request, 'changeInfo.html', {'userInfo': userInfo})
            userInfo.password = make_password(new_password)

        if avatar:
            userInfo.avatar = avatar

        userInfo.save()
        messages.success(request, '个人信息修改成功')
        return redirect('/home/changeInfo/')

    return render(request, 'changeInfo.html', {'userInfo': userInfo})
