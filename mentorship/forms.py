from django import forms
from .models import MentorshipSession, GroupSession, Feedback

class MentorshipSessionRequestForm(forms.ModelForm):
    class Meta:
        model = MentorshipSession
        fields = ['title', 'description']
        
class GroupSessionForm(forms.ModelForm):
    date_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text='Format: YYYY-MM-DD HH:MM'
    )
    
    class Meta:
        model = GroupSession
        fields = ['title', 'description', 'date_time', 'max_participants']
        
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
