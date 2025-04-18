from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'user_type', 'first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Info', {'fields': ('user_type', 'bio', 'profile_picture', 'graduation_year')}),
        ('Student Info', {'fields': ('course', 'year_of_study')}),
        ('Alumni Info', {'fields': ('company', 'position', 'industry')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile Info', {'fields': ('user_type', 'email', 'first_name', 'last_name')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
