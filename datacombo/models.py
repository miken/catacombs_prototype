from django.db import models
from django.core.urlresolvers import reverse


# Create your models here.
class ImportSession(models.Model):
    title = models.CharField(max_length=100, default=u'Session with no name')
    date_created = models.DateField()

    def school_count(self):
        count = self.school_set.count()
        return count

    def pr_count(self):
        count = self.schoolparticipation_set.count()
        return count

    def student_count(self):
        count = self.student_set.count()
        return count

    def response_count(self):
        count = self.response_set.count()
        return count

    def __unicode__(self):
        return self.title


class Survey(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ["code"]

    def alpha_suffix(self):
        '''
        Creates a suffix that gets appended to a school alpha
        For example: if a school abbr is 'HTH' and it participated in
        high school teacher feedback survey, its alpha is 'HTH-hs'
        '''
        suffix = self.code[-2:]
        return suffix

    def school_count(self):
        count = self.school_set.count()
        return count

    def get_absolute_url(self):
        return reverse('surveys-view', kwargs={'pk': self.id})

    def __unicode__(self):
        return self.name


class Variable(models.Model):
    survey = models.ForeignKey(Survey)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    active = models.BooleanField()

    class Meta:
        ordering = ["name"]

    def __unicode__(self):
        return self.name


class School(models.Model):
    #This field is used to match with schoolparticipation.legacy_school_short
    alpha = models.CharField(max_length=20, verbose_name=u'Legacy School_Alpha')
    name = models.CharField(max_length=100, verbose_name=u'Full School Name')
    abbrev_name = models.CharField(max_length=50, verbose_name=u'Short Name Used in Report')
    surveys = models.ManyToManyField(Survey, through='SchoolParticipation')
    q_code = models.CharField(max_length=10, blank=True, default='', verbose_name=u'Code used in Qualtrics logins')
    #When the ImportSession is deleted, this school will become "orphaned" and need to be removed individually
    imported_thru = models.ForeignKey(ImportSession, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["name"]

    def repeat_count(self):
        '''This function tells how many times this school has participated in YouthTruth'''
        count = self.schoolparticipation_set.count()
        return count

    def get_absolute_url(self):
        return reverse('schools-view', kwargs={'pk': self.id})

    def __unicode__(self):
        return self.name


class SchoolParticipation(models.Model):
    school = models.ForeignKey(School)
    survey = models.ForeignKey(Survey)
    date_participated = models.DateField()
    legacy_school_short = models.CharField(max_length=20, blank=True, default='', verbose_name=u'Legacy School_Short notation')
    note = models.CharField(max_length=100, blank=True, default='')
    #When the ImportSession is deleted, this participation record will become "orphaned" and need to be removed individually
    imported_thru = models.ForeignKey(ImportSession, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["date_participated"]
        get_latest_by = "date_participated"

    def student_count(self):
        count = self.student_set.count()
        return count

    def __unicode__(self):
        return self.school.name


class Subject(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.subject.name


class Course(models.Model):
    name = models.CharField(max_length=50, verbose_name=u'Course Name')
    subject = models.ForeignKey(Subject)

    def __unicode__(self):
        return self.course.name


class Teacher(models.Model):
    first_name = models.CharField(max_length=50, verbose_name=u'First Name')
    last_name = models.CharField(max_length=50, verbose_name=u'Last Name')
    full_name = u'{first} {last}'.format(first=first_name, last=last_name)
    salutation = models.CharField(max_length=10, default='', verbose_name=u'Salutation')
    salute_name = u'{salute} {last}'.format(salute=salutation, last=last_name)
    feedback_given_in = models.ForeignKey(SchoolParticipation)
    courses = models.ManyToManyField(Course)


class Student(models.Model):
    pin = models.CharField(max_length=20, verbose_name=u'YouthTruth PIN used')
    response_id = models.CharField(max_length=20, verbose_name=u'Response ID recorded by Qualtrics')
    course = models.ForeignKey(Course, null=True)
    teacher = models.ForeignKey(Teacher, null=True)
    surveyed_in = models.ForeignKey(SchoolParticipation)
    imported_thru = models.ForeignKey(ImportSession, null=True)


class Response(models.Model):
    question = models.ForeignKey(Variable)
    survey = models.ForeignKey(Survey)
    answer = models.PositiveSmallIntegerField(blank=True, null=True)
    #Indicates to whom the answer belongs
    #Set null=True for student because of a future possibility of surveying teachers and parents etc.
    student = models.ForeignKey(Student, null=True)
    #Indicates whether the answer was for a course or for a school-overall
    on_course = models.ForeignKey(Course, null=True)
    on_school = models.ForeignKey(School, null=True)
    imported_thru = models.ForeignKey(ImportSession, null=True)
