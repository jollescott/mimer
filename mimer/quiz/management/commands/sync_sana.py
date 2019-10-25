from django.core.management.base import BaseCommand, CommandError
from quiz.models import Asset
from sana.learn import (create_or_update_assets, LearnAsset,
                        ViewItem, LearnView, create_or_update_view, AssetTag)
from sana.constants import ASSET_EXERCISE


class Command(BaseCommand):
    help = 'Syncs Database with Sana Assets.'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--debug', action='store_true')

    def handle(self, *args, **options):
        assets = []
        debug = options['debug']

        for asset in Asset.objects.all():
            tags = None

            if asset.tags is not None:
                tags = []
                strings = asset.tags.split(',')

                i = 0
                for tag in strings:
                    tags.append(AssetTag('tag{0}'.format(i), tag))
                    i = i + 1

            asset = LearnAsset(asset.id, ASSET_EXERCISE, tags=tags, description=asset.text,
                               content_url='https://frogor.herokuapp.com/asset/{0}'.format(asset.id))
                               
            assets.append(asset)

            if debug:
                print('Generated asset: \n')
                print(asset.__dict__)

        try:
            result = create_or_update_assets(assets)

            if result is False:
                raise CommandError(
                    'Could not upload Sana Assets. Possible network error or wrong API key? ')

        except:
            raise CommandError(
                'Could not upload Sana Assets. Possible network error or wrong API key? ')

        view_items = [
            ViewItem(asset.id, '/greenlandic/{0}'.format(asset.id)) for asset in assets]
        view = LearnView('greenlandic', view_items, path='/greenlandic')
        create_or_update_view(1, view)
