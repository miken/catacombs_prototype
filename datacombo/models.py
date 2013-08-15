from django.db import models


# Create your models here.
class ImportSession(models.Model):
    date_created = models.DateField()


class Survey(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    def school_count(self):
        schools_participated = self.school_set.all()
        count = len(schools_participated)
        return count

    def __unicode__(self):
        return self.name


class Variable(models.Model):
    survey = models.ForeignKey(Survey)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    active = models.BooleanField()

    def __unicode__(self):
        return self.name


class School(models.Model):
    short = models.CharField(max_length=20, verbose_name=u'Old School_Short notation')
    name = models.CharField(max_length=100, verbose_name=u'Full School Name')
    abbrev_name = models.CharField(max_length=50, verbose_name=u'Short Name Used in Report')
    surveys = models.ManyToManyField(Survey, through='SchoolParticipation')
    q_code = models.CharField(max_length=10, verbose_name=u'Code used in Qualtrics logins')
    imported_thru = models.ForeignKey(ImportSession, null=True)

    def __unicode__(self):
        return self.name


class SchoolParticipation(models.Model):
    school = models.ForeignKey(School)
    survey = models.ForeignKey(Survey)
    date_participated = models.DateField()
    note = models.CharField(max_length=100, blank=True, null=True)
    imported_thru = models.ForeignKey(ImportSession, null=True)

    def __unicode__(self):
        return self.school.name


class Course(models.Model):
    name = models.CharField(max_length=50, verbose_name=u'Course Name')
    subject = models.CharField(max_length=50)


class Teacher(models.Model):
    first_name = models.CharField(max_length=50, verbose_name=u'First Name')
    last_name = models.CharField(max_length=50, verbose_name=u'Last Name')
    full_name = u'{first} {last}'.format(first=first_name, last=last_name)
    salutation = models.CharField(max_length=10, verbose_name=u'Salutation')
    salute_name = u'{salute} {last}'.format(salute=salutation, last=last_name)
    school = models.ForeignKey(School)
    courses = models.ManyToManyField(Course)


class Student(models.Model):
    pin = models.CharField(max_length=20, verbose_name=u'YouthTruth PIN used')
    response_id = models.CharField(max_length=20, verbose_name=u'Response ID recorded by Qualtrics')
    course = models.ForeignKey(Course, null=True)
    teacher = models.ForeignKey(Teacher, null=True)
    school = models.ForeignKey(School, null=True)
    imported_thru = models.ForeignKey(ImportSession, null=True)


class Response(models.Model):
    question = models.ForeignKey(Variable)
    survey = models.ForeignKey(Survey)
    answer = models.PositiveSmallIntegerField(blank=True, null=True)
    #Indicates to whom the answer belongs
    student = models.ForeignKey(Student, null=True)
    #Indicates whether the answer was for a teacher or for a school
    on_teacher = models.ForeignKey(Teacher, null=True)
    on_school = models.ForeignKey(School, null=True)
    imported_thru = models.ForeignKey(ImportSession, null=True)
