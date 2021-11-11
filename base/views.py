from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, request
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

from .models import Room, Topic, Message
from .forms import RoomForm


def loginPage(request):
    page = 'login'
    
    if request.user.is_authenticated: # checking if the user is logged in, if yes, redirect to homepage
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username, password=password)  # check user exist
            
        except User.DoesNotExist as e:
            messages.error(request, 'Login Error: '+ str(e))
            
        user = authenticate(request, username=username, password=password) # check credentials are correct
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR Password doesnot exist')
    
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)             # request.POST is getting the user data that the user filled 'username','password'
        if form.is_valid():
            user = form.save(commit=False)                # commit = false, is to check the data user passed is valid like the 'password', etc
            user.username = user.username.lower()
            user.save()
            login(request, user)                          # Logging in the current registered user in the current session(cookies)
            
            return redirect('home')
        
        else:
            messages.error(request, 'Error occured during registration, please try again!')
        
    return render(request, 'base/login_register.html', {'form':form})



def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # Filtering rooms for searching by desc, name, topics
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()          # TODO: Only filter out the most rooms or the top topics
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)) # TODO: Show activities of only people follows  # Show recent activities in the homepage

    context = {'rooms': rooms, 'topics':topics, 'room_count':room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created') # Get comments
    participants = room.participants.all() # Get participants in the room page
    
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=pk)

    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)

@login_required(login_url = 'login')
def createRoom(request):
    form = RoomForm()

    if request.method == 'POST':
        # print(request.POST)
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url = 'login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) # instance : room to get the updateRoom prefilled with room values
    
    if request.user != room.host:  # Checking if the logged user is the owner of the room
        return HttpResponse("Access denied, you are not the owner of this room!!!")

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url = 'login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host: # Checking if the logged user is the owner of the room
        return HttpResponse("Access denied, you are not the owner of this room!!!")    

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})



@login_required(login_url = 'login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user: # Checking if the logged user is the owner of the comment/message
        return HttpResponse("Access denied, you are not the owner of this message!!!")    

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':message})