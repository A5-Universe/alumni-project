from django.urls import path
from . import views

urlpatterns = [
    path('', views.call_home, name='call_home'),
    path('schedule/<int:user_id>/', views.schedule_call, name='schedule_call'),
    path('join/<int:call_id>/', views.join_call, name='join_call'),
    path('end/<int:call_id>/', views.end_call, name='end_call'),
    path('cancel/<int:call_id>/', views.cancel_call, name='cancel_call'),
]
