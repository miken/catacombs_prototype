from django.core.management.base import BaseCommand, CommandError
import os
import sys

root_dir = os.getcwd()
cmd_dir = os.path.join(root_dir, 'seeds')
os.chdir(cmd_dir)
# Add to PATH for importing files
sys.path.insert(0, cmd_dir)

import seed_users, seed_surveys, seed_factors, seed_vars, seed_varmaps



class Command(BaseCommand):
    help = 'Set up surveys and variables for testing'

    def handle(self, *args, **options):
        seed_users.execute()
        seed_surveys.execute()
        seed_factors.execute()
        seed_vars.execute()
        seed_varmaps.execute()