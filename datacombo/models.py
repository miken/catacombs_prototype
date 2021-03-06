from decimal import Decimal

from django.db import models
from django.db.models import Avg
from django.core.urlresolvers import reverse
from django.conf import settings

from secures3 import SecureS3


# Create your models here.
class Survey(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

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
        return ['V4', 'V1', 'School_Short', 'School_Name']

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

    def course_count(self):
        # Use distinct, since a school can participate in the same survey multiple times
        # We care about the number of distinct schools, instead of particpation records
        count = Course.objects.filter(feedback_given_in__in=self.schoolparticipation_set.distinct()).count()
        return count

    def student_count(self):
        count = Student.objects.filter(
            school__schoolparticipation__in=self.schoolparticipation_set.all()
            ).distinct().count()
        return count

    def courses_below_cutoff(self):
        '''
        This function returns a list of course objects that do not meet
        required response count of 5 or response rate of 60 and above
        '''
        # First get all teachers that belong to this survey
        teachers = Teacher.objects.filter(feedback_given_in__in=self.schoolparticipation_set.distinct())
        # Then get all courses that belong to these teachers
        courses = Course.objects.filter(teacher__id__in=teachers)
        courses_to_cut = []
        for c in courses:
            if c.is_below_cutoff():
                courses_to_cut.append(c)
        return courses_to_cut

    def orphaned_teachers(self):
        '''
        This function returns a QuerySet of teachers who do not have
        related course / student / response data for deletion
        '''
        # First get all teachers that have no attached records - bebause its faster
        all_orphaned = Teacher.objects.filter(courses__isnull=True)
        # Then get those for this 
        survey_orphaned = all_orphaned.filter(feedback_given_in__in=self.schoolparticipation_set.distinct())
        return survey_orphaned

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
    # Other meta information goes here
    # Number of rows in the CSV file uploaded
    number_of_rows = models.PositiveSmallIntegerField(blank=True, null=True)
    # Status of whether the uploaded data has been parsed or not
    parse_status = models.BooleanField()

    def school_count(self):
        count = self.school_set.distinct().count()
        return count

    def pr_count(self):
        count = self.schoolparticipation_set.count()
        return count

    def teacher_count(self):
        count = self.teacher_set.count()
        return count

    def course_count(self):
        count = self.course_set.count()
        return count

    def student_count(self):
        count = self.student_set.count()
        return count

    def response_count(self):
        count = self.response_set.count()
        return count

    def get_absolute_url(self):
        return reverse('sessions-view', kwargs={'pk': self.id})

    def __unicode__(self):
        return self.title


class SummaryMeasure(models.Model):
    survey = models.ForeignKey(Survey)
    name = models.CharField(max_length=50)
    label = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Variable(models.Model):
    survey = models.ForeignKey(Survey)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    qual = models.BooleanField(verbose_name=u'Is this a qualitative variable?')
    demographic = models.BooleanField(verbose_name=u'Is this a demographic variable?')
    summary_measure = models.ForeignKey(SummaryMeasure, blank=True, null=True)
    active = models.BooleanField()

    class Meta:
        ordering = ["name"]

    def __unicode__(self):
        return self.name


class VarMap(models.Model):
    '''
    This model instructs how to convert variable in the raw survey data files
    to the existing Variable in the database
    '''
    raw_name = models.CharField(max_length=50, verbose_name=u'Raw Variable Name in Qualtrics')
    variable = models.ForeignKey(Variable, verbose_name=u'Database Variable to map to')
    survey = models.ForeignKey(Survey)

    def get_absolute_url(self):
        return reverse('varmap-edit', kwargs={'pk': self.id})

    def __unicode__(self):
        return self.raw_name


class CustomRecode(models.Model):
    '''
    This model instructs datacombo how to recode a variable from the raw survey data files
    '''
    variable = models.ForeignKey(Variable, verbose_name=u'Database Variable to recode')
    orig_code = models.PositiveSmallIntegerField(verbose_name=u'Original response code in raw data')
    recode = models.PositiveSmallIntegerField(verbose_name=u'Response code in database')

    def __unicode__(self):
        return '{varname}: {orig_code} => {recode}'.format(
            varname=self.variable.name,
            orig_code=self.orig_code,
            recode=self.recode,
        )


class VarMatchRecord(models.Model):
    '''
    This model keeps track of whether a survey variable is found in the uploaded CSV file. There are two cases:
        - If a raw file is uploaded, a VarMatchRecord instance
        establishes the connection between a VarMap and the ImportSession
        and indicates whether match_status is True or False
        - If a legacy data file is uploaded, a VarMatchRecord instance
        establishes the connection between a Variable and the ImportSession
        and indicates whether match_status is True or False
    '''
    session = models.ForeignKey(ImportSession)
    raw_var = models.ForeignKey(VarMap, blank=True, null=True)
    var = models.ForeignKey(Variable, blank=True, null=True)
    match_status = models.BooleanField()

    def varname(self):
        if self.session.import_type == 'raw':
            if self.session.survey.is_teacher_feedback():
                return self.var
            else:
                return self.raw_var
        elif self.session.import_type == 'legacy':
            return self.var

    def __unicode__(self):
        string = '{session} - {var} - {status}'
        if self.raw_var:
            var = self.raw_var
        elif self.var:
            var = self.var
        return string.format(
            session=self.session,
            var=var,
            status=self.match_status
        )


class School(models.Model):
    #This field is used to match with schoolparticipation.legacy_school_short
    alpha = models.CharField(max_length=50, verbose_name=u'Legacy School_Alpha')
    name = models.CharField(max_length=100, verbose_name=u'Full School Name')
    abbrev_name = models.CharField(max_length=50, verbose_name=u'Short Name Used in Report')
    surveys = models.ManyToManyField(Survey, through='SchoolParticipation')
    q_code = models.CharField(max_length=10, blank=True, default='', verbose_name=u'Code used in Qualtrics logins')
    #When the ImportSession is deleted, this school will become "orphaned" and need to be removed individually
    imported_thru = models.ForeignKey(ImportSession, null=True)

    class Meta:
        ordering = ["name"]

    def repeat_count(self, survey):
        '''
        This function tells how many times this school has participated in YouthTruth
        for a given survey
        '''
        count = self.schoolparticipation_set.filter(survey=survey).count()
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
    imported_thru = models.ForeignKey(ImportSession, null=True)

    class Meta:
        ordering = ["date_participated"]
        get_latest_by = "date_participated"

    def month(self):
        return self.date_participated.strftime("%B")

    def year(self):
        return self.date_participated.strftime("%Y")

    def student_count(self):
        # If it's a teacher feedback survey record, use student_set.count() directly
        # Since student responses are cleaned at the course level
        # if self.survey.is_teacher_feedback():
        #     count = self.student_set.count()
        # else:
        #     student_ids = self.response_set.values_list('student__id', flat=True)
        #     count = Student.objects.filter(id__in=student_ids).distinct().count()
        count = Student.objects.filter(school__schoolparticipation=self).count()
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

    def teacher_count(self):
        count = Teacher.objects.filter(courses__in=self.course_set.all()).distinct().count()
        return count

    def course_count(self):
        count = self.course_set.count()
        return count

    def get_absolute_url(self):
        return reverse('subjects-view', kwargs={'pk': self.id})

    def __unicode__(self):
        return self.name


class Student(models.Model):
    pin = models.CharField(max_length=50, verbose_name=u'YouthTruth PIN used')
    response_id = models.CharField(max_length=50, verbose_name=u'Response ID recorded by Qualtrics')
    school = models.ForeignKey(School)
    imported_thru = models.ForeignKey(ImportSession, null=True)

    def __unicode__(self):
        return self.pin + ' - ' + self.school.alpha


class Course(models.Model):
    name = models.CharField(max_length=50, verbose_name=u'Course Name')
    subject = models.ForeignKey(Subject)
    classroom_size = models.PositiveSmallIntegerField(default=0)
    # TODO Add many-to-many relationship with students here so it's easier to count the number of students
    students = models.ManyToManyField(Student)
    legacy_survey_index = models.CharField(max_length=255, default='', verbose_name=u'Index generated from School_Short, Full_Name, and Course_Name')
    feedback_given_in = models.ForeignKey(SchoolParticipation)
    imported_thru = models.ForeignKey(ImportSession, null=True)

    class Meta:
        ordering = ["name"]

    def student_count(self):
        student_ids = self.response_set.values_list('student__id', flat=True)
        count = Student.objects.filter(id__in=student_ids).distinct().count()
        return count

    def rr_raw(self):
        resp_count = self.student_count()
        if self.classroom_size > 0 and resp_count:
            rr = Decimal(resp_count) / Decimal(self.classroom_size)
            return rr
        else:
            return 0

    def rr_string(self):
        rr_raw = self.rr_raw()
        rr_str = "{0:.0f}%".format(rr_raw * 100)
        return rr_str

    def is_below_cutoff(self):
        if self.rr_raw() < 0.6 or self.classroom_size < 5:
            return True
        else:
            return False

    def rating(self, var):
        '''
        Return the average rating in numeric format for a given variable
        var here is an instance of the Variable model
        '''
        course_varset = self.feedback_given_in.survey.variable_set
        if var not in course_varset.all():
            pass
        else:
            # Find all responses for this course
            course_resp = self.response_set.filter(question=var)
            # Take the average
            avg_dict = course_resp.aggregate(Avg('answer'))
            rating = avg_dict['answer__avg']
            return rating

    def get_absolute_url(self):
        return reverse('courses-view', kwargs={'pk': self.id})

    def __unicode__(self):
        return self.name


class Teacher(models.Model):
    first_name = models.CharField(max_length=50, verbose_name=u'First Name')
    last_name = models.CharField(max_length=50, verbose_name=u'Last Name')
    salutation = models.CharField(max_length=10, default='', verbose_name=u'Salutation')
    feedback_given_in = models.ForeignKey(SchoolParticipation)
    courses = models.ManyToManyField(Course)
    legacy_survey_index = models.CharField(max_length=255, default='', verbose_name=u'Index generated from School_Short and Full_Name')
    imported_thru = models.ForeignKey(ImportSession, null=True)

    class Meta:
        ordering = ["legacy_survey_index"]

    def full_name(self):
        full_name = u'{first} {last}'.format(first=self.first_name, last=self.last_name)
        return full_name

    def salute_name(self):
        salute_name = u'{salute} {last}'.format(salute=self.salutation, last=self.last_name)
        return salute_name

    def rating(self, var):
        '''
        Return the average rating for a given variable
        var here is an instance of the Variable model
        '''
        teacher_varset = self.feedback_given_in.survey.variable_set
        if var not in teacher_varset.all():
            pass
        else:
            # Find all responses for this teacher
            # Filter for just responses belonging to these courses
            responses = Response.objects.filter(on_course__in=self.courses.all())
            # Now filter for just responses with this variable
            var_responses = responses.filter(question=var)
            # Take the average
            avg_dict = var_responses.aggregate(Avg('answer'))
            rating = avg_dict['answer__avg']
            return rating

    def get_absolute_url(self):
        return reverse('teachers-view', kwargs={'pk': self.id})

    def __unicode__(self):
        return self.full_name()


class Response(models.Model):
    question = models.ForeignKey(Variable)
    survey = models.ForeignKey(Survey)
    # Response can be stored in either answer or comment, but not both
    # If question.qual is True, then store in comment
    answer = models.PositiveSmallIntegerField(blank=True, null=True)
    comment = models.CharField(max_length=16384, default='')
    # Indicates to whom the answer belongs
    # Set null=True for student because of a future possibility of surveying teachers and parents etc.
    student = models.ForeignKey(Student, null=True)
    #Indicates whether the answer was for a course or for a school-overall
    on_teacher = models.ForeignKey(Teacher, null=True, verbose_name=u'Feedback for which teacher?')
    on_course = models.ForeignKey(Course, null=True, verbose_name=u'Feedback for which course?')
    on_schoolrecord = models.ForeignKey(SchoolParticipation, null=True, verbose_name=u'Feedback for which school record?')
    legacy_survey_index = models.CharField(max_length=255, default='', verbose_name=u'Index generated from School_Short & (Teacher_Name & Course_Name) & Login PIN & varname')
    imported_thru = models.ForeignKey(ImportSession, null=True)

    def __unicode__(self):
        if self.question.qual:
            return '{pin}: ({question} - {answer})'.format(pin=self.student.pin,
                                                           question=self.question.name,
                                                           answer=self.comment)
        else:
            return '{pin}: ({question} - {answer})'.format(pin=self.student.pin,
                                                           question=self.question.name,
                                                           answer=self.answer)


class CSVExport(models.Model):
    QUANT = 'quant'
    QUAL = 'qual'
    UNDEFINED = 'Undefined'
    EXPORT_TYPE_CHOICES = (
        (QUANT, 'Student Ratings'),
        (QUAL, 'Student Comments'),
        (UNDEFINED, 'Undefined'),
    )

    title = models.CharField(max_length=100, default=u'No name')
    file_name = models.CharField(max_length=100, default=u'unnamed.csv')
    date_requested = models.DateField()
    # Which survey was this data used for?
    survey = models.ForeignKey(Survey)
    # Other meta information goes here
    # Whether this was a quantitative or qualitative file export
    export_type = models.CharField(max_length=10,
                                   choices=EXPORT_TYPE_CHOICES,
                                   default=UNDEFINED)
    # Status of whether the CSV file is ready or not
    file_status = models.BooleanField()

    def url(self):
        s3 = SecureS3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        return s3.get_auth_link(settings.AWS_STORAGE_BUCKET_NAME, self.file_name)

    def __unicode__(self):
        return self.title
