from django.urls import path

from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.index, name='index'),
    path('home', views.home, name='home'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('train', views.train, name='train'),
    path('test/<int:tid>/<int:qid>', views.question, name='question'),
    path('answer/<int:tid>/<int:qid>/<int:a>', views.answer, name='answer'),
    path('resume/<int:tid>', views.resume, name='resume'),
    path('result/<int:tid>', views.result, name='result')
]