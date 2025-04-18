from django.db import models
from users.models import CustomUser

class Call(models.Model):
    CALL_STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    channel_name = models.CharField(max_length=100)
    initiator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='initiated_calls')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_calls')
    status = models.CharField(max_length=10, choices=CALL_STATUS_CHOICES, default='scheduled')
    scheduled_time = models.DateTimeField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Call between {self.initiator.username} and {self.receiver.username}"
