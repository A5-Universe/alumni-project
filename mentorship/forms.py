from django import forms
from .models import MentorshipSession, GroupSession, Feedback, SessionReview

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
    widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your feedback about this mentorship experience...'})
        }

class SessionReviewForm(forms.ModelForm):
    class Meta:
        model = SessionReview
        fields = ['rating', 'content']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your thoughts about this session...'})
        }
        labels = {
            'content': 'Review'
        }
