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
    question_count = models.Question.objects.count()

    context = {
        'overall_score': user.overall_score,
        'name': user.username,
        'question_count': question_count
    }

    try:
        actual_tests = models.Test.objects.filter(user=user)
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

        context['tests'] = tests
    except Exception as e:
        print('No tests found for user')

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
        test.complete = True
        test.save()

        answers = models.Answer.objects.filter(user=user)
        correct = list(filter(lambda x: x.correct == True, answers))

        score = len(correct) / len(answers)
        user.overall_score = score
        user.save()

        return redirect('/result/{0}?completed=true'.format(test.id))
    else:
        nq = qs[index]
        return redirect('/test/{0}/{1}'.format(test.id, nq.id))


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
        alternatives = [test_answer.question.answer_a, test_answer.question.answer_b,
                        test_answer.question.answer_c, test_answer.question.answer_d]

        for i in range(0, len(alternatives)):
            alternatives[i] = {
                'text': alternatives[i],
                'correct': i == test_answer.question.correct
            }

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
