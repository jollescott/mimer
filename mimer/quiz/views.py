from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import django.contrib.auth
from . import models

from django.db.models.aggregates import Count
from random import randint
from sana.learn import (post_user_events, next_assets, UserEvent, UserEventAttributes,
                        UserEventTag, Mode, AssetFilter, SanaUser)

from sana.constants import EVENT_RESPONSE_SUBMIT, ASSET_EXERCISE, USER_LEARNER
from datetime import datetime
import random


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
    user = request.user

    if user.is_authenticated is False:
        return redirect('index')

    question_count = models.Asset.objects.count()

    context = {
        'overall_score': user.overall_score,
        'name': user.username,
        'question_count': question_count
    }

    try:
        actual_tests = models.Test.objects.filter(user=user).order_by('date')
        tests = []

        for a_test in actual_tests:
            answers = a_test.answers.all()
            correct_count = len(
                list(filter(lambda x: x.correct == True, answers)))
            test_question_count = len(a_test.questions.all())

            test = a_test.__dict__
            test['correct_count'] = correct_count
            test['question_count'] = test_question_count

            tests.append(test)

        context['tests'] = reversed(tests)
    except Exception:
        print('No tests found for user')

    return render(request, 'quiz/home.html', context=context)


def create_test(user):
    count = models.Asset.objects.count()

    if count == 0:
        return None

    use_sana = user.sana is True

    asset_ids = []
    recommendation_contexts = {}

    if use_sana:
        sana_user = SanaUser(user.id, USER_LEARNER)

        asset_filter = AssetFilter([ASSET_EXERCISE], ['/greenlandic'])
        mode = Mode('learn', {
            'language': 'greenlandic'
        })

        data = next_assets(sana_user, 1, asset_filter, mode, 10)

        for asset in data['data']:
            id = asset['asset_id']
            asset_ids.append(int(id))
            recommendation_contexts[str(id)] = asset['recommendation_context']

    else:
        id_range = range(1, count)
        asset_ids = random.sample(id_range, 10)

    assets = models.Asset.objects.all()
    choosen_assets = [asset for asset in assets if asset.id in asset_ids]
    questions = []

    for asset in choosen_assets:
        switch = randint(0, 1) < 1

        q = models.Question()
        q.text = asset.answer if switch else asset.text
        q.switch = switch
        q.asset = asset

        if str(asset.id) in recommendation_contexts:
            q.recommendation_context = recommendation_contexts[str(asset.id)]

        q.save()

        questions.append(q)

        other_assets = [a for a in assets if asset.id != a.id]
        alternative_assets = random.sample(other_assets, 4)
        alternative_assets.append(asset)
        random.shuffle(alternative_assets)

        for aasset in alternative_assets:
            alternative = models.Alternative()
            alternative.asset = aasset
            alternative.question = q
            alternative.correct = aasset.id == asset.id

            alternative.save()

    test = models.Test(user=user)
    test.save()
    test.questions.set(questions)

    return test


def train(request):
    user = request.user

    if user is None:
        return redirect('index')

    try:
        test = create_test(user)
    except BaseException as e:
        return HttpResponse('Could not retrieve questions. <a href="mailto: JoLi0125@student.grillska.se?subject=Server Fault (500)&body={0}">Please report incident.'.format(str(e)), content_type='text/html')

    if test is None:
        return HttpResponse('Could not create test')

    return redirect('/test/{0}/{1}'.format(test.id, test.questions.all()[0].id))


def question(request, tid, qid):
    user_id = request.user.id

    if user_id is None:
        return redirect('index')

    test = models.Test.objects.get(id=tid)

    if test is None:
        return HttpResponse('Test does not exist.')

    q = test.questions.all().get(id=qid)
    alternatives = models.Alternative.objects.filter(question=q)

    context = {
        'text': q.text,
        'answer_a': alternatives[0].asset.text if q.switch else alternatives[0].asset.answer,
        'answer_b': alternatives[1].asset.text if q.switch else alternatives[1].asset.answer,
        'answer_c': alternatives[2].asset.text if q.switch else alternatives[2].asset.answer,
        'answer_d': alternatives[3].asset.text if q.switch else alternatives[3].asset.answer,
        'answer_e': alternatives[4].asset.text if q.switch else alternatives[4].asset.answer,
        'question_id': q.id,
        'test_id': test.id
    }

    return render(request, 'quiz/question.html', context=context)


@csrf_exempt
def answer(request, tid, qid, a):
    user = request.user
    time_str = request.GET.get('time', 0)

    if user is None:
        return HttpResponse(status=401)

    test = models.Test.objects.get(id=tid)

    if test is None:
        return HttpResponse(status=404)

    q = models.Question.objects.get(id=qid)

    existing = models.Answer.objects.filter(question=q).count()

    if existing > 0:
        return HttpResponse(status=403)

    alternatives = models.Alternative.objects.filter(question=q)

    if len(alternatives) < a:
        return HttpResponse(status=403)

    correct = 0

    for alt in alternatives:
        if alt.correct:
            break
        else:
            correct = correct + 1

    is_correct = a == correct
    time = float(time_str)

    a = models.Answer(correct=is_correct, question=q, user=user, time=time)
    a.save()

    test.answers.add(a)
    test.save()

    index = 0
    qs = test.questions.all()

    for qc in qs:
        index += 1
        if qc.id == q.id:
            break

    link = ""

    if index >= test.questions.count():
        test.complete = True
        test.save()

        answers = models.Answer.objects.filter(user=user)
        is_correct = list(filter(lambda x: x.correct == True, answers))

        score = len(is_correct) / len(answers)
        user.overall_score = score
        user.save()

        link = '/result/{0}?completed=true'.format(test.id)
    else:
        nq = qs[index]
        link = '/test/{0}/{1}'.format(test.id, nq.id)

    if request.user.sana:
        user = SanaUser(user.id, USER_LEARNER)

        result = 'correct' if is_correct else 'incorrect'
        events = UserEventAttributes(
            1, q.asset.id, result, score=1, time_spent_ms=time)

        event = UserEvent(user, EVENT_RESPONSE_SUBMIT,
                          events, datetime.utcnow())

        if q.recommendation_context:
            event.recommendation_context = q.recommendation_context

        result = post_user_events([event])
        print(result)

    return JsonResponse({
        'link': link,
        'correct': correct
    })


def resume(request, tid):
    user_id = request.user.id

    if user_id is None:
        return redirect('index')

    test = models.Test.objects.get(id=tid)

    if test is None:
        return HttpResponse('Test does not exist.')

    questions = test.questions.all()
    answer_index = len(test.answers.all())

    if answer_index >= len(questions):
        print('Answer index problem')
        answer_index = len(questions) - 1

    q = questions[answer_index]

    return redirect('/test/{0}/{1}'.format(test.id, q.id))


def result(request, tid):
    completed = request.GET.get('completed', False)

    actual_test = models.Test.objects.get(id=tid)
    test_answers = actual_test.answers.all()

    answers = []

    for test_answer in test_answers:
        q_alternatives = models.Alternative.objects.filter(
            question=test_answer.question)
        alternatives = []

        for i in range(0, len(q_alternatives)):
            alternatives.append({
                'text': q_alternatives[i].asset.answer,
                'correct': q_alternatives[i].correct
            })

        answers.append({
            'text': test_answer.question.text,
            'correct': test_answer.correct,
            'alternatives': alternatives
        })

    test = {
        'datetime': actual_test.date,
        'answers': answers
    }

    context = {
        'completed': completed,
        'test': test
    }

    return render(request, 'quiz/result.html', context=context)

def asset(request, aid): 
    asset = models.Asset.objects.get(id=aid)

    if asset:
        return HttpResponse('{0}: {1}'.format(asset.text, asset.answer))
    else:
        return HttpResponse(status=404)
