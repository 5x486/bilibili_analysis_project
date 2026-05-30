from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('index/', views.index, name='index'),
    path('video/', views.video_analysis, name='video'),
    path('up/', views.up_analysis, name='up'),
    path('danmaku/', views.danmaku_analysis, name='danmaku'),
    path('ranking/', views.ranking, name='ranking'),
    path('ai/', views.ai_analysis, name='ai'),
    path('predict/', views.predict, name='predict'),
    path('changeInfo/', views.changeInfo, name='changeInfo'),
    path('logout/', views.logout, name='logout'),
]
