import datetime

from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView

# These two are used for user authentication
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# This is for file storage on S3
from django.core.files.storage import default_storage

# Import models and custom forms
from datacombo.models import Variable, School, Survey, ImportSession, SchoolParticipation, Teacher, Subject, Course, VarMap, SummaryMeasure, CSVExport, CustomRecode
from datacombo.forms import UploadFileForm, SchoolParticipationForm, VarForm, VarMapForm, CSVExportForm, CustomRecodeForm
from datacombo.upload import process_uploaded
from datacombo.export import s3_write_response_data, create_csvexport

# Set up RQ queue
import django_rq
q = django_rq.get_queue('default')


#Index View
def home_or_login(request):
    if request.user.is_authenticated():
        return redirect('home-view')
    else:
        return redirect('login-view')


class HomeView(TemplateView):

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['all_surveys'] = Survey.objects.all()
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomeView, self).dispatch(*args, **kwargs)


#Views for Variable
class ListVariableView(ListView):

    model = Variable
    template_name = 'variable/variable_list.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListVariableView, self).dispatch(*args, **kwargs)


class CreateVariableView(CreateView):

    model = Variable
    template_name = 'variable/edit_variable.html'

    def get_success_url(self):
        return reverse(
            'surveys-view',
            kwargs={'pk': self.get_object().survey.id}
        )

    def get_context_data(self, **kwargs):

        context = super(CreateVariableView, self).get_context_data(**kwargs)
        context['action'] = reverse('variables-new')
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateVariableView, self).dispatch(*args, **kwargs)


class UpdateVariableView(UpdateView):

    model = Variable
    template_name = 'variable/edit_variable.html'

    def get_success_url(self):
        return reverse('surveys-view',
            kwargs={'pk': self.get_object().survey.id}
        )

    def get_context_data(self, **kwargs):

        context = super(UpdateVariableView, self).get_context_data(**kwargs)
        context['action'] = reverse('variables-edit',
                                    kwargs={'pk': self.get_object().id})
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateVariableView, self).dispatch(*args, **kwargs)


class DeleteVariableView(DeleteView):

    model = Variable
    template_name = 'variable/delete_variable.html'

    def get_success_url(self):
        return reverse('surveys-view',
            kwargs={'pk': self.survey_id}
        )

    def delete(self, request, *args, **kwargs):
        self.survey_id = self.get_object().survey.id
        return super(DeleteVariableView, self).delete(request, *args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteVariableView, self).dispatch(*args, **kwargs)


#Views for School
class ListSchoolView(ListView):

    model = School
    template_name = 'school/school_list.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListSchoolView, self).dispatch(*args, **kwargs)


class CreateSchoolView(CreateView):

    model = School
    template_name = 'school/edit_school.html'

    def get_success_url(self):
        return reverse('schools-list')

    def get_context_data(self, **kwargs):

        context = super(CreateSchoolView, self).get_context_data(**kwargs)
        context['action'] = reverse('schools-new')
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateSchoolView, self).dispatch(*args, **kwargs)


class UpdateSchoolView(UpdateView):

    model = School
    template_name = 'school/edit_school.html'

    def get_success_url(self):
        return reverse('schools-list')

    def get_context_data(self, **kwargs):

        context = super(UpdateSchoolView, self).get_context_data(**kwargs)
        context['action'] = reverse('schools-edit',
                                    kwargs={'pk': self.get_object().id})
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateSchoolView, self).dispatch(*args, **kwargs)


class DeleteSchoolView(DeleteView):

    model = School
    template_name = 'school/delete_school.html'

    def get_success_url(self):
        return reverse('schools-list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteSchoolView, self).dispatch(*args, **kwargs)


class SchoolView(DetailView):

    model = School
    template_name = 'school/school.html'

    def get_object(self, queryset=None):
        obj = School.objects.get(id=self.kwargs['pk'])
        return obj

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SchoolView, self).dispatch(*args, **kwargs)


#Views for Subject
class ListSubjectView(ListView):

    model = Subject
    template_name = 'subject/subject_list.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListSubjectView, self).dispatch(*args, **kwargs)


class CreateSubjectView(CreateView):

    model = Subject
    template_name = 'subject/edit_subject.html'

    def get_success_url(self):
        return reverse('subjects-list')

    def get_context_data(self, **kwargs):

        context = super(CreateSubjectView, self).get_context_data(**kwargs)
        context['action'] = reverse('subjects-new')
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateSubjectView, self).dispatch(*args, **kwargs)


class UpdateSubjectView(UpdateView):

    model = Subject
    template_name = 'subject/edit_subject.html'

    def get_success_url(self):
        return reverse('subjects-list')

    def get_context_data(self, **kwargs):

        context = super(UpdateSubjectView, self).get_context_data(**kwargs)
        context['action'] = reverse('subjects-edit',
                                    kwargs={'pk': self.get_object().id})
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateSubjectView, self).dispatch(*args, **kwargs)


class DeleteSubjectView(DeleteView):

    model = Subject
    template_name = 'subject/delete_subject.html'

    def get_success_url(self):
        return reverse('subjects-list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteSubjectView, self).dispatch(*args, **kwargs)


class SubjectView(DetailView):

    model = Subject
    template_name = 'subject/subject.html'

    def get_object(self, queryset=None):
        obj = Subject.objects.get(id=self.kwargs['pk'])
        return obj

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SubjectView, self).dispatch(*args, **kwargs)


# Views for School Participation Records
# Use a function to add a record to school
@login_required
def add_school_record(request, pk):
    # Read school ID from parsed pk
    school_id = pk
    school = School.objects.get(id=school_id)
    context = {}
    if request.method == 'POST':
        form = SchoolParticipationForm(request.POST)
        if form.is_valid():
            # Create a new record object
            p = SchoolParticipation()
            p.school = school
            p.survey = form.cleaned_data['survey']
            p.date_participated = form.cleaned_data['date_participated']
            p.legacy_school_short = form.cleaned_data['legacy_school_short']
            p.note = form.cleaned_data['note']
            p.save()
            return redirect('schools-view', pk=p.school.id)
    else:
        form = SchoolParticipationForm()
    context['form'] = form
    context['school'] = school
    context['action'] = reverse('schoolparticipations-new', kwargs={'pk': pk})
    return render_to_response('schoolparticipation/edit_schoolparticipation.html', context, context_instance=RequestContext(request))


class UpdateSchoolParticipationView(UpdateView):

    model = SchoolParticipation
    form_class = SchoolParticipationForm
    template_name = 'schoolparticipation/edit_schoolparticipation.html'

    def get_success_url(self):
        return reverse('schools-view', kwargs={'pk': self.get_object().school.id})

    def get_context_data(self, **kwargs):

        context = super(UpdateSchoolParticipationView, self).get_context_data(**kwargs)
        context['action'] = reverse('schoolparticipations-edit',
                                    kwargs={'pk': self.get_object().id})

        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateSchoolParticipationView, self).dispatch(*args, **kwargs)


class DeleteSchoolParticipationView(DeleteView):

    model = SchoolParticipation
    template_name = 'schoolparticipation/delete_schoolparticipation.html'

    def get_success_url(self):
        return reverse('schools-view', kwargs={'pk': self.school_id})

    def delete(self, request, *args, **kwargs):
        self.school_id = self.get_object().school.id
        return super(DeleteSchoolParticipationView, self).delete(request, *args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteSchoolParticipationView, self).dispatch(*args, **kwargs)


class SchoolParticipationView(DetailView):

    model = SchoolParticipation
    template_name = 'schoolparticipation/schoolparticipation.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SchoolParticipationView, self).dispatch(*args, **kwargs)


# Views for Teacher
class UpdateTeacherView(UpdateView):

    model = Teacher
    template_name = 'teacher/edit_teacher.html'

    def get_success_url(self):
        return reverse('schoolparticipations-view',
            kwargs={'pk': self.get_object().feedback_given_in.id},
        )

    def get_context_data(self, **kwargs):

        context = super(UpdateTeacherView, self).get_context_data(**kwargs)
        context['action'] = reverse('teachers-edit',
                                    kwargs={'pk': self.get_object().id})
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateTeacherView, self).dispatch(*args, **kwargs)

class DeleteTeacherView(DeleteView):

    model = Teacher
    template_name = 'teacher/delete_teacher.html'

    def get_success_url(self):
        return reverse('schoolparticipations-view',
            kwargs={'pk': self.schoolparticipation_id},
        )

    def delete(self, request, *args, **kwargs):
        self.schoolparticipation_id = self.get_object().feedback_given_in.id
        return super(DeleteTeacherView, self).delete(request, *args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteTeacherView, self).dispatch(*args, **kwargs)


class TeacherView(DetailView):

    model = Teacher
    template_name = 'teacher/teacher.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TeacherView, self).dispatch(*args, **kwargs)


# Views for Course
class UpdateCourseView(UpdateView):

    model = Course
    template_name = 'course/edit_course.html'

    def get_success_url(self):
        return reverse('teachers-view',
            kwargs={'pk': self.get_object().teacher_set.all()[0].id}
        )

    def get_context_data(self, **kwargs):

        context = super(UpdateCourseView, self).get_context_data(**kwargs)
        context['action'] = reverse('courses-edit',
                                    kwargs={'pk': self.get_object().id})
        return context


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateCourseView, self).dispatch(*args, **kwargs)


class DeleteCourseView(DeleteView):

    model = Course
    template_name = 'course/delete_course.html'

    def get_success_url(self):
        return reverse(
            'teachers-view',
            kwargs={'pk': self.teacher_id}
        )

    def delete(self, request, *args, **kwargs):
        primary_teacher = self.get_object().teacher_set.all()[0]
        self.teacher_id = primary_teacher.id
        return super(DeleteCourseView, self).delete(request, *args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteCourseView, self).dispatch(*args, **kwargs)


class CourseView(DetailView):

    model = Course
    template_name = 'course/course.html'

    def get_context_data(self, **kwargs):
        context = super(CourseView, self).get_context_data(**kwargs)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CourseView, self).dispatch(*args, **kwargs)


#Views for Survey
class SurveyView(DetailView):

    model = Survey
    template_name = 'survey/survey.html'

    def get_context_data(self, **kwargs):
        context = super(SurveyView, self).get_context_data(**kwargs)
        variables = self.get_object().variable_set.order_by('summary_measure', 'name')
        context['variables'] = variables
        recodes = CustomRecode.objects.filter(variable__in=variables)
        context['recodes'] = recodes.order_by('variable', 'orig_code')
        schools = self.get_object().school_set.distinct()
        context['schools'] = schools
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SurveyView, self).dispatch(*args, **kwargs)


# View functions for handling file uploads
@login_required
def upload_file(request, pk):
    # Read survey ID from parsed pk
    survey_id = pk
    survey = Survey.objects.get(id=survey_id)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Process the uploaded file
            newfile = request.FILES['file']
            file_type = request.POST['file_type']
            session_title = request.POST['title']
            # Process the uploaded data using a helper function in upload.py
            # Send this task to background
            # q.enqueue_call(
            #     func=process_uploaded,
            #     args=(newfile, file_type, survey, session_title),
            # )
            context = process_uploaded(newfile, file_type, survey, session_title)
            # Redirect to upload wait after POST
            return render_to_response('survey/upload_wait.html', context, context_instance=RequestContext(request))
    else:
        form = UploadFileForm()
    return render_to_response('survey/upload.html', {'form': form, 'survey': survey}, context_instance=RequestContext(request))


# View function for cleaning survey data
@login_required
def clean_survey(request, pk):
    # Read survey ID from parsed pk
    survey_id = pk
    survey = Survey.objects.get(id=survey_id)
    context = {}
    context['survey'] = survey
    if request.method == 'POST':
        # Delete courses below response rate cutoff
        courses_below_cutoff = survey.courses_below_cutoff()
        if len(courses_below_cutoff) > 0:
            for c in survey.courses_below_cutoff():
                c.delete()
            context['courses_deleted'] = 'Courses deleted from database.'

        # Delete orphaned teachers
        orphaned_teachers = survey.orphaned_teachers()
        if orphaned_teachers.count() > 0:
            orphaned_teachers.delete()
            context['teachers_deleted'] = 'Teachers deleted from database.'
    return render_to_response('survey/clean_survey.html', context, context_instance=RequestContext(request))


# View function for mapping variables from raw data to database
@login_required
def variable_map(request, pk):
    # Read survey ID from parsed pk
    survey_id = pk
    survey = Survey.objects.get(id=survey_id)
    context = {}
    context['survey'] = survey
    return render_to_response('varmap/variable_map.html', context, context_instance=RequestContext(request))


class UpdateVarMapView(UpdateView):

    model = VarMap
    form_class = VarMapForm
    template_name = 'varmap/edit_varmap.html'

    def get_success_url(self):
        return reverse(
            'surveys-view',
            kwargs={'pk': self.get_object().survey.id}
        )

    def get_context_data(self, **kwargs):

        context = super(UpdateVarMapView, self).get_context_data(**kwargs)
        context['action'] = reverse('varmap-edit',
                                    kwargs={'pk': self.get_object().id})
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateVarMapView, self).dispatch(*args, **kwargs)


class DeleteVarMapView(DeleteView):

    model = VarMap
    template_name = 'varmap/delete_varmap.html'

    def get_success_url(self):
        return reverse('surveys-view',
            kwargs={'pk': self.survey_id}
        )

    def delete(self, request, *args, **kwargs):
        self.survey_id = self.get_object().survey.id
        return super(DeleteVarMapView, self).delete(request, *args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteVarMapView, self).dispatch(*args, **kwargs)


# View function for mapping variables from raw data to database
# TODO Can probably remove this?
@login_required
def recode_view(request, pk):
    # Read survey ID from parsed pk
    survey_id = pk
    survey = Survey.objects.get(id=survey_id)
    context = {}
    context['survey'] = survey
    return render_to_response('recode/recode.html', context, context_instance=RequestContext(request))


class UpdateCustomRecodeView(UpdateView):

    model = CustomRecode
    form_class = CustomRecodeForm
    template_name = 'recode/edit_recode.html'

    def get_success_url(self):
        return reverse(
            'surveys-view',
            kwargs={'pk': self.get_object().variable.survey.id}
        )

    def get_context_data(self, **kwargs):

        context = super(UpdateCustomRecodeView, self).get_context_data(**kwargs)
        context['action'] = reverse('recode-edit',
                                    kwargs={'pk': self.get_object().id})
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateCustomRecodeView, self).dispatch(*args, **kwargs)


class DeleteCustomRecodeView(DeleteView):

    model = CustomRecode
    template_name = 'recode/delete_recode.html'

    def get_success_url(self):
        return reverse('surveys-view',
            kwargs={'pk': self.survey_id}
        )

    def delete(self, request, *args, **kwargs):
        self.survey_id = self.get_object().variable.survey.id
        return super(DeleteCustomRecodeView, self).delete(request, *args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteCustomRecodeView, self).dispatch(*args, **kwargs)


@login_required
def add_recode(request, pk):
    # Read survey ID from parsed pk
    survey_id = pk
    survey = Survey.objects.get(id=survey_id)
    context = {}
    context['survey'] = survey
    if request.method == 'POST':
        form = CustomRecodeForm(request.POST)
        if form.is_valid():
            # Create a new variable mapping object
            cr = CustomRecodeForm()
            cr.variable = form.cleaned_data['variable']
            cr.orig_code = form.cleaned_data['orig_code']
            cr.recode = form.cleaned_data['recode']
            cr.save()
            return redirect('surveys-view', pk=survey_id)
    else:
        form = CustomRecodeForm()
        # Filter for the variables available to this survey
        form.fields['variable'].queryset = Variable.objects.filter(survey=survey)
    context['form'] = form
    context['action'] = reverse('recode-add', kwargs={'pk': pk})
    return render_to_response('recode/edit_recode.html', context, context_instance=RequestContext(request))


@login_required
def add_var(request, pk):
    # Read survey ID from parsed pk
    survey_id = pk
    survey = Survey.objects.get(id=survey_id)
    context = {}
    context['survey'] = survey
    if request.method == 'POST':
        form = VarForm(request.POST)
        if form.is_valid():
            # Create a new variable mapping object
            v = Variable()
            v.survey = survey
            v.name = form.cleaned_data['name']
            v.description = form.cleaned_data['description']
            v.qual = form.cleaned_data['qual']
            v.summary_measure = form.cleaned_data['summary_measure']
            v.active = form.cleaned_data['active']
            v.save()
            return redirect('surveys-view', pk=survey_id)
    else:
        form = VarForm()
        # Filter for the variables available to this survey
        form.fields['summary_measure'].queryset = SummaryMeasure.objects.filter(survey=survey)
    context['form'] = form
    context['action'] = reverse('var-add', kwargs={'pk': pk})
    return render_to_response('variable/edit_variable.html', context, context_instance=RequestContext(request))


# Views for VarMap
@login_required
def add_varmap(request, pk):
    # Read survey ID from parsed pk
    survey_id = pk
    survey = Survey.objects.get(id=survey_id)
    context = {}
    context['survey'] = survey
    if request.method == 'POST':
        form = VarMapForm(request.POST)
        if form.is_valid():
            # Create a new variable mapping object
            v = VarMap()
            v.raw_name = form.cleaned_data['raw_name']
            v.variable = form.cleaned_data['variable']
            v.survey = survey
            v.save()
            return redirect('surveys-view', pk=survey_id)
    else:
        form = VarMapForm()
        # Filter for the variables available to this survey
        form.fields['variable'].queryset = Variable.objects.filter(survey=survey)
    context['form'] = form
    context['action'] = reverse('varmap-add', kwargs={'pk': pk})
    return render_to_response('varmap/edit_varmap.html', context, context_instance=RequestContext(request))


#Views for Import Session
class SessionView(DetailView):
    model = ImportSession
    template_name = 'session/session.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SessionView, self).dispatch(*args, **kwargs)


class ListSessionView(ListView):

    model = ImportSession
    template_name = 'session/session_list.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListSessionView, self).dispatch(*args, **kwargs)


class UpdateSessionView(UpdateView):

    model = ImportSession
    template_name = 'session/edit_session.html'

    def get_success_url(self):
        return reverse('sessions-list')

    def get_context_data(self, **kwargs):

        context = super(UpdateSessionView, self).get_context_data(**kwargs)
        context['action'] = reverse('sessions-edit',
                                    kwargs={'pk': self.get_object().id})
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateSessionView, self).dispatch(*args, **kwargs)


@login_required
def delete_session(request, pk):
    session = get_object_or_404(ImportSession, pk=pk)
    if request.method == 'POST':
        session.delete()
        return redirect('sessions-list')
    else:
        return render(request, 'session/delete_session.html', {'session': session})


# Export CSV Views
class ExportView(DetailView):
    model = CSVExport
    template_name = 'export/export.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ExportView, self).dispatch(*args, **kwargs)


class ListExportView(ListView):

    model = CSVExport
    template_name = 'export/export_list.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListExportView, self).dispatch(*args, **kwargs)


class UpdateExportView(UpdateView):

    model = CSVExport
    form_class = CSVExportForm
    template_name = 'export/edit_export.html'

    def get_success_url(self):
        return reverse('exports-list')

    def get_context_data(self, **kwargs):

        context = super(UpdateExportView, self).get_context_data(**kwargs)
        context['action'] = reverse('exports-edit',
                                    kwargs={'pk': self.get_object().id})
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateExportView, self).dispatch(*args, **kwargs)


@login_required
def delete_export(request, pk):
    export = get_object_or_404(CSVExport, pk=pk)
    if request.method == 'POST':
        # We'll also delete the file associated with this export at this time
        if default_storage.exists(export.file_name):
            default_storage.delete(export.file_name)
        export.delete()
        return redirect('exports-list')
    else:
        return render(request, 'export/delete_export.html', {'export': export})


@login_required
def export_wait(request, pk, qual=None):
    survey = get_object_or_404(Survey, pk=pk)

    # Enqueue this task for background processing
    if qual:
        # Create a CSVExport Session first
        export = create_csvexport(survey, 'Student Comments')
        q.enqueue(s3_write_response_data, survey, export, qual)
    else:
        # Create a CSVExport Session first
        export = create_csvexport(survey, 'Student Responses')
        q.enqueue(s3_write_response_data, survey, export)
    # s3_write_response_data(survey)
    return render(request, 'export/export_wait.html', {'survey_name': survey.name})
