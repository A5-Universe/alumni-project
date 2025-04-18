from django.urls import path
from . import views

urlpatterns = [
    path('request/<int:mentor_id>/', views.request_mentorship, name='request_mentorship'),
    path('requests/', views.mentorship_requests, name='mentorship_requests'),
    path('action/<int:session_id>/<str:action>/', views.mentorship_action, name='mentorship_action'),
    path('group/create/', views.create_group_session, name='create_group_session'),
    path('group/all/', views.group_sessions, name='group_sessions'),
    path('group/join/<int:session_id>/', views.join_group_session, name='join_group_session'),
    path('group/leave/<int:session_id>/', views.leave_group_session, name='leave_group_session'),
    path('feedback/<int:session_id>/', views.provide_feedback, name='provide_feedback'),
    path('review/<str:session_type>/<int:session_id>/', views.review_session, name='review_session'),
    path('reviews/<str:session_type>/<int:session_id>/', views.view_session_reviews, name='view_session_reviews'),
    
]

