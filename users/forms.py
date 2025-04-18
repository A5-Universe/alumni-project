from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'first_name', 'last_name')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'profile_picture')

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('bio', 'profile_picture', 'graduation_year', 'course', 'year_of_study')
        
class AlumniProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('bio', 'profile_picture', 'graduation_year', 'company', 'position', 'industry')
