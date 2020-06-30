import random

from django import http
from django.shortcuts import render
from django.views import View
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE
from . import constants

class ImageCodeView(View):
    def get(self,request,uuid):
        #接收
        # 验证
        # 处理：１生成图片文本，数据
        text,code,image=captcha.generate_captcha()

        # 　　　２保存图片文本用于后续与用户输入值对比
        redis_cli=get_redis_connection('image_code')
        redis_cli.setex(uuid,constants.IMAGE_CODE_EXPIRES,code)
        # 响应：输出图片数据
        return http.HttpResponse(image,content_type='image/png')


class SmsCodeView(View):
    def get(self,request,mobile):
        # 接收
        uuid=request.GET.get('image_code_id')
        image_code=request.GET.get('image_code')
        # 验证:非空,图形验证码是否正确
        if not all([uuid,image_code]):
            return http.JsonResponse({
                'code':RETCODE.PARAMERR,
                'errmsg':'参数不完整'
            })

        redis_cli = get_redis_connection('image_code')
        image_code_redis=redis_cli.get(uuid)
        if image_code_redis is None:
            return http.JsonResponse({
                'code':RETCODE.IMAGECODEERR,
                'errmsg':'图形验证码过期，点击刷新'
            })
        redis_cli.delete(uuid)

        # 存储在Redis中的数据取出后为二进制数据，不能直接与接收的String类型数据进行对比，
        # 因此要对Redis取出的数据解码操作　.decode(),
        # 以及对两边的字符串同时转换为同样的大小写形式
        if image_code.lower()!=image_code_redis.decode().lower():
            return http.JsonResponse({
                'code':RETCODE.IMAGECODEERR,
                'errmsg':'图形验证码错误'
            })

        # 处理:随机生成６位数
        sms_code='%06d'%random.randint(0,999999)
        # 存入Redis
        redis_cli=get_redis_connection('sms_code')
        redis_cli.setex(mobile,constants.SMS_CODE_EXPIRES,sms_code)
        print(sms_code)
        # 响应
        return http.JsonResponse({
            'code':RETCODE.OK,
            'errmsg':'OK'
        })