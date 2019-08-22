from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class QuizUser(AbstractUser):
    overall_score = models.SmallIntegerField(default=0)