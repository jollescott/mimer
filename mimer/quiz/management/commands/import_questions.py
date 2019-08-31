from django.core.management.base import BaseCommand, CommandError
from quiz.models import Question
import os, json


class Command(BaseCommand):
    help = 'Uploads questions supplied to database.'

    def handle(self, *args, **options):
        file = args[0]

        if file is None:
            raise CommandError('Error: No file specified.')

        if os.path.isfile('./questions.json'):
            questions_file = open('./questions.json', 'r')
            questions_json = questions_file.read()

            questions = json.loads(questions_json)

            for question in questions:
                try:
                    model = Question()
                    model.text = question['text']
                    model.correct = question['correct']

                    model.answer_a = question['alternatives'][0]
                    model.answer_b = question['alternatives'][1]
                    model.answer_c = question['alternatives'][2]
                    model.answer_d = question['alternatives'][3]
                    model.answer_e = question['alternatives'][4]

                    model.save()
                except Exception as e:
                    raise CommandError('Could not process JSON. Possible format error: ' + e)

        else:
            raise CommandError('File was not found')
