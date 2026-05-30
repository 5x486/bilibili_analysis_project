"""
Bilibili open API data fetcher.
No login required. Rate limited to 5 req/s max.
"""
import os
import sys
import random

import django

# 配置 Django 环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bilibili_analyses.settings')
django.setup()

import time
import requests
from datetime import datetime


class BiliFetcher:
    """Client for Bilibili's public APIs."""

    BASE = "https://api.bilibili.com"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/",
    }

    def __init__(self, rate_limit=0.3):
        self._last_request = 0
        self._rate_limit = rate_limit

    def _get(self, endpoint, params=None):
        """Rate-limited GET request."""
        elapsed = time.time() - self._last_request
        if elapsed < self._rate_limit:
            time.sleep(self._rate_limit - elapsed)
        time.sleep(random.uniform(0.5, 1.5))
        url = f"{self.BASE}{endpoint}"
        resp = requests.get(url, headers=self.HEADERS, params=params, timeout=15)
        self._last_request = time.time()

        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            raise Exception(f"API error: {data.get('message', 'unknown')}")
        return data.get("data", {})

    def search_videos(self, keyword, page=1, page_size=20):
        """Search videos by keyword."""
        return self._get("/x/web-interface/search/type", {
            "search_type": "video", "keyword": keyword,
            "page": page, "page_size": page_size,
        })

    def get_video_info(self, bvid=None, avid=None):
        """Get video basic info by bvid or avid."""
        params = {}
        if bvid: params["bvid"] = bvid
        elif avid: params["aid"] = avid
        return self._get("/x/web-interface/view", params)

    def get_video_detail(self, bvid):
        """Get video card detail."""
        return self._get("/x/web-interface/card", {"bvid": bvid})

    def get_up_videos(self, mid, page=1, page_size=30):
        """Get UP主's video list."""
        return self._get("/x/space/wbi/arc/search", {
            "mid": mid, "ps": page_size, "pn": page, "order": "pubdate",
        })

    def get_up_info(self, mid):
        """Get UP主 profile info."""
        return self._get("/x/space/wbi/acc/info", {"mid": mid})

    def get_ranking(self, rid=0, rtype="all"):
        """Get ranking videos."""
        return self._get("/x/web-interface/ranking/v2", {"rid": rid, "type": rtype})

    def get_popular(self, pn=1, ps=20):
        """Get popular videos."""
        return self._get("/x/web-interface/popular", {"pn": pn, "ps": ps})

    def get_danmaku_xml(self, cid):
        """Get danmaku XML for a video cid."""
        url = f"https://api.bilibili.com/x/v1/dm/list.so?oid={cid}"
        resp = requests.get(url, headers=self.HEADERS, timeout=10)
        resp.raise_for_status()
        resp.encoding = 'utf-8'  # Bilibili returns UTF-8, but header doesn't specify charset
        return resp.text


def parse_danmaku_xml(xml_text):
    """Parse Bilibili danmaku XML into list of dicts."""
    import re
    danmaku_list = []
    pattern = re.compile(r'<d p="([^"]*)">(.*?)</d>')
    for match in pattern.finditer(xml_text):
        attrs = match.group(1).split(",")
        content = match.group(2)
        if len(attrs) >= 4:
            danmaku_list.append({
                "video_time": float(attrs[0]),
                "dm_type": int(attrs[1]),
                "font_size": float(attrs[2]),
                "color": int(attrs[3]),
                "send_time": datetime.fromtimestamp(int(attrs[4])),
                "content": content,
            })
    return danmaku_list


def parse_search_result(result):
    """Extract video list from search API response."""
    videos = []
    for item in result.get("result", []):
        videos.append({
            "avid": item.get("aid"),
            "bvid": item.get("bvid"),
            "title": item.get("title", "").replace('<em class="keyword">', '').replace('</em>', ''),
            "description": item.get("description", ""),
            "duration": parse_duration(item.get("duration", "0:00")),
            "publish_time": datetime.fromtimestamp(item.get("pubdate", 0)),
            "partition": item.get("typename", ""),
            "tags": item.get("tag", ""),
            "view_count": item.get("play", 0),
            "like_count": item.get("like", 0) if isinstance(item.get("like"), int) else 0,
            "coin_count": item.get("coin", 0) if isinstance(item.get("coin"), int) else 0,
            "favorite_count": item.get("favorites", 0) if isinstance(item.get("favorites"), int) else 0,
            "comment_count": item.get("review", 0),
            "danmaku_count": item.get("video_review", 0),
            "share_count": 0,
            "up_mid": item.get("mid", 0),
            "up_name": item.get("author", ""),
            "cover_url": item.get("pic", ""),
        })
    return videos


def parse_duration(dur_str):
    """Convert 'MM:SS' to total seconds."""
    parts = dur_str.split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0


def fetch_and_save_search(keyword, count=100):
    """Search videos and save to database."""
    from video.models import VideoData
    fetcher = BiliFetcher()
    saved = 0
    page = 1
    while saved < count:
        try:
            result = fetcher.search_videos(keyword, page=page, page_size=20)
            videos = parse_search_result(result)
            if not videos:
                break
            for v in videos:
                if not VideoData.objects.filter(bvid=v["bvid"]).exists():
                    VideoData.objects.create(**v)
                    saved += 1
                if saved >= count:
                    break
            page += 1
        except Exception as e:
            print(f"Fetch error: {e}")
            break
    return saved


def fetch_and_save_up_videos(mid, count=50):
    """Fetch a UP主's videos and save."""
    from video.models import VideoData, UpData
    fetcher = BiliFetcher()
    saved = 0
    page = 1

    # Fetch UP主 info
    try:
        up_info = fetcher.get_up_info(mid)
        UpData.objects.update_or_create(
            mid=mid,
            defaults={
                "name": up_info.get("name", ""),
                "signature": up_info.get("sign", ""),
                "avatar": up_info.get("face", ""),
                "follower_count": up_info.get("follower", 0) if "follower" in up_info else 0,
                "following_count": up_info.get("following", 0) if "following" in up_info else 0,
                "video_count": up_info.get("video", 0) if "video" in up_info else 0,
                "total_views": up_info.get("total_play", 0) if "total_play" in up_info else 0,
                "total_likes": up_info.get("total_like", 0) if "total_like" in up_info else 0,
                "level": up_info.get("level", 0),
                "official_verify": up_info.get("official", {}).get("title", ""),
            }
        )
    except Exception as e:
        print(f"UP主 info fetch error: {e}")

    # Fetch videos
    while saved < count:
        try:
            result = fetcher.get_up_videos(mid, page=page)
            vlist = result.get("list", {}).get("vlist", [])
            if not vlist:
                break
            for v in vlist:
                bvid = v.get("bvid", "")
                if not VideoData.objects.filter(bvid=bvid).exists():
                    try:
                        detail = fetcher.get_video_info(bvid=bvid)
                        stat = detail.get("stat", {})
                        VideoData.objects.create(
                            avid=v.get("aid", 0), bvid=bvid,
                            title=v.get("title", ""),
                            description=v.get("description", ""),
                            duration=parse_duration(v.get("length", "0:00")),
                            publish_time=datetime.fromtimestamp(v.get("created", 0)),
                            view_count=stat.get("view", 0),
                            like_count=stat.get("like", 0),
                            coin_count=stat.get("coin", 0),
                            favorite_count=stat.get("favorite", 0),
                            comment_count=stat.get("reply", 0),
                            danmaku_count=stat.get("danmaku", 0),
                            share_count=stat.get("share", 0),
                            up_mid=mid, up_name=v.get("author", ""),
                            cover_url=v.get("pic", ""),
                        )
                        saved += 1
                    except Exception as e:
                        print(f"Video detail fetch error: {e}")
                if saved >= count:
                    break
            page += 1
        except Exception as e:
            print(f"UP video fetch error: {e}")
            break
    return saved


def fetch_and_save_danmaku(bvid=None, avid=None):
    """Fetch danmaku XML for a video and save to database.

    Needs the video's cid (obtained via get_video_info).
    """
    from video.models import DanmakuData
    fetcher = BiliFetcher()

    # Get video info to obtain cid
    try:
        info = fetcher.get_video_info(bvid=bvid, avid=avid)
    except Exception as e:
        print(f"获取视频信息失败: {e}")
        return 0

    cid = info.get("cid", 0)
    if not cid:
        print("未找到视频 cid，无法获取弹幕")
        return 0

    real_avid = info.get("aid", avid or 0)

    # Fetch and parse danmaku
    try:
        xml_text = fetcher.get_danmaku_xml(cid)
    except Exception as e:
        print(f"获取弹幕 XML 失败: {e}")
        return 0

    danmaku_list = parse_danmaku_xml(xml_text)
    saved = 0
    for dm in danmaku_list:
        if not DanmakuData.objects.filter(
            content=dm["content"],
            video_time=dm["video_time"],
            avid=real_avid,
        ).exists():
            DanmakuData.objects.create(**dm, avid=real_avid)
            saved += 1

    print(f"视频 {bvid or avid} 共采集 {saved} 条弹幕")
    return saved


def fetch_and_save_danmaku_batch(limit=10):
    """Fetch danmaku for videos that don't have danmaku data yet."""
    from video.models import VideoData
    videos = VideoData.objects.exclude(
        avid__isnull=True
    ).exclude(avid=0).order_by("-view_count")

    saved_total = 0
    for v in videos[:limit]:
        print(f"正在采集 {v.bvid} ({v.title[:30]}...) 的弹幕...")
        saved = fetch_and_save_danmaku(bvid=v.bvid)
        saved_total += saved

    print(f"\n批量弹幕采集完成，共 {saved_total} 条")
    return saved_total


def fetch_and_save_ranking(rid=0, rtype="all"):
    """Fetch ranking list and save to database."""
    from video.models import RankingData
    from datetime import date
    fetcher = BiliFetcher()

    try:
        ranking_data = fetcher.get_ranking(rid=rid, rtype=rtype)
    except Exception as e:
        print(f"获取排行榜失败: {e}")
        return 0

    saved = 0
    today = date.today()
    for item in ranking_data.get("list", []):
        avid = item.get("aid", 0)
        rank = item.get("rank", 0)
        score = item.get("score", 0)
        if not RankingData.objects.filter(avid=avid, date=today, list_type=rtype).exists():
            RankingData.objects.create(
                avid=avid, rank=rank,
                list_type=rtype, score=score,
                date=today,
            )
            saved += 1

    print(f"排行榜 [{rtype}] 共采集 {saved} 条")
    return saved


def fetch_and_save_popular(count=50):
    """Fetch popular videos page by page and save to database."""
    from video.models import VideoData
    fetcher = BiliFetcher()
    saved = 0
    pn = 1
    while saved < count:
        try:
            data = fetcher.get_popular(pn=pn, ps=20)
            videos = data.get("list", [])
            if not videos:
                break
            for item in videos:
                bvid = item.get("bvid", "")
                if not bvid:
                    continue
                if not VideoData.objects.filter(bvid=bvid).exists():
                    stat = item.get("stat", {})
                    VideoData.objects.create(
                        avid=item.get("aid", 0), bvid=bvid,
                        title=item.get("title", ""),
                        description=item.get("desc", ""),
                        duration=item.get("duration", 0),
                        publish_time=item.get("pubdate", 0),
                        partition=item.get("tname", ""),
                        view_count=stat.get("view", 0),
                        like_count=stat.get("like", 0),
                        coin_count=stat.get("coin", 0),
                        favorite_count=stat.get("favorite", 0),
                        comment_count=stat.get("reply", 0),
                        danmaku_count=stat.get("danmaku", 0),
                        share_count=stat.get("share", 0),
                        up_mid=item.get("owner", {}).get("mid", 0),
                        up_name=item.get("owner", {}).get("name", ""),
                        cover_url=item.get("pic", ""),
                    )
                    saved += 1
                if saved >= count:
                    break
            pn += 1
        except Exception as e:
            print(f"热门视频采集失败: {e}")
            break

    print(f"热门视频共采集 {saved} 条")
    return saved


def fetch_and_save_popular_ranking(count=100):
    """Fetch popular videos and save as RankingData with list_type='popular'."""
    from video.models import RankingData
    from datetime import date
    fetcher = BiliFetcher()
    saved = 0
    pn = 1
    today = date.today()

    while saved < count:
        try:
            data = fetcher.get_popular(pn=pn, ps=20)
            videos = data.get("list", [])
            if not videos:
                break
            for item in videos:
                avid = item.get("aid", 0)
                if not avid:
                    continue
                stat = item.get("stat", {})
                score = stat.get("view", 0)  # use view count as score
                rank = saved + 1
                if not RankingData.objects.filter(avid=avid, date=today, list_type='popular').exists():
                    RankingData.objects.create(
                        avid=avid, rank=rank,
                        list_type='popular', score=score,
                        date=today,
                    )
                    saved += 1
                if saved >= count:
                    break
            pn += 1
        except Exception as e:
            print(f"Fetch popular ranking error: {e}")
            break

    print(f"排行榜 [popular] 共采集 {saved} 条")
    return saved


def fetch_and_save_weekly_ranking(count=100):
    """Fetch 7-day region ranking across partitions and save as RankingData with list_type='weekly'."""
    from video.models import RankingData
    from datetime import date

    fetcher = BiliFetcher()
    saved = 0
    today = date.today()

    # Major Bilibili partitions (rid: region id)
    partition_rids = [1, 3, 4, 5, 24, 36, 119, 155, 160, 165, 181, 188]

    for rid in partition_rids:
        if saved >= count:
            break
        try:
            weekly_data = fetcher._get("/x/web-interface/ranking/region",
                                       {"rid": rid, "day": 7})
            items = weekly_data if isinstance(weekly_data, list) else []
            for item in items:
                if saved >= count:
                    break
                avid = item.get("aid", 0)
                if not avid:
                    continue
                play_str = str(item.get("play", "0"))
                # Bilibili may return play count as string with commas or as number
                score = int(play_str.replace(",", "")) if play_str.replace(",", "").isdigit() else 0
                rank = saved + 1
                if not RankingData.objects.filter(avid=avid, date=today, list_type='weekly').exists():
                    RankingData.objects.create(
                        avid=avid, rank=rank,
                        list_type='weekly', score=score,
                        date=today,
                    )
                    saved += 1
        except Exception as e:
            print(f"Fetch weekly ranking for rid={rid} error: {e}")
            continue

    print(f"排行榜 [weekly] 共采集 {saved} 条")
    return saved


def collect_all(keyword="Python", video_count=100, up_count=5, fetch_danmaku=True):
    """一键全量采集：搜索视频 → UP主视频 → 弹幕 → 排行榜 → 热门。

    用法:
        python -c "from data.fetcher import collect_all; collect_all('Python')"
    """
    print("=" * 50)
    print("B站数据全量采集")
    print("=" * 50)

    # 1. 搜索关键词采集视频
    print("\n[1/5] 搜索关键词采集视频...")
    n1 = fetch_and_save_search(keyword, video_count)
    print(f"  -> 采集 {n1} 条视频")

    # 2. 采集热门 UP 主的视频
    print(f"\n[2/5] 采集播放量最高的 {up_count} 个 UP 主的视频...")
    from video.models import VideoData
    from django.db.models import Sum
    top_ups = (
        VideoData.objects.values("up_mid", "up_name")
        .annotate(total_views=Sum("view_count"))
        .order_by("-total_views")[:up_count]
    )
    n2 = 0
    for up in top_ups:
        if up["up_mid"]:
            print(f"  正在采集 UP 主: {up['up_name']} (mid={up['up_mid']})...")
            n2 += fetch_and_save_up_videos(up["up_mid"], 30)
    print(f"  -> 共采集 {n2} 条视频")

    # 3. 采集弹幕
    if fetch_danmaku:
        print("\n[3/5] 为热门视频采集弹幕...")
        n3 = fetch_and_save_danmaku_batch(limit=10)
        print(f"  -> 共采集 {n3} 条弹幕")
    else:
        n3 = 0
        print("\n[3/5] 跳过弹幕采集")

    # 4. 采集排行榜
    print("\n[4/5] 采集排行榜...")
    n4 = fetch_and_save_ranking(rid=0, rtype="all")
    print(f"  -> 共采集 {n4} 条排行数据")

    # 5. 采集热门视频
    print("\n[5/5] 采集热门视频...")
    n5 = fetch_and_save_popular(50)
    print(f"  -> 共采集 {n5} 条视频")

    print("\n" + "=" * 50)
    total_videos = n1 + n2 + n5
    print(f"采集完成！视频: {total_videos} | 弹幕: {n3} | 排行: {n4}")
    print("=" * 50)
