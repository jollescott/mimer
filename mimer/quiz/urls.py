from django.urls import path

from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.index, name='index'),
    path('home', views.home, name='home'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('train', views.train, name='train'),
    path('test', views.test, name='test'),
    path('test/<int:test>/<int:question>', views.question, name='question')
]