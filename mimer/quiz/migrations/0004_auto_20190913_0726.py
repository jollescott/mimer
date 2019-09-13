# Generated by Django 2.2.4 on 2019-09-13 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0003_remove_test_train'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='answer_e',
            field=models.CharField(default='Alternative 5', max_length=50),
        ),
        migrations.AlterField(
            model_name='question',
            name='answer_a',
            field=models.CharField(default='Alternative 1', max_length=50),
        ),
        migrations.AlterField(
            model_name='question',
            name='answer_b',
            field=models.CharField(default='Alternative 2', max_length=50),
        ),
        migrations.AlterField(
            model_name='question',
            name='answer_c',
            field=models.CharField(default='Alternative 3', max_length=50),
        ),
        migrations.AlterField(
            model_name='question',
            name='answer_d',
            field=models.CharField(default='Alternative 4', max_length=50),
        ),
    ]