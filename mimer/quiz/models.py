from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class QuizUser(AbstractUser):
    overall_score = models.DecimalField(default=0, decimal_places=2, max_digits=100)
    sana = models.BooleanField(default=False)

class Asset(models.Model):
    text = models.CharField(max_length=50) 
    answer = models.CharField(max_length=50)
    tags = models.CharField(max_length=200)

    def __str__(self):
        return "{0} - {1} version: {2}".format(self.text, self.answer, self.id)

class Question(models.Model):
    text = models.CharField(max_length=50)

    def __str__(self):
        return self.text

class Alternative(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    correct = models.BooleanField(default=False)

    question = models.ForeignKey(Question, on_delete=models.CASCADE)

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(QuizUser, on_delete=models.CASCADE)
    correct = models.BooleanField(default=False)
    time = models.DecimalField(default=0, decimal_places=2, max_digits=100)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} {1} version: {2}".format(self.user, self.question, self.id)

class Test(models.Model):
    questions = models.ManyToManyField(Question)
    answers = models.ManyToManyField(Answer)
    user = models.ForeignKey(QuizUser, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return "{0} {1}".format(self.user, self.id)
