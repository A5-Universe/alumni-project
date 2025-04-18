from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, StudentProfileForm, AlumniProfileForm
from .models import CustomUser

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created for {user.username}! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        if user.user_type == 'student':
            form = StudentProfileForm(request.POST, request.FILES, instance=user)
        else:
            form = AlumniProfileForm(request.POST, request.FILES, instance=user)
            
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        if user.user_type == 'student':
            form = StudentProfileForm(instance=user)
        else:
            form = AlumniProfileForm(instance=user)
            
    return render(request, 'users/profile.html', {'form': form})

def user_detail(request, username):
    user = get_object_or_404(CustomUser, username=username)
    return render(request, 'users/user_detail.html', {'profile_user': user})

@login_required
def alumni_list(request):
    alumni = CustomUser.objects.filter(user_type='alumni')
    return render(request, 'users/alumni_list.html', {'alumni': alumni})

@login_required
def student_list(request):
    students = CustomUser.objects.filter(user_type='student')
    return render(request, 'users/student_list.html', {'students': students})
