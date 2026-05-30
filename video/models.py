from django.db import models


class VideoData(models.Model):
    avid = models.BigIntegerField(verbose_name='视频avid', null=True, blank=True)
    bvid = models.CharField(max_length=20, verbose_name='视频bvid', null=True, blank=True)
    title = models.TextField(verbose_name='标题', null=True, blank=True)
    description = models.TextField(verbose_name='视频描述', null=True, blank=True)
    duration = models.IntegerField(verbose_name='时长(秒)', null=True, blank=True)
    publish_time = models.DateTimeField(verbose_name='发布时间', null=True, blank=True)
    partition = models.CharField(max_length=50, verbose_name='分区', null=True, blank=True)
    tags = models.TextField(verbose_name='标签', null=True, blank=True)
    view_count = models.BigIntegerField(verbose_name='播放数', null=True, blank=True)
    like_count = models.BigIntegerField(verbose_name='点赞数', null=True, blank=True)
    coin_count = models.BigIntegerField(verbose_name='投币数', null=True, blank=True)
    favorite_count = models.BigIntegerField(verbose_name='收藏数', null=True, blank=True)
    comment_count = models.BigIntegerField(verbose_name='评论数', null=True, blank=True)
    danmaku_count = models.BigIntegerField(verbose_name='弹幕数', null=True, blank=True)
    share_count = models.BigIntegerField(verbose_name='分享数', null=True, blank=True)
    up_mid = models.BigIntegerField(verbose_name='UP主mid', null=True, blank=True)
    up_name = models.CharField(max_length=100, verbose_name='UP主名称', null=True, blank=True)
    cover_url = models.URLField(verbose_name='封面URL', null=True, blank=True)

    class Meta:
        verbose_name = '视频信息'
        db_table = 'videodata'
        verbose_name_plural = '视频数据'


class UpData(models.Model):
    mid = models.BigIntegerField(verbose_name='UP主mid', unique=True)
    name = models.CharField(max_length=100, verbose_name='昵称', null=True, blank=True)
    signature = models.TextField(verbose_name='简介', null=True, blank=True)
    avatar = models.URLField(verbose_name='头像URL', null=True, blank=True)
    follower_count = models.BigIntegerField(verbose_name='粉丝数', null=True, blank=True)
    following_count = models.BigIntegerField(verbose_name='关注数', null=True, blank=True)
    video_count = models.IntegerField(verbose_name='总视频数', null=True, blank=True)
    total_views = models.BigIntegerField(verbose_name='总播放数', null=True, blank=True)
    total_likes = models.BigIntegerField(verbose_name='总获赞数', null=True, blank=True)
    level = models.IntegerField(verbose_name='等级', null=True, blank=True)
    official_verify = models.TextField(verbose_name='认证信息', null=True, blank=True)

    class Meta:
        verbose_name = 'UP主信息'
        db_table = 'updata'
        verbose_name_plural = 'UP主数据'


class DanmakuData(models.Model):
    content = models.TextField(verbose_name='弹幕内容', null=True, blank=True)
    send_time = models.DateTimeField(verbose_name='发送时间', null=True, blank=True)
    video_time = models.FloatField(verbose_name='视频时间点(秒)', null=True, blank=True)
    dm_type = models.IntegerField(verbose_name='弹幕类型', null=True, blank=True)
    color = models.IntegerField(verbose_name='颜色', null=True, blank=True)
    font_size = models.FloatField(verbose_name='字体大小', null=True, blank=True)
    avid = models.BigIntegerField(verbose_name='所属视频avid', null=True, blank=True)

    class Meta:
        verbose_name = '弹幕信息'
        db_table = 'danmakudata'
        verbose_name_plural = '弹幕数据'


class RankingData(models.Model):
    avid = models.BigIntegerField(verbose_name='视频avid', null=True, blank=True)
    rank = models.IntegerField(verbose_name='排名', null=True, blank=True)
    list_type = models.CharField(max_length=50, verbose_name='榜单类型', null=True, blank=True)
    score = models.IntegerField(verbose_name='综合得分', null=True, blank=True)
    date = models.DateField(verbose_name='上榜日期', null=True, blank=True)

    class Meta:
        verbose_name = '排行信息'
        db_table = 'rankingdata'
        verbose_name_plural = '排行数据'


class User(models.Model):
    username = models.CharField(max_length=255, default='', verbose_name='用户名')
    password = models.CharField(max_length=255, default='', verbose_name='密码')
    avatar = models.ImageField(
        upload_to='avatars/', null=True, blank=True,
        verbose_name='头像', default='img/default-avatar.png'
    )
    createTime = models.DateField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'bili_user'
        verbose_name = '用户信息'
        verbose_name_plural = '用户数据'

    def __str__(self):
        return self.username
