# Generated by Django 2.2.4 on 2019-10-25 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0003_question_switch'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='recommendation_context',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]