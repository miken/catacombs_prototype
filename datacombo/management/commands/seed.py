from django.core.management.base import BaseCommand, CommandError
import os
import sys

root_dir = os.getcwd()
cmd_dir = os.path.join(root_dir, 'seeds')
os.chdir(cmd_dir)

from seeds import seed_users, seed_surveys, seed_factors, seed_vars, seed_varmaps, seed_recodes, seed_schools


class Command(BaseCommand):
    help = 'Set up surveys and variables for testing'

    def handle(self, *args, **options):
        #seed_users.execute()
        #seed_surveys.execute()
        #seed_schools.execute()
        #seed_factors.execute()
        seed_vars.execute()
        seed_varmaps.execute()
        seed_recodes.execute()
