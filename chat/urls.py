from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('create/<int:user_id>/', views.create_chat, name='create_chat'),
    path('create-group/', views.create_group_chat, name='create_group_chat'),
    path('send/<int:room_id>/', views.send_message, name='send_message'),
]
