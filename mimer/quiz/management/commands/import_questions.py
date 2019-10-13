from django.core.management.base import BaseCommand, CommandError
from quiz.models import Question, Asset, Alternative
import os, json


class Command(BaseCommand):
    help = 'Uploads questions supplied to database.'

    def add_arguments(self, parser):
        parser.add_argument('questions_json', type=str)
        parser.add_argument('-d', '--debug', action='store_true')
        parser.add_argument('-c', '--count', type=int)
        parser.add_argument('-i', '--init', action='store_true')

    def handle(self, *args, **options):

        if 'questions_json' not in options:
            raise CommandError('Error: No file specified.')

        file = options['questions_json']
        debug = options['debug']
        init = options['init']
        count = options['count']

        if init:
            if Asset.objects.all().count() > 0:
                print('Database has already been seeded!')
                return

        if os.path.isfile(file):
            questions_file = open(file, 'r')
            questions_json = questions_file.read()

            questions = json.loads(questions_json)

            if count:
                questions = questions[:count]

            for question in questions:
                try:
                    asset = Asset()
                    asset.text = question['greenlandic']
                    asset.answer = question['swedish']
                    asset.tags = question['tags']

                    asset.save()

                except Exception as e:
                    raise CommandError('Could not process JSON. Possible format error: ' + str(e))
        else:
            raise CommandError('File was not found')
