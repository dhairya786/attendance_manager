import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message,Course,Student
from django.contrib.auth.models import User

class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self,data):
        pk = self.scope['url_route']['kwargs']['pk']
        cc = Course.objects.get(id=pk)
        messages = Message.objects.filter(course=cc).order_by('-timestamp')[:10];
        content = {
            'command' : 'messages',
            'messages' : self.messages_to_json(messages)
        }
        self.send_message(content)

    def new_message(self,data):
        author = data['from']
        author_user = User.objects.filter(username=author)[0]
        pk = self.scope['url_route']['kwargs']['pk']
        cc = Course.objects.get(id=pk)
        message = Message.objects.create(author = author_user,content=data['message'],course=cc)
        content = {
            'command' : 'new_message',
            'message' : self.message_to_json(message)
        }
        return self.send_chat_message(content)

    def messages_to_json(self,messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self,message):
        pk = self.scope['url_route']['kwargs']['pk']
        cc = Course.objects.get(id=pk)
        st = Student.objects.filter(user=message.author)
        return {
            'author' : message.author.username,
            'content' : message.content,
            'timestamp' : str(message.timestamp),
            'course' : cc.name,
            'img' : st[0].image.url,
        }

    commands = {
        'fetch_messages' : fetch_messages,
        'new_message' : new_message
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['pk']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self,data)
        

    def send_chat_message(self,message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self,message):
        self.send(text_data=json.dumps(message))

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps(message))