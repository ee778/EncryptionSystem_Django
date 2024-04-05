# Generated by Django 5.0.3 on 2024-03-07 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CheckRecord',
            fields=[
                ('cr_id', models.UUIDField(primary_key=True, serialize=False, verbose_name='唯一码')),
                ('cr_applicant', models.UUIDField(verbose_name='申请人id')),
                ('cr_reviewer', models.UUIDField(verbose_name='回复人id')),
                ('cr_status', models.BigIntegerField(default=0, verbose_name='申请状态 0， 申请中  1： 申请通过，  2： 申请拒绝')),
                ('cr_apply_time', models.DateTimeField(auto_now_add=True, verbose_name='申请时间')),
            ],
        ),
        migrations.CreateModel(
            name='CipherText',
            fields=[
                ('cpht_id', models.UUIDField(primary_key=True, serialize=False, verbose_name='唯一码id')),
                ('cpht_user_id', models.UUIDField(verbose_name='用户id')),
                ('cpht_name', models.CharField(max_length=255, verbose_name='文件名')),
                ('cpht_size', models.CharField(max_length=255, verbose_name='文件大小')),
                ('apt_upload_time', models.DateTimeField(auto_now_add=True, verbose_name='上传时间')),
                ('cpht_kfile_id', models.UUIDField(default=0, verbose_name='密钥id')),
                ('cpht_file', models.FileField(null=True, upload_to='cipher_file', verbose_name='密文文件')),
            ],
        ),
        migrations.CreateModel(
            name='ContactApply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('capply_userid', models.UUIDField(verbose_name='用户id')),
                ('capply_contactid', models.UUIDField(verbose_name='联系人id')),
                ('capply_applytime', models.DateTimeField(auto_now_add=True, verbose_name='申请时间')),
                ('capply_state', models.BigIntegerField(default='0', verbose_name='申请状态， 0： ')),
                ('capply_inf', models.CharField(max_length=255, verbose_name='申请信息')),
            ],
        ),
        migrations.CreateModel(
            name='Contacts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('con_userid', models.UUIDField(verbose_name='用户id')),
                ('con_contact_id', models.UUIDField(verbose_name='联系人id')),
                ('con_status', models.BigIntegerField(default=0, verbose_name='联系人状态    0：申请中   1：正常好友')),
            ],
        ),
        migrations.CreateModel(
            name='KeyFile',
            fields=[
                ('kfile_id', models.UUIDField(primary_key=True, serialize=False, verbose_name='密钥id')),
                ('kfile_user_id', models.UUIDField(verbose_name='用户id')),
                ('kfile_type', models.BigIntegerField(default=0, verbose_name='密钥类型 ，0： AES密钥')),
                ('kfile_size', models.BigIntegerField(default=0, verbose_name='密钥大小， 单位为KB')),
                ('kfile_upload_time', models.DateTimeField(auto_now_add=True, verbose_name='上传时间')),
                ('kfile_key', models.CharField(default='', max_length=255, verbose_name='密钥文本')),
            ],
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('notice_id', models.UUIDField(primary_key=True, serialize=False, verbose_name='通知id')),
                ('notice_user_id', models.UUIDField(default=0, verbose_name='用户名id')),
                ('notice_type', models.BigIntegerField(default=0)),
                ('notice_msg', models.CharField(default='', max_length=255, verbose_name='消息内容')),
                ('notice_time', models.DateTimeField(auto_now_add=True, verbose_name='提示创建时间')),
                ('notice_state', models.BigIntegerField(default=0, verbose_name='消息状态， 0为   1 为 ')),
            ],
        ),
        migrations.CreateModel(
            name='PrivateKeyCPHT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pkc_id', models.UUIDField(verbose_name='私钥密文id')),
                ('pkc_userid', models.UUIDField(verbose_name='私钥密文用户id')),
                ('pkc_create_time', models.DateTimeField(auto_now_add=True, verbose_name='私钥密文创建时间')),
                ('pkc_cpht', models.CharField(max_length=255, null=True, verbose_name='私钥密文')),
            ],
        ),
        migrations.CreateModel(
            name='SMCMSG',
            fields=[
                ('smc_phone', models.CharField(max_length=11, primary_key=True, serialize=False, verbose_name='手机号')),
                ('smc_code', models.CharField(max_length=6, verbose_name='验证码')),
                ('smc_create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('smc_type', models.BigIntegerField(default=0, verbose_name='验证码类型， 0：注册  1：登录  2：修改密码')),
                ('smc_state', models.BigIntegerField(default=0, verbose_name='验证码状态， 0：未验证， 1：已验证')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.UUIDField(primary_key=True, serialize=False, verbose_name='用户id')),
                ('user_name', models.CharField(max_length=200, verbose_name='用户名')),
                ('user_phone', models.CharField(max_length=11, unique=True, verbose_name='手机号')),
                ('user_status', models.BigIntegerField(default=0, verbose_name='用户状态')),
                ('user_pwd', models.CharField(max_length=32, verbose_name='用户密码')),
                ('user_create_time', models.DateTimeField(auto_now_add=True, verbose_name='用户创建时间')),
                ('user_level', models.BigIntegerField(default=0, verbose_name='用户等级')),
            ],
        ),
    ]
