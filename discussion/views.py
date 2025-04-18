from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Topic, Post, Comment
from .forms import TopicForm, PostForm, CommentForm

@login_required
def topic_list(request):
    topics = Topic.objects.all().order_by('-created_at')
    return render(request, 'discussion/topic_list.html', {'topics': topics})

@login_required
def create_topic(request):
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.created_by = request.user
            topic.save()
            messages.success(request, 'Topic created successfully!')
            return redirect('topic_detail', topic_id=topic.id)
    else:
        form = TopicForm()
    
    return render(request, 'discussion/create_topic.html', {'form': form})

@login_required
def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    posts = topic.posts.all().order_by('-created_at')
    
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.author = request.user
            post.save()
            messages.success(request, 'Post added successfully!')
            return redirect('topic_detail', topic_id=topic.id)
    else:
        form = PostForm()
    
    return render(request, 'discussion/topic_detail.html', {
        'topic': topic,
        'posts': posts,
        'form': form
    })

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('created_at')
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = CommentForm()
    
    return render(request, 'discussion/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })
