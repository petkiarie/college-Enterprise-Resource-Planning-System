from operator import imod
from pydoc_data.topics import topics
from unicodedata import name
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains =q))

    context = {'rooms':rooms, 'topics':topics,
               'room_count':room_count,
               'room_messages': room_messages
               }
    return render(request, 'chatapp/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')

        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room':room, 'room_messages': room_messages, 'participants': participants}

    return render(request, 'chatapp/room.html', context)

def userProfile(request, pk):
    user = get_user_model().objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms,
               'room_messages': room_messages,
               'topics': topics}

    return render(request, 'chatapp/profile.html', context)


@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'chatapp/room_form.html', context)


@login_required(login_url='/login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()


    if request.user != room.host:
        return HttpResponse('You are not allowed to update this room!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'chatapp/room_form.html', context)


@login_required(login_url='/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed to delete this room!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render(request, 'chatapp/delete.html', {'obj':room})


@login_required(login_url='/login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed to delete this message!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')

    return render(request, 'chatapp/delete.html', {'obj':message})


@login_required(login_url='/login')
def updateUser(request):
    user = request.user
    form =  UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'chatapp/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'chatapp/topics.html', {'topics': topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'chatapp/activity.html', {'room_messages': room_messages})