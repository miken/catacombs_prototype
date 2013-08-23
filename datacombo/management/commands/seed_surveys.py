from django.core.management.base import BaseCommand
from datacombo.models import Survey


class Command(BaseCommand):
    help = 'Seed 5 surveys in the database'

    def handle(self, *args, **options):
        tchhs = Survey(name='HS Teacher Feedback Survey',
                       code='tch-hs')
        tchhs.save()
        tchms = Survey(name='MS Teacher Feedback Survey',
                       code='tch-ms')
        tchms.save()
        tches = Survey(name='ES Teacher Feedback Survey',
                       code='tch-es')
        tches.save()
        schhs = Survey(name='HS Overall Experience Survey',
                       code='sch-hs')
        schhs.save()
        schms = Survey(name='MS Overall Experience Survey',
                       code='sch-ms')
        schms.save()

        print "Seeded 5 surveys"
