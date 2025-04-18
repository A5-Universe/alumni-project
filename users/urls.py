from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('user/<str:username>/', views.user_detail, name='user_detail'),
    path('alumni/', views.alumni_list, name='alumni_list'),
    path('students/', views.student_list, name='student_list'),
]
