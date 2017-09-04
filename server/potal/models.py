# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class UserInfo(models.Model):
	    # CharField类型不能为空,最少要指定一个长度
	    user = models.CharField(max_length=32)
	    pwd = models.CharField(max_length=32)
def get_userinfo_settings():
      all_settings =  UserInfo.objects.all()
#  userinfo_settings = 0
#     userinfo_settings=all_settings[0]
#      return userinfo_settings
      return all_settings
