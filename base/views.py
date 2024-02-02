from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login,logout
from .models import *
from .forms import RoomForm, UserForm, MyUserCreationForm, UploadFileForm
from django.db.models import Q

# Create your views here.



def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

        else:
            messages.error(request,"Username or Password does not exist" )

    context = {'page':page}
    return render(request,'base/login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')

        else:
            messages.error(request, 'An error occured during registration')
    return render(request,'base/login_register.html', {'form':form})
def home(malumot):
    q = malumot.GET.get('q') if malumot.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))


    context = {'rooms':rooms,'topics':topics,
               'room_count':room_count,'room_messages':room_messages}
    return render(malumot,'base/home.html',context)


def room(request,pk):
    room = Room.objects.get(id=pk)



    room_messages = room.message_set.all()
    participants= room.participants.all()
    is_participant = request.user in participants
    if request.method == 'POST':
        if 'join' in request.POST:
            room.participants.add(request.user)
            return redirect('room', pk=room.id)

        if 'remove' in request.POST:
            room.participants.remove(request.user)
            return redirect('room', pk=room.id)

        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )

        return redirect('room',pk=room.id)



    context = {'room':room,'room_messages':room_messages,'participants':participants,'is_participant':is_participant}
    return render(request,'base/room.html',context)

# def roomCourse(request,pk):
#     room = Room.objects.get(id=pk)
#     form = RoomForm()
#     if request.method == 'POST':
#         form = RoomForm(request.POST,request.FILES)
#         file = request.FILES['videos']
#         room.videos = file
#         room.save()
#
#     else:
#         form = RoomForm()
#     context = {'room': room,'form':form}
#     return render(request, 'base/courses.html', context)
def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {'user':user,'rooms':rooms,'room_messages':room_messages,'topics':topics}
    return render(request, 'base/profile.html',context)



@login_required(login_url='login')
def createRoom(malumot):
    form = RoomForm()
    topics = Topic.objects.all()
    if malumot.method == 'POST':
        form = RoomForm(malumot.POST,malumot.FILES)
        # file = malumot.POST.get('photo')
        topic_name = malumot.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=malumot.user,
            topic= topic,
            name=malumot.POST.get('name'),
            description = malumot.POST.get('description'),
            url_title=malumot.POST.get('url_title'),
            url=malumot.POST.get('url'))



        return redirect('home')
    else:
        form = RoomForm()
    context = {'form':form,'topics':topics}
    return render(malumot,'base/room_form.html',context)
@login_required(login_url='login')
def updateRoom(malumot,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if malumot.user != room.host:
        return HttpResponse('You are not allowed here!')

    if malumot.method == 'POST':
        topic_name = malumot.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = malumot.POST.get('name')
        room.topic = topic
        room.description = malumot.POST.get('description')
        room.save()
        return redirect('home')
    context = {'form':form,'topics':topics,'room':room}
    return render(malumot,'base/room_form.html',context)
@login_required(login_url='login')
def deleteRoom(malumot,pk):
    room = Room.objects.get(id=pk)

    if malumot.user != room.host:
        return HttpResponse('You are not allowed here!')

    if malumot.method == 'POST':
        room.delete()
        return redirect('home')
    return render(malumot,'base/delete.html', {'obj':room})

@login_required(login_url='login')
def deleteMessage(malumot,pk):
    message = Message.objects.get(id=pk)

    if malumot.user != message.user:
        return HttpResponse('You are not allowed here!')

    if malumot.method == 'POST':
        message.delete()
        return redirect('home')
    return render(malumot,'base/delete.html', {'obj':message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form':form}
    return render(request,'base/update-user.html',context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request,'base/topics.html',{'topics':topics})


def activityPage(request):
    room_message = Message.objects.all()
    return render(request,'base/activity.html',{'room_messages':room_message})