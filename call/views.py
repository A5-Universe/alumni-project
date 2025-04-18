from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
import random
import time
import json
from agora_token_builder import RtcTokenBuilder
from .models import Call
from users.models import CustomUser

@login_required
def call_home(request):
    # Get upcoming scheduled calls
    upcoming_calls = Call.objects.filter(
        models.Q(initiator=request.user) | models.Q(receiver=request.user),
        status='scheduled',
        scheduled_time__gt=timezone.now()
    ).order_by('scheduled_time')
    
    return render(request, 'call/call_home.html', {'upcoming_calls': upcoming_calls})

@login_required
def schedule_call(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        scheduled_time = request.POST.get('scheduled_time')
        
        if not scheduled_time:
            messages.error(request, 'Please select a valid time for the call.')
            return redirect('schedule_call', user_id=user_id)
        
        # Create a unique channel name
        channel_name = f"call_{request.user.id}_{other_user.id}_{int(time.time())}"
        
        # Create the call
        call = Call.objects.create(
            channel_name=channel_name,
            initiator=request.user,
            receiver=other_user,
            status='scheduled',
            scheduled_time=scheduled_time
        )
        
        messages.success(request, f'Call scheduled with {other_user.username}!')
        return redirect('call_home')
    
    return render(request, 'call/schedule_call.html', {'other_user': other_user})

@login_required
def join_call(request, call_id):
    call = get_object_or_404(Call, id=call_id)
    
    # Check if user is part of the call
    if request.user != call.initiator and request.user != call.receiver:
        messages.error(request, "You don't have access to this call.")
        return redirect('call_home')
    
    # Update call status if it's the first person joining
    if call.status == 'scheduled':
        call.status = 'ongoing'
        call.start_time = timezone.now()
        call.save()
    
    # Generate Agora token
    app_id = settings.AGORA_APP_ID
    app_certificate = settings.AGORA_APP_CERTIFICATE
    channel_name = call.channel_name
    uid = random.randint(1, 230)
    expiration_time_in_seconds = 3600  # 1 hour
    current_timestamp = int(time.time())
    privilege_expired_ts = current_timestamp + expiration_time_in_seconds
    
    token = RtcTokenBuilder.buildTokenWithUid(
        app_id, app_certificate, channel_name, uid, 1, privilege_expired_ts
    )
    
    return render(request, 'call/join_call.html', {
        'call': call,
        'token': token,
        'app_id': app_id,
        'channel_name': channel_name,
        'uid': uid,
    })

@login_required
def end_call(request, call_id):
    call = get_object_or_404(Call, id=call_id)
    
    # Check if user is part of the call
    if request.user != call.initiator and request.user != call.receiver:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    call.status = 'completed'
    call.end_time = timezone.now()
    call.save()
    
    return JsonResponse({'status': 'success'})

@login_required
def cancel_call(request, call_id):
    call = get_object_or_404(Call, id=call_id)
    
    # Check if user is part of the call
    if request.user != call.initiator and request.user != call.receiver:
        messages.error(request, "You don't have access to this call.")
        return redirect('call_home')
    
    call.status = 'cancelled'
    call.save()
    
    messages.info(request, 'Call has been cancelled.')
    return redirect('call_home')
