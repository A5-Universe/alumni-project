from django.db import models
from users.models import CustomUser
from django.utils import timezone

class ChatRoom(models.Model):
    name = models.CharField(max_length=100, blank=True)
    participants = models.ManyToManyField(CustomUser, related_name='chat_rooms')
    is_group_chat = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.is_group_chat:
            return f"Group: {self.name}"
        else:
            participants = self.participants.all()
            if participants.count() == 2:
                return f"Chat between {participants[0].username} and {participants[1].username}"
            return f"Chat {self.id}"
    
    def get_last_message(self):
        return self.messages.order_by('-timestamp').first()

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.sender.username} in {self.room}"
    
    class Meta:
        ordering = ['timestamp']
