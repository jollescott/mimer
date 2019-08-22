from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
import django.contrib.auth
from . import models

from django.db.models.aggregates import Count
from random import randint


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

        user = django.contrib.auth.authenticate(
            request, username=username, password=password)

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


def create_test(user_id, is_train):
    user = models.QuizUser.objects.get(id=user_id)
    count = models.Question.objects.aggregate(count=Count('id'))['count']

    if count == 0:
        return None

    use_sana = is_train is False and user.sana is True

    questions = []
    
    if use_sana:
        pass
    else:
        for i in range(0, 10):
            random_index = randint(0, count - 1)
            question = models.Question.objects.all()[random_index]
            questions.append(question)

    test = models.Test(user=user, test=True, questions=questions)
    test.train = is_train
    test.save()

    return test

def train(request):
    user_id = request.user.id

    if user_id is None:
        return redirect('index')

    test = create_test(user_id, True)

    if test is None:
        return redirect('home')

    return redirect('/test/{0}/{1}'.format(test.id, test.questions[0].id))

def test(request):
    user_id = request.user.id

    if user_id is None:
        return redirect('index')

    test = create_test(user_id, False)

    if test is None:
        return redirect('home')

    return redirect('/test/{0}/{1}'.format(test.id, test.questions[0].id))

