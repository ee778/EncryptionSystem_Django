from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path, include, re_path

# 使用DRF路由
from rest_framework.routers import DefaultRouter

from EncryptionSystem_Main import views

from . import consumers

router = DefaultRouter()

urlpatterns = [
    path('user/create/', views.CreateUserAPIView.as_view(), name='user_list'),
    # 验证码api
    path('user/verification/registration/', views.RegistrationAPIView.as_view(), name='verification_registration'),
    path('user/verification/login/', views.LoginAPIView.as_view(), name='verification_login'),
    path('user/verification/modify/', views.ModifyPwdAPIView.as_view(), name='verification_forget'),
    path('user/registration/', views.RegistrationVerification.as_view(), name='registration'),
    path('user/login/', views.LoginVerification.as_view(), name='login'),
    path('user/modify/', views.ModifyPwdVerification.as_view(), name='modify'),
    path('test/', views.MyDRFApiView.as_view(), name='test'),
    path('user/upload/file/', views.EncryptedFileUploadView.as_view(), name='file-upload'),
    path('user/download/file/', views.CipherTextDownloadView.as_view(), name='file-downlaod'),
    path('user/upload/keyfile/', views.KeyFileView.as_view(), name='keyfile-upload'),
    path('user/getcontacts/', views.ContactListView.as_view(), name="getcontacts")
]

websocket_urlpatterns = [
    path('ws/chat/<str:user_id>/', consumers.ChatConsumer.as_asgi())
]

#q: 在使用软件连接ws://localhost:8002/ws/chat/friend1时报错：Exception inside application: No route found for path 'ws/chat/friend1'.
#a: 问题出在asgi.py文件中，将AllowedHostsOriginValidator去掉即可。

# q: 但是asgi.py 已经没有AllowedHostsOriginValidator了,还是报错




