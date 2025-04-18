from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import MentorshipSession, GroupSession, Feedback, SessionReview
from .forms import MentorshipSessionRequestForm, GroupSessionForm, FeedbackForm, SessionReviewForm
from users.models import CustomUser
from discussion.models import Topic

def home_view(request):
    if request.user.is_authenticated:
        # Get recent topics for the dashboard
        recent_topics = Topic.objects.all().order_by('-created_at')[:5]

        if request.user.user_type == 'student':
            mentorship_sessions = MentorshipSession.objects.filter(mentee=request.user, status='accepted')
            group_sessions = request.user.group_sessions.all()
        else:  # Alumni
            mentorship_sessions = MentorshipSession.objects.filter(mentor=request.user, status='accepted')
            group_sessions = GroupSession.objects.filter(mentor=request.user)
            
        context = {
            'mentorship_sessions': mentorship_sessions,
            'group_sessions': group_sessions,
            'recent_topics': recent_topics,

        }
        return render(request, 'mentorship/dashboard.html', context)
    else:
        return render(request, 'mentorship/home.html')

@login_required
def request_mentorship(request, mentor_id):
    mentor = get_object_or_404(CustomUser, id=mentor_id, user_type='alumni')
    
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can request mentorship.')
        return redirect('alumni_list')
        
    if request.method == 'POST':
        form = MentorshipSessionRequestForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.mentor = mentor
            session.mentee = request.user
            session.save()
            messages.success(request, f'Mentorship request sent to {mentor.username}!')
            return redirect('mentorship_requests')
    else:
        form = MentorshipSessionRequestForm()
        
    return render(request, 'mentorship/request_mentorship.html', {'form': form, 'mentor': mentor})

@login_required
def mentorship_requests(request):
    user = request.user

    if user.user_type == 'alumni':
        pending_requests = MentorshipSession.objects.filter(mentor=user, status='pending')
        is_mentor = True
    else:
        pending_requests = MentorshipSession.objects.filter(mentee=user)
        is_mentor = False

    for session in pending_requests:
        session.has_feedback = session.feedbacks.filter(reviewer=user).exists()

    context = {
        'requests': pending_requests,
        'is_mentor': is_mentor,
        'user': user,
    }

    return render(request, 'mentorship/mentorship_requests.html', context)


@login_required
def mentorship_action(request, session_id, action):
    session = get_object_or_404(MentorshipSession, id=session_id)
    
    if request.user != session.mentor:
        return HttpResponseForbidden()
        
    if action == 'accept':
        session.status = 'accepted'
        messages.success(request, f'You have accepted the mentorship request from {session.mentee.username}.')
    elif action == 'reject':
        session.status = 'rejected'
        messages.info(request, f'You have rejected the mentorship request from {session.mentee.username}.')
    elif action == 'complete':
        session.status = 'completed'
        messages.success(request, f'You have marked the mentorship with {session.mentee.username} as completed.')
        
    session.save()
    return redirect('mentorship_requests')

@login_required
def create_group_session(request):
    if request.user.user_type != 'alumni':
        messages.error(request, 'Only alumni can create group sessions.')
        return redirect('home')
        
    if request.method == 'POST':
        form = GroupSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.mentor = request.user
            session.save()
            messages.success(request, 'Group session created successfully!')
            return redirect('group_sessions')
    else:
        form = GroupSessionForm()
        
    return render(request, 'mentorship/create_group_session.html', {'form': form})

@login_required
def group_sessions(request):
    upcoming_sessions = GroupSession.objects.filter(date_time__gt=timezone.now()).order_by('date_time')
    return render(request, 'mentorship/group_sessions.html', {'sessions': upcoming_sessions})

@login_required
def join_group_session(request, session_id):
    session = get_object_or_404(GroupSession, id=session_id)
    
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can join group sessions.')
        return redirect('group_sessions')
        
    if session.participants.count() >= session.max_participants:
        messages.error(request, 'This session is already full.')
        return redirect('group_sessions')
        
    session.participants.add(request.user)
    messages.success(request, f'You have joined the group session: {session.title}')
    return redirect('group_sessions')

@login_required
def leave_group_session(request, session_id):
    session = get_object_or_404(GroupSession, id=session_id)
    
    if request.user in session.participants.all():
        session.participants.remove(request.user)
        messages.info(request, f'You have left the group session: {session.title}')
    
    return redirect('group_sessions')

@login_required
def provide_feedback(request, session_id):
    session = get_object_or_404(MentorshipSession, id=session_id, status='completed')
    
    # Determine if user is mentor or mentee
    if request.user == session.mentor:
        recipient = session.mentee
    elif request.user == session.mentee:
        recipient = session.mentor
    else:
        return HttpResponseForbidden()
        
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.session = session
            feedback.reviewer = request.user
            feedback.recipient = recipient
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('mentorship_requests')
    else:
        form = FeedbackForm()
        
    return render(request, 'mentorship/provide_feedback.html', {
        'form': form,
        'session': session,
        'recipient': recipient
    })

@login_required
def review_session(request, session_type, session_id):
    """Add a review for either a mentorship session or a group session"""
    if session_type == 'mentorship':
        session = get_object_or_404(MentorshipSession, id=session_id)
        # Check if user is part of the session
        if request.user != session.mentor and request.user != session.mentee:
            return HttpResponseForbidden()
    else:  # group session
        session = get_object_or_404(GroupSession, id=session_id)
        # Check if user is mentor or participant
        if request.user != session.mentor and request.user not in session.participants.all():
            return HttpResponseForbidden()
    
    # Check if user already reviewed this session
    existing_review = None
    if session_type == 'mentorship':
        existing_review = SessionReview.objects.filter(
            mentorship_session=session, 
            reviewer=request.user
        ).first()
    else:
        existing_review = SessionReview.objects.filter(
            group_session=session, 
            reviewer=request.user
        ).first()
    
    if request.method == 'POST':
        if existing_review:
            form = SessionReviewForm(request.POST, instance=existing_review)
        else:
            form = SessionReviewForm(request.POST)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            
            if session_type == 'mentorship':
                review.mentorship_session = session
            else:
                review.group_session = session
                
            review.save()
            messages.success(request, 'Your review has been submitted!')
            
            if session_type == 'mentorship':
                return redirect('mentorship_requests')
            else:
                return redirect('group_sessions')
    else:
        form = SessionReviewForm(instance=existing_review) if existing_review else SessionReviewForm()
    
    context = {
        'form': form,
        'session': session,
        'session_type': session_type,
        'is_edit': existing_review is not None
    }
    return render(request, 'mentorship/review_session.html', context)

@login_required
def view_session_reviews(request, session_type, session_id):
    """View all reviews for a session"""
    if session_type == 'mentorship':
        session = get_object_or_404(MentorshipSession, id=session_id)
        reviews = SessionReview.objects.filter(mentorship_session=session)
    else:  # group session
        session = get_object_or_404(GroupSession, id=session_id)
        reviews = SessionReview.objects.filter(group_session=session)
    
    context = {
        'session': session,
        'session_type': session_type,
        'reviews': reviews
    }
    return render(request, 'mentorship/session_reviews.html', context)