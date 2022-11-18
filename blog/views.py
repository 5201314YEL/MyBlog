# -*- coding: UTF-8 -*-
import json
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect
from blog import myforms
from blog import models
from django.http import JsonResponse
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import random
from io import BytesIO
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.db.models import F
from django.db import transaction
from utils import mypage
from bs4 import BeautifulSoup
import os
from MyBlog import settings
# Create your views here.

def register(request):
	form_obj = myforms.MyRegForm()
	if request.method == 'POST':
		# 检验数据是否合法
		back_dic = {'code': 1000, 'msg': ''}
		form_obj = myforms.MyRegForm(request.POST)
		# 判断数据是否合法
		if form_obj.is_valid():
			clean_data = form_obj.cleaned_data
			clean_data.pop('re_password')
			# 用户头像
			avatar = request.FILES.get('avatar')
			print(avatar)
			# 针对用户头像做空值判断
			if avatar:
				clean_data['avatar'] = avatar
			print(clean_data)
			# 操作数据库导入数据
			models.UserInfo.objects.create_user(**clean_data)
			back_dic['url'] = '/blog/login/'
		else:
			back_dic['code'] = 2000
			back_dic['msg'] = form_obj.errors
		return JsonResponse(back_dic)  # 前端args接收back_dic
	return render(request, 'blog/register.html', locals())
def index(request):
	article_queryset = models.Article.objects.all()
	return render(request, 'blog/index.html', locals())
def get_random():
	return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
def get_code(request):
	img_obj = Image.new('RGB', (300, 45), get_random())
	img_draw = ImageDraw.Draw(img_obj)
	img_font = ImageFont.truetype('blog/static/font/思源宋体TW-SemiBold.otf', 30)
	# 	随机验证码
	code = ''
	for i in range(6):
		random_upper = chr(random.randint(65, 90))
		random_lower = chr(random.randint(97, 122))
		random_int = str(random.randint(0, 9))
		tmp = random.choice([random_int, random_lower, random_upper])
		img_draw.text((i * 50 + 18, 0), tmp, get_random(), img_font)
		code += tmp
	request.session['code'] = code
	io_obj = BytesIO()
	img_obj.save(io_obj, format='png')
	image_stream = io_obj.getvalue()
	return HttpResponse(image_stream, content_type="image/png")
def login(request):
	if request.method == 'POST':
		# 正对Ajax请求，通常会定义一个字典
		back_dic = {'code': 1000, 'msg': ''}
		username = request.POST.get('username')
		password = request.POST.get('password')
		code = request.POST.get('code')
		print(code, username, password)
		# 1. 先校验验证码
		if request.session.get('code') == code:
			user_obj = auth.authenticate(request, username=username, password=password)
			if user_obj:
				# 			保存用户状态
				auth.login(request, user_obj)
				back_dic['url'] = '/blog/home/'
			else:
				back_dic['code'] = 2000
				back_dic['msg'] = '用户名或密码错误'
		else:
			back_dic['code'] = 3000
			back_dic['msg'] = '验证码错误'
		return JsonResponse(back_dic)
	return render(request, 'blog/login.html')
@login_required()
def set_password(request):
	if request.is_ajax():
		back_dic = {'code': 1000, 'msg': ''}
		if request.method == 'POST':
			old_password = request.POST.get('old_password')
			new_password = request.POST.get('new_password')
			confirm_password = request.POST.get('confirm_password')
			# print(old_password, new_password, confirm_password)
			if request.user.check_password(old_password):
				if new_password == confirm_password:
					request.user.set_password(new_password)
					request.user.save()
					back_dic['msg'] = '修改成功'
				else:
					back_dic['code'] = 1001
					back_dic['msg'] = '两次密码不一致'
			else:
				back_dic['code'] = 1002
				back_dic['msg'] = '原密码不正确'
		return JsonResponse(back_dic)

def site(request, username, **kwargs):
	"""
	如果**kwargs有值，需要对article_list做额外的操作
	"""
	user_obj = models.UserInfo.objects.filter(username=username).first()
	# 用户如果不存在，返回404页面
	if not user_obj:
		return render(request, 'blog/errors.html')
	blog = user_obj.blog
	article_list = models.Article.objects.filter(blog=blog)
	if kwargs:
		# print(kwargs)  # {'condition': 'tag', 'param': '1'}
		condition = kwargs.get('condition')
		param = kwargs.get('param')
	# 	判断用户按哪个条件进行筛选
		if condition == 'category':
			article_list = article_list.filter(category_id=param)
		elif condition == 'tag':
			article_list = article_list.filter(tags__id=param)
		else:
			year, month = param.split('-')
			article_list = article_list.filter(create_time__year=year, create_time__month=month)
	# 查询当前用户所有的分类以及分类下的文章数
	category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list('name', 'count_num', 'pk')
	# print(category_list)
	# 查询当前用户所有的标签以及标签下的文章数
	tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list('name', 'count_num', 'pk')
	# print(tag_list)
	# 按照年月分组查询所有文章
	date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values('month').annotate(count_num=Count('pk')).values_list('month', 'count_num')
	# print(date_list)
	return render(request, 'blog/site.html', locals())
#  侧边栏筛选针对article_list再次筛选
def article_detail(request, username, article_id):
	user_obj = models.UserInfo.objects.filter(username=username).first()
	blog = user_obj.blog
	# 先获取文章对象
	article_boj = models.Article.objects.filter(pk=article_id, blog__userinfo__username=username).first()
	if not article_boj:
		return render(request, 'blog/errors.html')
	# 获取当前文章的所有评论
	comment_list = models.Comment.objects.filter(article=article_boj)
	return render(request, 'blog/article_detail.html', locals())

def up_or_down(request):
	if request.is_ajax():
		back_dic = {'code':1000, 'msg':''}
		# print(back_dic)
		if request.user.is_authenticated:
			article_id = request.POST.get('article_id')
			is_up = request.POST.get('is_up')
			is_up = json.loads(is_up)
			article_obj = models.Article.objects.filter(pk=article_id).first()
			if not article_obj.blog.userinfo == request.user:
		# 		校验当前用户是否已经点赞了
				is_click = models.UpAndDown.objects.filter(user=request.user, article=article_obj)
		# 		操作数据库，记录数据，同步操作
				if not is_click:
					if is_up:
			# 			给点赞数加1
						models.Article.objects.filter(pk=article_id).update(up_num=F('up_num')+1)
						back_dic['msg'] = '谢谢点赞'
					else:
			# 			给点踩数加1
						models.Article.objects.filter(pk=article_id).update(up_num=F('down_num') + 1)
						back_dic['msg'] = '不要踩我'
					models.UpAndDown.objects.create(user=request.user, article=article_obj, is_up=is_up)
				else:
					back_dic['code'] = 1001
					back_dic['msg'] = '不可重复点赞'
			else:
				back_dic['code'] = 1002
				back_dic['msg'] = '不能给自己的文章点赞'
		else:
			back_dic['code'] = 1003
			back_dic['msg'] = '请先登录'
		return JsonResponse(back_dic)
def comment(request):
	if request.is_ajax():
		back_dic = {'code': 1000, 'msg': ''}
		if request.method == 'POST':
			if request.user.is_authenticated:
				article_id = request.POST.get('article_id')
				content = request.POST.get('content')
				parent_id = request.POST.get('parent_id')
				print(parent_id)
	# 			直接操作评论表存储数据，两张表，开启事务
				with transaction.atomic():
					models.Article.objects.filter(pk = article_id).update(comment_num = F('comment_num') + 1)
					models.Comment.objects.create(user=request.user, article_id=article_id, content=content, parent_id=parent_id)
				back_dic['msg'] = '感谢评论'
			else:
				back_dic['code'] = 1001
				back_dic['msg'] = ['用户未登录']
			# print(back_dic)
			return JsonResponse(back_dic)
def logout(request):
	response = render(request, 'blog/login.html')
	response.delete_cookie(key='sessionid')
	return response

@login_required
def backend(request):
	
	article_list = models.Article.objects.filter(blog=request.user.blog)
	page_obj = mypage.Pagination(current_page=request.GET.get('page', 1), all_count=article_list.count(), per_page_num=10)
	page_queryset = article_list[page_obj.start:page_obj.end]
	return render(request, 'backend/backend.html', locals())


@login_required
def add_article(request):
	if request.method == 'POST':
		title = request.POST.get('title')
		content = request.POST.get('content')
		category_id = request.POST.get('category')
		tag_id_list = request.POST.getlist('tag')
		soup = BeautifulSoup(content, 'html.parser')
		tags = soup.find_all()
		for tag in tags:
			print(tag.name)# 获取页面所有标签
			if tag.name == 'script':
				tag.decomposed()
	# 	文章简介：切取content的前150字符
		desc = soup.text[0:150]
		# desc = content[0:150]
		article_obj = models.Article.objects.create(title=title, content=str(soup),desc=desc, category_id=category_id, blog=request.user.blog)
		article_obj_list = []
		for i in tag_id_list:
			article_obj_list.append(models.ArticleToTag(article=article_obj, tag_id=i))
		models.ArticleToTag.objects.bulk_create(article_obj_list)
		return HttpResponseRedirect('/blog/backend/')
	category_list = models.Category.objects.filter(blog=request.user.blog)
	tag_list = models.Tag.objects.filter(blog=request.user.blog)
	return render(request, 'backend/add_article.html', locals())


def upload_image(request):
	back_dic = {'error': 0}  # 先提前定义返回给编辑器的数据格式
	if request.method == 'POST':
	# 	获取用户上传的图片对象
		file_obj = request.FILES.get('imgFile')
		file_dir = os.path.join(settings.BASE_DIR, 'media', 'article_image')
	# 	先判断该文件夹是否存在，如果不存在，自动创建
		if not os.path.isdir(file_dir):
			os.mkdir(file_dir)
	# 	拼接图片的完整路径
		file_path = os.path.join(file_dir, file_obj.name)
		with open(file_path, 'wb')as f:
			for line in file_obj:
				f.write(line)
		back_dic['url'] = '/media/article_image/%s'%file_obj.name
	return JsonResponse(back_dic)

@login_required
def set_avatar(request):
	if request.method == 'POST':
		file_obj = request.FILES.get('avatar')
		# models.UserInfo.objects.filter(pk=request.user.pk).update(avatar=file_obj) 不会自己加avatar前缀
	# 	1. 手动添加前缀
	#  2.
		user_obj = request.user
		user_obj.avatar = file_obj
		user_obj.save()
		return HttpResponseRedirect('/blog/home/')
	blog = request.user.blog
	username = request.user.username
	return render(request, 'blog/set_avatar.html', locals())
