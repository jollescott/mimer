from django.core.management.base import BaseCommand, CommandError
from quiz.models import Question
from sana.learn import (create_or_update_assets, LearnAsset,
    ViewItem, LearnView, create_or_update_view)
from sana.constants import ASSET_EXERCISE


class Command(BaseCommand):
    help = 'Syncs Database with Sana Assets.'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--debug', action='store_true')

    def handle(self, *args, **options):
        assets = []
        debug = options['debug']

        for question in Question.objects.all():
            tags = [question.text, question.answer_a, question.answer_b,
                    question.answer_c, question.answer_d, question.correct]
            asset = LearnAsset(question.id, ASSET_EXERCISE)
            assets.append(asset)

            if debug:
                print('Generated asset: \n')
                print(asset.__dict__)

        try:
            result = create_or_update_assets(assets)
        except Exception as e:
            raise CommandError('Could not upload Sana Assets. Possible network error or wrong API key? ')

        view_items = [ViewItem(asset.id, 'greenlandic/{0}]'.format(asset.id)) for asset in assets]
        view = LearnView('greenlandic', view_items, path='greenlandic')

        create_or_update_view(0, view)
        