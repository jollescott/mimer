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

    test = models.Test(user=user, train=is_train)
    test.save()
    test.questions.set(questions)
    test.save()

    return test


def train(request):
    user_id = request.user.id

    if user_id is None:
        return redirect('index')

    test = create_test(user_id, True)

    if test is None:
        return HttpResponse('Could not create test')

    return redirect('/test/{0}/{1}'.format(test.id, test.questions.all()[0].id))


def test(request):
    user_id = request.user.id

    if user_id is None:
        return redirect('index')

    test = create_test(user_id, False)

    if test is None:
        return redirect('home')

    return redirect('/test/{0}/{1}'.format(test.id, test.questions.all()[0].id))


def question(request, tid, qid):
    user_id = request.user.id

    if user_id is None:
        return redirect('index')

    test = models.Test.objects.get(id=tid)

    if test is None:
        return HttpResponse('Test does not exist.')

    q = test.questions.all().get(id=qid)

    context = {
        'text': q.text,
        'answer_a': q.answer_a,
        'answer_b': q.answer_b,
        'answer_c': q.answer_c,
        'answer_d': q.answer_d,
        'train': test.train,
        'question_id': q.id,
        'test_id': test.id
    }

    return render(request, 'quiz/question.html', context=context)


def answer(request, tid, qid, a):
    user_id = request.user.id

    if user_id is None:
        return redirect('index')

    user = models.QuizUser.objects.get(id=user_id)
    test = models.Test.objects.get(id=tid)

    if test is None:
        return HttpResponse('Test does not exist.')

    q = test.questions.all().get(id=qid)

    correct = q.correct == a

    a = models.Answer(correct=correct, question=q, user=user)
    a.save()

    test.answers.add(a)
    test.save()

    index = 0
    qs = test.questions.all()

    for qc in qs:
        index += 1
        if qc.id == q.id:
            break

    if index >= test.questions.count():
        return redirect('/complete/{0}'.format(test.id))
    else:
        nq = qs[index]
        return redirect('/test/{0}/{1}'.format(test.id, nq.id))
