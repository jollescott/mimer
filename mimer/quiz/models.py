from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class QuizUser(AbstractUser):
    overall_score = models.SmallIntegerField(default=0)
    sana = models.BooleanField(default=False)

class Question(models.Model):
    text = models.CharField(max_length=50)

    answer_a = models.CharField(max_length=50)
    answer_b = models.CharField(max_length=50)
    answer_c = models.CharField(max_length=50)
    answer_d = models.CharField(max_length=50)

    correct = models.CharField(max_length=1)

    def __str__(self):
        return self.text

class Test(models.Model):
    questions = models.ManyToManyField(Question)
    user = models.ForeignKey(QuizUser, on_delete=models.CASCADE)
    train = models.BooleanField(default=True)

    def __str__(self):
        return "{0} {1}".format(self.user, self.id)