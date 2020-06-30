from django.shortcuts import render, redirect
from django.views import View
from django import http
import re
from meiduo_mall.utils.response_code import RETCODE
from .models import User
# from django.contrib.auth.models import User# 使用自带的User模型类创建用户对象是为了密码加密
from django.contrib.auth import login
from django_redis import get_redis_connection
# 视图代码４大部分：１接收，２验证，３处理，４响应

'''
业务逻辑
# 接收：用户名，密码，确认密码，图形验证码，短信验证码，同意协议
# 验证：　验证以上数据
# 处理：注册，创建用户对象，状态保持
# 响应：重定向到首页

视图设计
--类：RegisterView
--方法：get查．post加，put改，delete删，结论：post
--路由规则：url('^$')
'''

class RegisterView(View):
    def get(self,request):
      return render(request,'register.html')

    def post(self,request):
        '''
        接收
        验证
        处理响应
        :param request:
        :return:
        '''
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        password2 = request.POST.get('cpwd')
        mobile = request.POST.get('phone')
        sms_code = request.POST.get('msg_code')
        allow = request.POST.get('allow')

        # 非空验证
        if not all([username,password,password2,mobile,sms_code,allow]):
            return http.HttpResponseForbidden('填写数据不完整')
        # 用户名验证，格式　格式判断，重名判断
        if not re.match('^[a-zA-Z0-9_-]{5,20}$',username):
            return http.HttpResponseForbidden('用户名非法')
        if User.objects.filter(username=username).count()>0:
            return http.HttpResponseForbidden('用户名已存在')

        # 密码验证,格式，确认密码
        if not re.match('^[0-9A-Za-z]{8,20}$',password):
            return http.HttpResponseForbidden('密码非法')
        if password != password2:
            return http.HttpResponseForbidden('密码不一致')

        # 手机号验证
        if not re.match('^1[345789]\d{9}$',mobile):
            return http.HttpResponseForbidden('手机号码错误')
        if User.objects.filter(mobile=mobile).count()>0:
            return http.HttpResponseForbidden('手机号已存在')
        # 短信验证码，作用为验证手机号为真且在正常使用
        # 读取Redis中的短信验证码
        redis_cli=get_redis_connection('sms_code')
        sms_code_redis=redis_cli.get(mobile)
        if sms_code_redis is None:
            return http.HttpResponseForbidden('短信验证码过期')
        redis_cli.delete(mobile)
        redis_cli.delete(mobile+'_flage')
        if sms_code_redis.decode()!=sms_code:
            return http.HttpResponseForbidden('短信验证码错误，请重新输入')
        # 协议同意验证,if all 中已经验证完毕

        # 处理　创建用户对象
        user = User.objects.create_user(
            username=username,
            password=password,
            mobile=mobile
        )

        #　状态保持,django自带login()方法，实现ssesion操作
        login(request,user)

        # 响应，重定向到首页
        return redirect('/')


class UsernameCountView(View):
    def get(self,request,username):
        #接收：通过路由正则表达式在路径中提取
        #验证：路由的正则表达式已实现验证
        #处理：判断用户名是否存在
        count=User.objects.filter(username=username).count()
        #响应：提示是否存在
        return http.JsonResponse({
            'count':count,
            'code':RETCODE.OK,
            'errmsg':'ok',
        })


class MobileCountView(View):
    def get(self,request,mobile):
        count=User.objects.filter(mobile=mobile).count()

        return http.JsonResponse({
            'count':count,
            'code': RETCODE.OK,
            'errmsg': 'ok',
        })