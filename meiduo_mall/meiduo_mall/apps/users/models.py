from django.db import models

# class User(models.Model):
#     username
#     password
#     mobile

# 使用ｄｊａｎｇｏ自带的用户模型类

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    mobile = models.CharField(max_length=11)