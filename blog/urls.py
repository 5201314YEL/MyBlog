#!/usr/bin/python
# -*- coding: UTF-8 -*-
# ！python3.9.10
# @Time    : 2022/11/3 15:57
# @Author  : 妙玄
# @File    : urls.py
from django.urls import path,re_path
from blog import views
urlpatterns = [
    path('home/', views.index, name='home'),
    path('register/',views.register, name='register'),
    path('login/',views.login, name='login'),
    # 后台管理
    path('backend/', views.backend, name='backend'),
    # 添加文章
    path('add_article', views.add_article, name='add_article'),
    # 图片验证码
    path('get_code/',views.get_code, name='get_code'),
    path('set_password/',views.set_password, name='set_password'),
    path('logout/', views.logout, name='logout'),
    # 编辑器上传图片接口
    path('upload_image/', views.upload_image, name='upload_image'),
    # 修改用户头像
    path('set_avatar/', views.set_avatar, name='set_avatar'),
    re_path(r'^comment/', views.comment, name='comment'),
#     点赞点踩
    re_path(r'^up_or_down/$', views.up_or_down, name='up_or_down'),
# 个人站点页面搭建
    re_path(r'^(?P<username>\w+)/$', views.site, name='site'),
#     侧边栏筛选针对article_list再次筛选
#     re_path(r'(?P<username>\w+)/category/(\d+)', views.site),# 分类
#     re_path(r'(?P<username>\w+)/tag/(\d+)', views.site), # 标签
#     re_path(r'(?P<username>\w+)/archive/(\w+)', views.site) # 标签
    re_path(r'^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/', views.site),
#     文章详情页
    re_path(r'^(?P<username>\w+)/article/(?P<article_id>\d+)', views.article_detail)
]
