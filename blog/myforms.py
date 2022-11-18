#!/usr/bin/python
# -*- coding: UTF-8 -*-
# ！python3.9.10
# @Time    : 2022/11/3 16:49
# @Author  : 妙玄
# @File    : myforms.py
# 针对用户表的forms组件代码
from django import forms
from django.core.validators import RegexValidator
from blog import models
class MyRegForm(forms.Form):
	username = forms.CharField(label='用户名',min_length=3, max_length=8, error_messages={
		'min_length': '用户名最少3位',
		'max_length': '用户名最大8位',
		'required': '用户名不能为空'
	}, widget=forms.EmailInput(attrs={'class': 'form-control'}))
	
	password = forms.CharField(label='密码',min_length=6, max_length=16, error_messages={
		'min_length': '密码最少六位',
		'max_length': '密码最大16位',
		'required': '密码不为空'
	}, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
	re_password = forms.CharField(label='再输入密码',max_length=16, min_length=6, error_messages={
		'min_length': '确认密码最少六位',
		'max_length': '确认密码最大16位',
		'required': '确认密码不为空'
	}, widget=forms.PasswordInput(attrs={'class': 'form-control c1 c2'}))
	
	email = forms.EmailField(label='邮箱', error_messages={
		'required':'邮箱不能为空',
		'invalid':'邮箱格式不正确，请输入正确的邮箱'
	},widget=forms.EmailInput(attrs={'class': 'form-control'}))
	# RegexValidatorr('^[0-9]+$', '请输入数字')
	phone = forms.CharField(validators=[RegexValidator(r'^1[0-9]{10}$', '手机号输入错误')],
	                        widget=forms.TextInput(attrs={'class': 'form-control'}))
	# 	1. 局部钩子
	def clean_username(self):
		# 		1. 获取用户名
		username = self.cleaned_data.get('username')
		# 数据库中校验用户名是否已经存在
		is_exits = models.UserInfo.objects.filter(username=username)
		if is_exits:
			self.add_error('username', '用户名已存在，请重新输入')
		return username
	# 	全局钩子
	def clean(self):
		password = self.cleaned_data.get('password')
		re_password = self.cleaned_data.get('re_password')
		if password != re_password:
			self.add_error('re_password', '两次输入密码不一致')
		return self.cleaned_data
