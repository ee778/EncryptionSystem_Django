import uuid
from datetime import datetime, timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User as AuthUser
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import FileResponse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from EncryptionSystem_Main.serializers import UserSerializer, CipherTextSerializer, KeyFileSerializer, \
    PrivateKeyCPHTSerializer, publicKeySerializer
from EncryptionSystem_Main.models import User, SMCMSG, KeyFile, PrivateKeyCPHT, PublicKey, Contacts, CipherText
from .aliyun_sms_sdk import AliyunSmsSDK

from .permissions import RegistrationPermission
from rest_framework.authtoken import views as token_views

# settings.AUTH_USER_MODEL
@receiver(post_save, sender=AuthUser)  # django 的信号机制
def generate_token(sender, instance=None, created=False, **kwargs):
    """
    创建用户时自动生成Token
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    if created:
        Token.objects.create(user=instance)


# 创建一个User的视图类，继承自APIView
class CreateUserAPIView(APIView):
    permission_classes = [RegistrationPermission]

    def get(self, request):
        """
        :param request:
        :return:
        """
        queryset = User.objects.all()
        s = UserSerializer(queryset, many=True)
        return Response(data=s.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        :param request:
        :return:
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # 创建 auth_user 表数据
            auth_user = AuthUser.objects.create_user(username=request.data['user_name'],
                                                     password=request.data['user_pwd'])
            return Response(data={"msg": "create success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyDRFApiView(APIView):
    def get(self, request):
        data = {'message': 'hello, world'}
        return Response(data)


# 测试文件上传
class EncryptedFileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, format=None):
        file_obj = request.FILES['cpht_file']

        if not file_obj:
            return Response({'message': '文件上传失败'}, status=status.HTTP_400_BAD_REQUEST)
        # 获取文件类型
        file_type = file_obj.content_type
        request.data['cpht_type'] = str(file_type)
        # 获取文件名
        file_name = file_obj.name
        request.data['cpht_name'] = file_name
        # 获取文件大小
        file_size = file_obj.size
        request.data['cpht_size'] = file_size
        # 获取用户名
        user_name = request.user.username
        # 获取文件id
        request.data['cpht_id'] = request.POST.get("uuid")
        # 通过用户名获取在User表中的id
        user_id = User.objects.get(user_name=user_name).user_id
        if not user_id:
            return Response({'message': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)
        request.data['cpht_user_id'] = user_id

        # 序列化密文
        serializer = CipherTextSerializer(data=request.data)
        if serializer.is_valid():
            # q: 这里报错：You cannot call `.save()` after accessing `serializer.data`.If you need to access data before committing to the database then inspect 'serializer.validated_data' instead.
            # a: 不能在访问serializer.data后调用.save()。如果需要在提交到数据库之前访问数据，请检查'serializer.validated_data'。
            serializer.save()
            # 在这里执行文件上传的操作
            return Response({'message': '文件上传成功'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 密文文件下发
class CipherTextDownloadView(APIView):
    def post(self, request):
        # 获取对应的文件id
        file_id = request.data['file_id']
        if not file_id:
            return Response({'message': 'file_id is empty'}, status=status.HTTP_400_BAD_REQUEST)
        # 获取对应的文件
        file = CipherText.objects.filter(cpht_id=file_id)
        if not file:
            return Response({'message': 'file not exist'}, status=status.HTTP_400_BAD_REQUEST)
        # 获取文件名
        file_name = file[0].cpht_name
        # 获取文件路径
        file_path = file[0].cpht_file.path
        # 返回二进制文件
        # with open(file_path, 'rb') as f:
        #     response = Response(f.read(), content_type='application/octet-stream')
        #     # q:Content-Disposition是什么意思？
        #     # a:Content-Disposition是一个HTTP标头，它指示浏览器应该如何显示附加的文件。如果您希望浏览器显示文件而不是尝试加载它，您可以使用此标头。
        #     response['Content-Disposition'] = 'attachment; filename=' + file_name
        #     return response
        response = FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')  # 使用FileResponse进行流式传输
        response['Content-Disposition'] = f'attachment; filename=' + file_name
        return response

# 注册验证码发送api
class RegistrationAPIView(APIView):
    permission_classes = [RegistrationPermission]
    def post(self, request):
        # 获取手机号
        phone = request.data['phone_number']
        # 发送短信
        AliyunSmsSDK.main(phone, 0)
        return Response(data={"msg": "smc code send success"}, status=status.HTTP_200_OK)


class LoginAPIView(APIView):
    permission_classes = [RegistrationPermission]
    def post(self, request):
        # 获取手机号
        phone = request.data['phone_number']
        # 发送短信
        AliyunSmsSDK.main(phone, 1)
        return Response(data={"msg": "smc code send success"}, status=status.HTTP_200_OK)


class ModifyPwdAPIView(APIView):
    permission_classes = [RegistrationPermission]
    def post(self, request):
        # 获取手机号
        phone = request.data['phone_number']
        # 发送短信
        AliyunSmsSDK.main(phone, 2)
        return Response(data={"msg": "smc code send success"}, status=status.HTTP_200_OK)


# 注册请求验证手机号是否正确、验证码是否正确，是否输入密码
class RegistrationVerification(APIView):
    permission_classes = [RegistrationPermission]
    def post(self, request):
        phone = request.data['phone_number']
        code = request.data['verification_code']
        pwd = request.data['password']
        user_name = request.data['user_name']
        # 验证用户名是否存在
        user_1 = User.objects.filter(user_name=user_name)
        if user_1:
            return Response(data={"msg": "user name has been registered"}, status=status.HTTP_400_BAD_REQUEST)
        # 验证手机号是否存在
        user = User.objects.filter(user_phone=phone)
        if user:
            return Response(data={"msg": "phone has been registered"}, status=status.HTTP_400_BAD_REQUEST)

        smcmsg = SMCMSG.objects.filter(smc_phone=phone, smc_code=code, smc_type=0)
        if not smcmsg:
            return Response(data={"msg": "code error"}, status=status.HTTP_400_BAD_REQUEST)
        # 验证验证码是否超过5分钟
        if smcmsg[0].smc_create_time + timedelta(minutes=5) < datetime.now():
            return Response(data={"msg": "code has been expired"}, status=status.HTTP_400_BAD_REQUEST)

        # 验证密码是否输入
        if not pwd:
            return Response(data={"msg": "pwd is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # 构建一个符合User字段名称的data
        userData = {
            "user_name": request.data['user_name'],
            "user_phone": phone,
            "user_pwd": pwd
        }
        serializer = UserSerializer(data=userData)

        if serializer.is_valid():
            serializer.save()
            # 创建 auth_user 表数据
            auth_user = AuthUser.objects.create_user(username=userData['user_name'],
                                                     password=userData['user_pwd'])

            # 获取use_id
            user_id = User.objects.get(user_phone=phone).user_id
            # 构建一个符合private_key_cpht字段名称的data
            keyData = {
                "pkc_userid": user_id,
                "pkc_cpht": request.data['pkc_cpht']
            }
            pkc_serializer = PrivateKeyCPHTSerializer(data=keyData)
            if pkc_serializer.is_valid():
                pkc_serializer.save()
            else:
                return Response(pkc_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # 构建一个符合public_key字段名称的data
            public_key_data = {
                "pk_userid": user_id,
                "pk_text": request.data['pk_text']
            }
            pk_serializer = publicKeySerializer(data=public_key_data)
            if pk_serializer.is_valid():
                pk_serializer.save()
            else:
                return Response(pk_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(data={"msg": "create success"}, status=status.HTTP_201_CREATED)


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 登录请求验证手机号与密码是否正确，如果正确则返回token和公钥明文和私钥密文
class LoginVerification(APIView):
    permission_classes = [RegistrationPermission]
    def post(self, request):
        phone = request.data['phone_number']
        pwd = request.data['password']
        user = User.objects.filter(user_phone=phone, user_pwd=pwd)
        if not user:
            return Response(data={"msg": "phone or pwd error"}, status=status.HTTP_400_BAD_REQUEST)
        # 获取token的方式如下，通过查询user表中的user_name获取auth_user表中的id， 再通过id查找auth_token表中的token
        user_name = User.objects.filter(user_phone=phone)[0].user_name
        token = Token.objects.get(user=AuthUser.objects.get(username=user_name))
        if not token:
            return Response(data={"msg": "token error"}, status=status.HTTP_400_BAD_REQUEST)

        # 获取user_id 对应的私钥密文
        user_id = User.objects.get(user_phone=phone).user_id
        pkc = PrivateKeyCPHT.objects.filter(pkc_userid=user_id)

        if not pkc:
            return Response(data={"msg": "private key cpht not exist"}, status=status.HTTP_400_BAD_REQUEST)

        # 获取user_id 对应的公钥明文
        puk = PublicKey.objects.filter(pk_userid=user_id)
        if not puk:
            return Response(data={"msg": "public key not exist"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"msg": "login succeed", "token": token.key, "pkc_cpht": pkc[0].pkc_cpht, 'pk_text': puk[0].pk_text, 'user_name': user_name, 'user_id': user_id}, status=status.HTTP_200_OK)


# 修改密码请求验证手机号与验证码是否正确

class ModifyPwdVerification(APIView):
    permission_classes = [RegistrationPermission]
    def post(self, request):
        phone = request.data['phone_number']
        code = request.data['verification_code']
        pwd = request.data['password']
        # 验证手机号是否存在
        user = User.objects.filter(user_phone=phone)
        if not user:
            return Response(data={"msg": "phone not exist"}, status=status.HTTP_400_BAD_REQUEST)

        smcmsg = SMCMSG.objects.filter(smc_phone=phone, smc_code=code, smc_type=2)
        if not smcmsg:
            return Response(data={"msg": "code error"}, status=status.HTTP_400_BAD_REQUEST)
        # 验证验证码是否超过5分钟
        if smcmsg[0].smc_create_time + timedelta(minutes=5) < datetime.now():
            return Response(data={"msg": "code has been expired"}, status=status.HTTP_400_BAD_REQUEST)
        # 验证密码是否输入
        if not pwd:
            return Response(data={"msg": "pwd is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # 修改密码
        user.update(user_pwd=pwd)
        # 修改auth_user表中的密码
        auth_user = AuthUser.objects.get(username=user[0].user_name)
        auth_user.set_password(pwd)

        # 更新userid对应的私钥密文
        user_id = User.objects.get(user_phone=phone).user_id
        pkc = PrivateKeyCPHT.objects.filter(pkc_userid=user_id)
        if not pkc:
            # 构建一个符合private_key_cpht字段名称的data
            keyData = {
                "pkc_userid": user_id,
                "pkc_cpht": request.data['pkc_cpht']
            }
            pkc_serializer = PrivateKeyCPHTSerializer(data=keyData)
            if pkc_serializer.is_valid():
                pkc_serializer.save()
            else:
                return Response(pkc_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            pkc.update(pkc_cpht=request.data['private_key_cpht'])

        return Response(data={"msg": "modify success"}, status=status.HTTP_200_OK)


# 密钥表视图
class KeyFileView(APIView):

    def post(self, request):
        # 获取用户名
        user_name = request.user.username
        # 通过用户名获取在User表中的id
        user_id = User.objects.get(user_name=user_name).user_id
        if not user_id:
            return Response({'msg': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)
        request.data['kfile_user_id'] = user_id
        request.data['kfile_id'] = uuid.uuid4()
        serializer = KeyFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'create success', 'kfile_id': serializer.data['kfile_id']}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContactListView(APIView):
    def post(self, request):
        # 获取用户id
        user_id = request.data['user_id']

        queryobject = User.objects.get(user_id=user_id)
        if not queryobject:
            return Response({'msg': 'user not exist'}, status=status.HTTP_400_BAD_REQUEST)
        contacts = Contacts.objects.all()
        users = User.objects.all()
        user_dict = {user.user_id: user for user in users}
        # 获取用户id 的联系人列表
        queryContacts = Contacts.objects.filter(con_userid=user_id)

        jsonResponse = []
        for contact in queryContacts:
            user = User.objects.get(user_id=contact.con_contact_id)
            if user:
                jsonResponse.append({
                    'user_id': user.user_id,
                    'user_phone': user.user_phone,
                    'user_name': user.user_name
                })

        return Response(jsonResponse, status=status.HTTP_200_OK)



class UserInfoView(APIView):
    def post(self, request):
        # 获取查询的信息
        user_info = request.data['user_info']
        jsonResponse = dict()
        # 查询是否存在这个手机号
        try:
            queryobject = User.objects.get(user_phone=user_info)

            if queryobject:
                jsonResponse["status"] = "success"
                jsonResponse["user_id"] = queryobject.user_id
                jsonResponse["user_phone"] = queryobject.user_phone
                jsonResponse["user_name"] = queryobject.user_name
                return Response(jsonResponse, status=status.HTTP_200_OK)



        except ObjectDoesNotExist:
            pass

        try:
            queryobject1 = User.objects.get(user_name=user_info)

            if queryobject1:
                jsonResponse["status"] = "success"
                jsonResponse["user_id"] = queryobject1.user_id
                jsonResponse["user_phone"] = queryobject1.user_phone
                jsonResponse["user_name"] = queryobject1.user_name
                return Response(jsonResponse, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            pass

        jsonResponse["status"] = "fail"
        return Response(jsonResponse, status=status.HTTP_200_OK)


