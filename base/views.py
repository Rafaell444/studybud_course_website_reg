from django.shortcuts import render, redirect
from .models import Room, Topic
from .forms import RoomForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm


# rooms = [
#     {"id": 1, "name": "lets learn python!"},
#     {"id": 2, "name": "design with me"},
#     {"id": 3, "name": "Frontend devs"},
# ]


def loginpage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
        except:
            print(messages.error(request, "user does not exist"))

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "username or password doesnot exist")

    context = {"page": page}
    return render(request, 'base/login_register.html', context)


def logoutuser(request):
    logout(request)
    return redirect("home")


def registerpage(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An error occurred during registration")
    return render(request, 'base/login_register.html', {"form": form})


def home(request):
    q = request.GET.get("q") if request.GET.get('q') is not None else ""
    print(q)

    rooms = Room.objects.filter(Q(topic__name__icontains=q) |
                                Q(name__icontains=q) |
                                Q(description__icontains=q))  # searches by this tree topic.name/room.name/room.description
    print(rooms)

    topic = Topic.objects.all()

    context = {"rooms": rooms, "topics": topic}
    return render(request, "base/home.html", context)


def room(request, pk):
    room = Room.objects.get(id=pk)

    context = {"room": room}

    return render(request, "base/room.html", context)


@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm()
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    context = {"form": form}
    return render(request, "base/room_form.html", context)


@login_required(login_url='/login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("you are not allowed here !")

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect("home")

    context = {"form": form}
    return render(request, "base/room_form.html", context)


@login_required(login_url='/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("you are not allowed here !")

    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": room})
