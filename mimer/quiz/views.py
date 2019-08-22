from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
import django.contrib.auth

def index(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')

def login(request):
    if request.user.is_authenticated:
        return redirect('home')

    context = {}

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = django.contrib.auth.authenticate(request, username=username, password=password)

        if user is not None:
            django.contrib.auth.login(request, user)
            return redirect('home')
        else:
            context = {
                'fail': True
            }

    return render(request, 'quiz/login.html', context=context)    

def logout(request):
    django.contrib.auth.logout(request)
    return redirect('index')

def home(request):
    return render(request, 'quiz/home.html')