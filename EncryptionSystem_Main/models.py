from django.db import models
from django.conf import settings


# Create your models here.

class User(models.Model):
    # user_id 为一个全局唯一的用户id
    user_id = models.UUIDField(primary_key=True, verbose_name='用户id')
    user_name = models.CharField(max_length=200, unique=False, verbose_name='用户名')
    user_phone = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    user_status = models.BigIntegerField(default=0, verbose_name='用户状态')
    user_pwd = models.CharField(max_length=32, unique=False, verbose_name='用户密码')
    user_create_time = models.DateTimeField(auto_now_add=True, verbose_name='用户创建时间')
    user_level = models.BigIntegerField(default=0, verbose_name='用户等级')

    def __str__(self):
        return self.user_name
    # q: 在这里使用Meta类的作用是什么？
    # a: Meta类是用于定义一些Django模型类的行为特性的类，它是所有内部类的父类。


# 通知消息表
class Notice(models.Model):
    notice_id = models.UUIDField(primary_key=True, verbose_name='通知id')
    notice_user_id = models.UUIDField(default=0, unique=False, null=False, verbose_name="用户名id")
    notice_type = models.BigIntegerField(default=0, unique=False, null=False)
    notice_msg = models.CharField(max_length=255, default="", verbose_name="消息内容")
    notice_time = models.DateTimeField(auto_now_add=True, verbose_name="提示创建时间")
    notice_state = models.BigIntegerField(default=0, verbose_name="消息状态， 0为   1 为 ")


class PrivateKeyCPHT(models.Model):
    """
    私钥密文表
    """
    pkc_id = models.UUIDField(verbose_name="私钥密文id")
    pkc_userid = models.UUIDField(verbose_name="私钥密文用户id")
    pkc_create_time = models.DateTimeField(auto_now_add=True, verbose_name="私钥密文创建时间")
    # 密文文本
    pkc_cpht = models.CharField(max_length=2048, null= True, verbose_name="私钥密文")

class Contacts(models.Model):
    """
    联系人表
    """
    con_userid = models.UUIDField(verbose_name="用户id")
    con_contact_id = models.UUIDField(null=False, verbose_name="联系人id")
    con_status = models.BigIntegerField(default=0, verbose_name="联系人状态    0：申请中   1：正常好友")


class ContactApply(models.Model):
    """
    联系人申请表
    """
    capply_userid = models.UUIDField(null=False, verbose_name="用户id")
    capply_contactid = models.UUIDField(null=False, verbose_name="联系人id")
    capply_applytime = models.DateTimeField(auto_now_add=True, verbose_name="申请时间")
    capply_state = models.BigIntegerField(default="0", verbose_name="申请状态， 0： ")
    capply_inf = models.CharField(max_length=255, unique=False, verbose_name="申请信息")


class CheckRecord(models.Model):
    """
    密钥申请记录表
    """
    cr_id = models.UUIDField(primary_key=True, null=False, verbose_name="唯一码")
    cr_applicant = models.UUIDField(null=False, verbose_name="申请人id")
    cr_reviewer = models.UUIDField(null=False, verbose_name="回复人id")
    cr_status = models.BigIntegerField(default=0, verbose_name="申请状态 0， 申请中  1： 申请通过，  2： 申请拒绝")
    cr_apply_time = models.DateTimeField(auto_now_add=True, verbose_name="申请时间")
    kfile_id = models.UUIDField(null=False, default=0, verbose_name="密钥id")

class KeyFile(models.Model):
    """
    AES 加密密钥
    """
    kfile_id = models.UUIDField(primary_key=True, null=False, verbose_name="密钥id")
    kfile_user_id = models.UUIDField(null=False, verbose_name="用户id")
    kfile_type = models.BigIntegerField(default=0, verbose_name="密钥类型 ，0： AES密钥")
    kfile_size = models.BigIntegerField(default=0, verbose_name="密钥大小， 单位为KB")
    kfile_upload_time = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    # 密钥文本
    kfile_key = models.CharField(max_length=2048, default="", verbose_name="密钥文本")

class CipherText(models.Model):
    """
    密文表
    """
    cpht_id = models.UUIDField(primary_key=True, null=False, verbose_name="唯一码id")
    cpht_user_id = models.UUIDField(null=False, verbose_name="用户id")
    cpht_name = models.CharField(max_length=255, verbose_name="文件名")
    cpht_size = models.CharField(max_length=255, verbose_name="文件大小")
    apt_upload_time = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    cpht_kfile_id = models.UUIDField(default=0, verbose_name="密钥id")
    # 密文文件 upload_to 的含义是上传到服务器中的路径
    cpht_file = models.FileField(upload_to='cipher_file', null=True, verbose_name="密文文件")
    cpht_type = models.CharField(max_length=255, verbose_name="文件类型")

class SMCMSG(models.Model):
    """
    短信验证码表
    """
    smc_phone = models.CharField(primary_key=True, max_length=11, verbose_name="手机号")
    smc_code = models.CharField(max_length=6, verbose_name="验证码")
    smc_create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    smc_type = models.BigIntegerField(default=0, verbose_name="验证码类型， 0：注册  1：登录  2：修改密码")
    smc_state = models.BigIntegerField(default=0, verbose_name="验证码状态， 0：未验证， 1：已验证")


# 公钥明文表
class PublicKey(models.Model):
    pk_id = models.UUIDField(primary_key=True, verbose_name="公钥id")
    pk_userid = models.UUIDField(verbose_name="用户id")
    pk_create_time = models.DateTimeField(auto_now_add=True, verbose_name="公钥创建时间")
    # 公钥文本
    pk_text = models.CharField(max_length=2048, null=True, verbose_name="公钥文本")