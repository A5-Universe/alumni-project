from django.db import models
from users.models import CustomUser

class MentorshipSession(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    mentor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mentor_sessions')
    mentee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mentee_sessions')
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.mentor.username} mentoring {self.mentee.username}"

class GroupSession(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    mentor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='hosted_group_sessions')
    date_time = models.DateTimeField()
    max_participants = models.IntegerField(default=10)
    participants = models.ManyToManyField(CustomUser, related_name='group_sessions', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
        
    @property
    def available_slots(self):
        return self.max_participants - self.participants.count()

class Feedback(models.Model):
    RATING_CHOICES = (
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    )
    
    session = models.ForeignKey(MentorshipSession, on_delete=models.CASCADE, related_name='feedbacks')
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='given_feedbacks')
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_feedbacks')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback from {self.reviewer.username} to {self.recipient.username}"
