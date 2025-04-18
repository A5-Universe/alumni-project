from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import ChatRoom, Message
from users.models import CustomUser

@login_required
def chat_list(request):
    # Get all chat rooms the user is part of
    chat_rooms = request.user.chat_rooms.all()
    
    # For each room, get the latest message and other participants
    rooms_with_details = []
    for room in chat_rooms:
        latest_message = room.messages.order_by('-timestamp').first()
        
        if room.is_group_chat:
            other_participants = room.participants.exclude(id=request.user.id)
            room_name = room.name
        else:
            other_participants = room.participants.exclude(id=request.user.id)
            room_name = other_participants.first().username if other_participants.exists() else "Empty Chat"
        
        unread_count = room.messages.filter(is_read=False).exclude(sender=request.user).count()
        
        rooms_with_details.append({
            'room': room,
            'latest_message': latest_message,
            'other_participants': other_participants,
            'room_name': room_name,
            'unread_count': unread_count
        })
    
    # Sort by latest message timestamp
    rooms_with_details.sort(
        key=lambda x: x['latest_message'].timestamp if x['latest_message'] else timezone.now(),
        reverse=True
    )
    
    return render(request, 'chat/chat_list.html', {'rooms': rooms_with_details})

@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Check if user is a participant
    if request.user not in room.participants.all():
        messages.error(request, "You don't have access to this chat room.")
        return redirect('chat_list')
    
    # Mark messages as read
    room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    # Get all messages in the room
    chat_messages = room.messages.all()
    
    # Get other participants
    other_participants = room.participants.exclude(id=request.user.id)
    
    context = {
        'room': room,
        'messages': chat_messages,
        'other_participants': other_participants,
    }
    
    return render(request, 'chat/chat_room.html', context)

@login_required
def create_chat(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)
    
    # Check if a chat already exists between these users
    existing_chat = ChatRoom.objects.filter(
        is_group_chat=False,
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    if existing_chat:
        return redirect('chat_room', room_id=existing_chat.id)
    
    # Create a new chat room
    new_chat = ChatRoom.objects.create(is_group_chat=False)
    new_chat.participants.add(request.user, other_user)
    
    return redirect('chat_room', room_id=new_chat.id)

@login_required
def create_group_chat(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        participant_ids = request.POST.getlist('participants')
        
        if not name or len(participant_ids) < 1:
            messages.error(request, 'Please provide a name and select at least one participant.')
            return redirect('create_group_chat')
        
        # Create a new group chat
        new_group = ChatRoom.objects.create(name=name, is_group_chat=True)
        new_group.participants.add(request.user)
        
        # Add selected participants
        for user_id in participant_ids:
            user = CustomUser.objects.get(id=user_id)
            new_group.participants.add(user)
        
        messages.success(request, f'Group chat "{name}" created successfully!')
        return redirect('chat_room', room_id=new_group.id)
    
    # Get potential participants (all users except the current user)
    potential_participants = CustomUser.objects.exclude(id=request.user.id)
    
    return render(request, 'chat/create_group_chat.html', {
        'potential_participants': potential_participants
    })

@login_required
def send_message(request, room_id):
    """API endpoint for sending messages without WebSockets (fallback)"""
    if request.method == 'POST':
        try:
            room = get_object_or_404(ChatRoom, id=room_id)
            content = request.POST.get('message')
            
            if not content:
                return JsonResponse({'status': 'error', 'message': 'Message content is required'})
            
            # Create message
            message = Message.objects.create(
                room=room,
                sender=request.user,
                content=content,
                timestamp=timezone.now()
            )
            
            return JsonResponse({
                'status': 'success',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender_id': message.sender.id,
                    'sender_name': message.sender.username,
                    'timestamp': message.timestamp.isoformat()
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
