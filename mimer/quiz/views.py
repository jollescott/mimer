from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
import django.contrib.auth
from . import models

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
    user_id = request.user.id

    if user_id is None:
        return redirect('index')

    user = models.QuizUser.objects.get(id=user_id)
    
    context = {
        'overall_score': user.overall_score
    }

    return render(request, 'quiz/home.html', context=context)