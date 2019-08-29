from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class QuizUser(AbstractUser):
    overall_score = models.DecimalField(default=0, decimal_places=2, max_digits=100)
    sana = models.BooleanField(default=False)

class IntegerRangeField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)
    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value':self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)

class Question(models.Model):
    text = models.CharField(max_length=50)

    answer_a = models.CharField(max_length=50)
    answer_b = models.CharField(max_length=50)
    answer_c = models.CharField(max_length=50)
    answer_d = models.CharField(max_length=50)

    correct = IntegerRangeField(min_value=0, max_value=3, default=0)

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(QuizUser, on_delete=models.CASCADE)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return "{0} {1} version: {2}".format(self.user, self.question, self.id)

class Test(models.Model):
    questions = models.ManyToManyField(Question)
    answers = models.ManyToManyField(Answer)
    user = models.ForeignKey(QuizUser, on_delete=models.CASCADE)
    train = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now=True)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return "{0} {1}".format(self.user, self.id)