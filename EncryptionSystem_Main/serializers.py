from rest_framework import serializers
# from django.contrib.auth.models import User
from .models import User, CipherText, KeyFile, PrivateKeyCPHT, PublicKey, ContactApply, Contacts, CheckRecord
import uuid


# 创建一个User的序列化类，继承自serializers.ModelSerializer
class UserSerializer(serializers.ModelSerializer):
    # 创建一个Meta类，用于指定User模型类的一些信息
    class Meta:
        model = User
        fields = ['user_name', 'user_phone', 'user_pwd']  # 表示传入的参数中需要进行加载的内容

    def create(self, validated_data):
        # 生成全局唯一码作为用户id
        validated_data["user_id"] = uuid.uuid4()
        user = User.objects.create(user_status=0, user_level=1, **validated_data)
        return user


# 创建密文序列化类
class CipherTextSerializer(serializers.ModelSerializer):
    # 创建一个Meta类，用于指定User模型类的一些信息
    class Meta:
        model = CipherText
        fields = ['cpht_file', 'cpht_user_id', 'cpht_name', 'cpht_size', 'cpht_kfile_id',
                  'cpht_type', 'cpht_id']  # 表示传入的参数中需要进行加载的内容

    def create(self, validated_data):
        # 生成全局唯一码作为密文id
        #validated_data["cpht_id"] = uuid.uuid4()
        # 创建密文表
        cipher_text = CipherText.objects.create(**validated_data)
        return cipher_text


# 创建密钥表序列化
class KeyFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyFile
        fields = ['kfile_type', 'kfile_size', 'kfile_key', 'kfile_user_id', 'kfile_id']  # 表示传入的参数中需要进行加载的内容

    def create(self, validated_data):
        # 生成全局唯一码作为密钥id

        # 创建密钥表
        key_file = KeyFile.objects.create(**validated_data)
        return key_file


class PrivateKeyCPHTSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateKeyCPHT
        fields = ['pkc_userid', 'pkc_cpht']  # 表示传入的参数中需要进行加载的内容

    def create(self, validated_data):
        # 生成全局唯一码作为密文id
        validated_data["pkc_id"] = uuid.uuid4()
        # 创建密文表
        private_key_cpht = PrivateKeyCPHT.objects.create(**validated_data)
        return private_key_cpht


# 创建公钥序列化类
class publicKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicKey
        fields = ['pk_userid', 'pk_text']  # 表示传入的参数中需要进行加载的内容

    def create(self, validated_data):
        # 生成全局唯一码作为密文id
        validated_data["pk_id"] = uuid.uuid4()
        # 创建密文表
        publicKey = PublicKey.objects.create(**validated_data)
        return publicKey


class ContactApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactApply
        fields = ['capply_userid', 'capply_contactid', 'capply_state', 'capply_inf']  # 表示传入的参数中需要进行加载的内容

    def create(self, validated_data):
        # 创建密文表
        contact_apply = ContactApply.objects.create(**validated_data)
        return contact_apply


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacts
        fields = ['con_userid', 'con_contact_id', 'con_status']  # 表示传入的参数中需要进行加载的内容

    def create(self, validated_data):
        # 创建联系人表
        contact = Contacts.objects.create(**validated_data)
        return contact


# 密钥申请记录表序列化
class CheckRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckRecord
        fields = ['cr_applicant', 'cr_reviewer', 'cr_status', 'kfile_id']  # 表示传入的参数中需要进行加载的内容

    def create(self, validated_data):
        # 生成全局唯一码作为密文id
        validated_data["cr_id"] = uuid.uuid4()
        # 创建密文表
        check_record = CheckRecord.objects.create(**validated_data)
        return check_record
