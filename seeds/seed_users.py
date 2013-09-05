from django.contrib.auth.models import User

def execute():
    # Create login accounts for Nathan, Caredwen, and An-Li

    caredwen = User.objects.create_user('caredwenf', 'caredwenf@youthtruthsurvey.org', 'password')
    nathan = User.objects.create_user('nathanh', 'nathanh@youthtruthsurvey.org', 'password')
    anli = User.objects.create_user('an-lih', 'an-lih@youthtruthsurvey.org', 'password')
    caredwen.save()
    nathan.save()
    anli.save()
    print "Seeded accounts for Nathan, An-Li, and Caredwen."