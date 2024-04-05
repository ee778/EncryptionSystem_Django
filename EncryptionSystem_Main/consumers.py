import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from rest_framework.authtoken.models import Token as AuthtokenToken

from EncryptionSystem_Main.models import ContactApply, CheckRecord
from EncryptionSystem_Main.serializers import ContactApplySerializer, ContactSerializer, CheckRecordSerializer


@sync_to_async
def token_is_valid(authToken):
    # 判断数据库中是否有这个token
    authQuery = AuthtokenToken.objects.filter(key=authToken)
    # 如果没有这个token，那么就返回False
    # q: 这里报错：You cannot call this from an async context - use a thread or sync_to_async.
    # a: 这里的问题是因为这里的authQuery是一个异步查询，所以需要
    # 使用sync_to_async将其转换为同步查询

    if not authQuery:
        return False
    # 如果有这个token，那么就返回True
    return True


@sync_to_async
def update_contact_apply(receiver_id, user_id, capply_state=1):
    # 异步执行数据库操作
    ContactApply.objects.filter(capply_userid=receiver_id, capply_contactid=user_id).update(capply_state=capply_state)


@sync_to_async
def update_check_record(cr_applicant: str, cr_reviwer: str, cr_status=1):
    crquery = CheckRecord.objects.filter(cr_applicant=cr_applicant, cr_reviewer=cr_reviwer)
    # 判断是否有这个密钥申请记录
    if not crquery:
        return
    # 如果有这个密钥申请记录，那么就将状态改为传入参数cr_status
    crquery.update(cr_status=cr_status)


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # q： 这里报错TypeError: list indices must be integers or slices, not str
        # a: 这里的self.scope是一个字典，所以不能使用self.scope['headers']['user-token']这种方式获取值

        # 从headers的参数user-token中获取token
        authToken = ''
        for value in self.scope['headers']:
            if value[0].decode() == 'user-token':
                authToken = value[1].decode()
                break
        # 查看是否有token
        if not authToken:
            return
        # 查看token是否有效
        if not token_is_valid(authToken):
            return
        self.room_name = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = 'chat_%s' % self.room_name
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 接收到消息后，将消息发送到聊天组
    async def receive(self, text_data):
        # json内容解析
        try:
            text_data_json = json.loads(text_data)
            text_data_json['type'] = 'chat_message'
            msgType = text_data_json['msg_type']
            receiver_id = text_data_json['receiver_id']
            if msgType == 'chat.message':
                pass
            elif msgType == 'file.send':
                pass
            elif msgType == 'friend.add':
                # 增加一个好友申请表信息
                receier_id = text_data_json['receiver_id']
                apply_info = text_data_json['apply_info']
                user_id = text_data_json['user_id']

                jsonMsg = {
                    'capply_userid': user_id,
                    'capply_contactid': receiver_id,
                    'capply_state': 0,
                    'capply_inf': apply_info
                }
                # 联系人申请表序列化
                contactApplySerializer = ContactApplySerializer(data=jsonMsg)
                if contactApplySerializer.is_valid():
                    await sync_to_async(contactApplySerializer.save)()
            elif msgType == 'friend.recv':
                # 首先判断是否通过请求
                apply_result = text_data_json['apply_result']
                if apply_result == 1:
                    # 如果通过请求，那么就将两个用户添加到对方的联系人列表中
                    jsonMsg = {
                        'con_userid': text_data_json['user_id'],
                        'con_contact_id': text_data_json['receiver_id'],
                        'con_status': 1
                    }
                    # 序列化
                    contactSerializer = ContactSerializer(data=jsonMsg)
                    if contactSerializer.is_valid():
                        await sync_to_async(contactSerializer.save)()

                    # 联系人和联系人之间的关系是双向的，所以还需要添加一次
                    jsonMsg = {
                        'con_userid': text_data_json['receiver_id'],
                        'con_contact_id': text_data_json['user_id'],
                        'con_status': 1
                    }
                    # 序列化
                    contactSerializer = ContactSerializer(data=jsonMsg)
                    if contactSerializer.is_valid():
                        await sync_to_async(contactSerializer.save)()
                    await update_contact_apply(text_data_json['receiver_id'], text_data_json['user_id'], 1)
                else:
                    pass
            elif msgType == 'decr.apply':
                jsonMsg = {
                    'cr_applicant': text_data_json['user_id'],
                    'cr_reviewer': text_data_json['receiver_id'],
                    'cr_status': 0,
                    'kfile_id': text_data_json['kfile_id']
                }
                # 序列化
                checkRecordSerializer = CheckRecordSerializer(data=jsonMsg)
                if checkRecordSerializer.is_valid():

                    await sync_to_async(checkRecordSerializer.save)()
            elif msgType == 'decr.recv':
                # 查看回复是否通过
                status = text_data_json['status']
                if status == 1:
                    # 如果通过，那么就将密钥申请记录表的状态改为1
                    await update_check_record(text_data_json['receiver_id'], text_data_json['user_id'], 1)
                else:
                    # 如果不通过，那么就将密钥文件的状态改为2
                    await update_check_record(text_data_json['receiver_id'], text_data_json['user_id'], 2)

        except json.JSONDecodeError:
            # 如果接收到的数据不是json格式，直接返回
            return
        # 数据库保存异常
        except ModuleNotFoundError:
            return

        if not receiver_id:
            return
        try:
            str_receiver_id = f'chat_{receiver_id}'
            await self.channel_layer.group_send(
                str_receiver_id,
                text_data_json
            )
        # 捕获group_send的异常
        except Exception as e:

            return

    # q: 下面的chat_message具体实现了什么
    # a: 实现了将接收到的消息发送到聊天组
    async def chat_message(self, event):
        msgType = event['msg_type']
        jsonMsg = dict()

        if msgType == 'chat.message':
            jsonMsg['message'] = event['message']
        elif msgType == 'file.send':
            jsonMsg['user_id'] = event['user_id']
            jsonMsg['receiver_id'] = event['receiver_id']
            jsonMsg['file_id'] = event['file_id']
            jsonMsg['file_name'] = event['file_name']
        elif msgType == 'friend.add':
            jsonMsg['user_id'] = event['user_id']
            jsonMsg['receiver_id'] = event['receiver_id']
            jsonMsg['apply_info'] = event['apply_info']
        elif msgType == 'friend.recv':
            jsonMsg['user_id'] = event['user_id']
            jsonMsg['receiver_id'] = event['receiver_id']
            jsonMsg['apply_result'] = event['apply_result']
        elif msgType == 'decr.apply':
            jsonMsg['user_id'] = event['user_id']
            jsonMsg['receiver_id'] = event['receiver_id']
            jsonMsg['kfile_id'] = event['kfile_id']
            jsonMsg['file_name'] = event['file_name']
            jsonMsg['keyfile'] = event['keyfile']
        elif msgType == 'decr.recv':
            jsonMsg['user_id'] = event['user_id']
            jsonMsg['receiver_id'] = event['receiver_id']
            jsonMsg['keyfile'] = event['keyfile']  # 已经使用接收者公钥加密的AES密钥
            jsonMsg['kfile_id'] = event['kfile_id']
            jsonMsg['file_id'] = event['file_id']
            jsonMsg['status'] = event['status']
        jsonMsg['type'] = 'chat_message'
        await self.send(text_data=json.dumps(jsonMsg))
