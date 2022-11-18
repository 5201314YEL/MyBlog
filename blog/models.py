from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


# 1. 先写普通字段
class UserInfo(AbstractUser):
	phone = models.BigIntegerField(verbose_name='手机号', null=True, blank=True)
	'''
	给avatar字段存储文件对象，该文件会自动存储到avatar文件夹下，然后avatar字段的值保存文件路径
	'''
	avatar = models.FileField(verbose_name='头像', upload_to='avatar/', default='avatar/default.png')
	create_time = models.DateField(auto_now_add=True)
	blog = models.OneToOneField(to='Blog', null=True, on_delete=models.CASCADE)
	class Meta:
		db_table = 'UserInfo'
		verbose_name_plural = '用户'
	def __str__(self):
		return self.username
# 个人站点
class Blog(models.Model):
	site_name = models.CharField(verbose_name='站点名称', max_length=32)
	site_title = models.CharField(verbose_name='站点标题', max_length=32)
	site_theme = models.CharField(verbose_name='站点样式', max_length=64, null=True)  # 村css或js的文件路径，简单模拟
	class Meta:
		db_table = 'Blog'
		verbose_name_plural = '站点'
	def __str__(self):
		return self.site_name
# 文章分类
class Category(models.Model):
	name = models.CharField(verbose_name='分类名', max_length=32)
	blog = models.ForeignKey(to='Blog', null=True, on_delete=models.CASCADE)
	class Meta:
		db_table = 'Category'
		verbose_name_plural = '文章分类'
		
	def __str__(self):
		return self.name
# 文章标签
class Tag(models.Model):
	name = models.CharField(verbose_name='标签名', max_length=32)
	blog = models.ForeignKey(to='Blog', null=True, on_delete=models.CASCADE)
	class Meta:
		db_table = 'Tag'
		verbose_name_plural = '文章标签'
	def __str__(self):
		return self.name
# 文章
class Article(models.Model):
	title = models.CharField(verbose_name='文章标题', max_length=64)
	desc = models.CharField(verbose_name='文章简介', max_length=255)
	content = models.TextField(verbose_name='文章内容')
	create_time = models.DateField(auto_now_add=True)
	# 	数据库字段设计优化
	up_num = models.IntegerField(verbose_name='点赞数', default=0)
	down_num = models.IntegerField(verbose_name='点踩数', default=0)
	comment_num = models.IntegerField(verbose_name='评论数', default=0)
	
	blog = models.ForeignKey(to='Blog', null=True, on_delete=models.CASCADE)
	category = models.ForeignKey(to='Category', null=True, on_delete=models.CASCADE)
	tags = models.ManyToManyField(to='Tag', through='ArticleToTag', through_fields=('article', 'tag'))
	class Meta:
		db_table = 'Article'
		verbose_name_plural = '文章'
	def __str__(self):
		return self.title
# 点赞表
class UpAndDown(models.Model):
	user = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE)
	article = models.ForeignKey(to='Article', on_delete=models.CASCADE)
	is_up = models.BooleanField(default=True)
	class Meta:
		db_table = 'UpAndDown'
		verbose_name_plural = '点赞'
# 评论表
class Comment(models.Model):
	user = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE)
	article = models.ForeignKey(to='Article', on_delete=models.CASCADE)
	content = models.CharField(verbose_name='评论内容', max_length=255)
	comment_time = models.DateTimeField(verbose_name='评论时间', auto_now_add=True)
	# 	自关联
	parent = models.ForeignKey(verbose_name='子评论', to='self', null=True, on_delete=models.CASCADE)
	class Meta:
		db_table = 'Comment'
		verbose_name_plural = '评论'
class ArticleToTag(models.Model):
	article = models.ForeignKey(to='Article', on_delete=models.CASCADE)
	tag = models.ForeignKey(to='Tag', on_delete=models.CASCADE)
	class Meta:
		db_table = 'ArticleToTag'
		verbose_name_plural = '文章与标签'
