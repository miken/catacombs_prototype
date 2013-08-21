from django.db import models
from django.core.urlresolvers import reverse


# Create your models here.
class Survey(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ["code"]

    def is_teacher_feedback(self):
        '''
        Determines whether a survey is a teacher feedback survey
        by scanning the first three letters of the survey code
        for the string 'tch'
        '''
        if self.code[:3] == 'tch':
            return True
        else:
            return False

    def panel_columns_for_csv_matching(self):
        '''
        Use this list to determine whether a new panel CSV file is a match
        '''
        if self.is_teacher_feedback():
            return ['School_Short', 'School_Name', 'teachersalutation', 'teacherfirst', 'teacherlast', 'coursename', 'subject']
        else:
            return ['School_Short', 'School_Name']

    def raw_columns_for_csv_matching(self):
        '''
        Use this list to determine whether a new raw CSV file is a match
        '''
        if self.is_teacher_feedback():
            return ['ExternalDataReference', 'School_Short', 'SchoolName', 'teachersalutation1', 'teacherfirst1', 'teacherlast1', 'coursename1', 'subject1']
        else:
            return ['ExternalDataReference', 'School_Short', 'SchoolName']

    def alpha_suffix(self):
        '''
        Creates a suffix that gets appended to a school alpha
        For example: if a school abbr is 'HTH' and it participated in
        high school teacher feedback survey, its alpha is 'HTH-hs'
        '''
        suffix = self.code[-2:]
        return suffix

    def school_count(self):
        # Use distinct, since a school can participate in the same survey multiple times
        # We care about the number of distinct schools, instead of particpation records
        count = self.school_set.distinct().count()
        return count

    def teacher_count(self):
        # Use distinct, since a school can participate in the same survey multiple times
        # We care about the number of distinct schools, instead of particpation records
        count = Teacher.objects.filter(feedback_given_in__in=self.schoolparticipation_set.distinct()).count()
        return count


    def student_count(self):
        # Use distinct, since a school can participate in the same survey multiple times
        # We care about the number of distinct schools, instead of particpation records
        count = Student.objects.filter(surveyed_in__in=self.schoolparticipation_set.distinct()).count()
        return count

    def get_absolute_url(self):
        return reverse('surveys-view', kwargs={'pk': self.id})

    def __unicode__(self):
        return self.name


class ImportSession(models.Model):
    PANEL = 'panel'
    RAW = 'raw'
    LEGACY = 'legacy'
    UNDEFINED = 'Undefined'
    IMPORT_TYPE_CHOICES = (
        (PANEL, 'Qualtrics Panel'),
        (RAW, 'Qualtrics Raw Export'),
        (LEGACY, 'Legacy Data'),
        (UNDEFINED, 'Undefined'),
    )

    title = models.CharField(max_length=100, default=u'Session with no name')
    import_type = models.CharField(max_length=10,
                                   choices=IMPORT_TYPE_CHOICES,
                                   default=UNDEFINED)
    date_created = models.DateField()
    survey = models.ForeignKey(Survey)

    def school_count(self):
        count = self.school_set.distinct().count()
        return count

    def pr_count(self):
        count = self.schoolparticipation_set.count()
        return count

    def teacher_count(self):
        count = self.teacher_set.count()
        return count

    def student_count(self):
        count = self.student_set.count()
        return count

    def response_count(self):
        count = self.response_set.count()
        return count

    def __unicode__(self):
        return self.title


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
    alpha = models.CharField(max_length=50, verbose_name=u'Legacy School_Alpha')
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
    legacy_school_short = models.CharField(max_length=50, blank=True, default='', verbose_name=u'Legacy School_Short notation')
    note = models.CharField(max_length=100, blank=True, default='')
    #When the ImportSession is deleted, this participation record will become "orphaned" and need to be removed individually
    imported_thru = models.ForeignKey(ImportSession, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["date_participated"]
        get_latest_by = "date_participated"

    def month(self):
        return self.date_participated.strftime("%B")

    def year(self):
        return self.date_participated.strftime("%Y")

    def student_count(self):
        count = self.student_set.count()
        return count

    def teacher_count(self):
        count = self.teacher_set.count()
        return count

    def get_absolute_url(self):
        return reverse('schoolparticipations-view', kwargs={'pk': self.id})

    def __unicode__(self):
        return self.legacy_school_short


class Subject(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=50, verbose_name=u'Course Name')
    subject = models.ForeignKey(Subject)
    legacy_survey_key = models.CharField(max_length=255)
    imported_thru = models.ForeignKey(ImportSession, null=True)

    def __unicode__(self):
        return self.name


class Teacher(models.Model):
    first_name = models.CharField(max_length=50, verbose_name=u'First Name')
    last_name = models.CharField(max_length=50, verbose_name=u'Last Name')
    salutation = models.CharField(max_length=10, default='', verbose_name=u'Salutation')
    feedback_given_in = models.ForeignKey(SchoolParticipation)
    courses = models.ManyToManyField(Course)
    imported_thru = models.ForeignKey(ImportSession, null=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    def full_name(self):
        full_name = u'{first} {last}'.format(first=self.first_name, last=self.last_name)
        return full_name

    def salute_name(self):
        salute_name = u'{salute} {last}'.format(salute=self.salutation, last=self.last_name)
        return salute_name

    def __unicode__(self):
        return self.full_name()

class Student(models.Model):
    pin = models.CharField(max_length=50, verbose_name=u'YouthTruth PIN used')
    response_id = models.CharField(max_length=50, verbose_name=u'Response ID recorded by Qualtrics')
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
