from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.response import SimpleTemplateResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView

from datacombo.models import Variable, School, Survey, ImportSession, SchoolParticipation, Teacher, Subject, Course
from datacombo.forms import UploadFileForm, SchoolParticipationForm
from datacombo.upload import process_uploaded


#Index View
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
    template_name = 'variable_list.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListVariableView, self).dispatch(*args, **kwargs)


class CreateVariableView(CreateView):

    model = Variable
    template_name = 'edit_variable.html'

    def get_success_url(self):
        return reverse('variables-list')

    def get_context_data(self, **kwargs):

        context = super(CreateVariableView, self).get_context_data(**kwargs)
        context['action'] = reverse('variables-new')
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateVariableView, self).dispatch(*args, **kwargs)


class UpdateVariableView(UpdateView):

    model = Variable
    template_name = 'edit_variable.html'

    def get_success_url(self):
        return reverse('variables-list')

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
    template_name = 'delete_variable.html'

    def get_success_url(self):
        return reverse('variables-list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteVariableView, self).dispatch(*args, **kwargs)


#Views for School
class ListSchoolView(ListView):

    model = School
    template_name = 'school_list.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListSchoolView, self).dispatch(*args, **kwargs)


class CreateSchoolView(CreateView):

    model = School
    template_name = 'edit_school.html'

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
    template_name = 'edit_school.html'

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
    template_name = 'delete_school.html'

    def get_success_url(self):
        return reverse('schools-list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteSchoolView, self).dispatch(*args, **kwargs)


class SchoolView(DetailView):

    model = School
    template_name = 'school.html'

    def get_object(self, queryset=None):
        obj = School.objects.get(id=self.kwargs['pk'])
        return obj

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SchoolView, self).dispatch(*args, **kwargs)


#Views for Subject
class ListSubjectView(ListView):

    model = Subject
    template_name = 'subject_list.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListSubjectView, self).dispatch(*args, **kwargs)


class CreateSubjectView(CreateView):

    model = Subject
    template_name = 'edit_subject.html'

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
    template_name = 'edit_subject.html'

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
    template_name = 'delete_subject.html'

    def get_success_url(self):
        return reverse('subjects-list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteSubjectView, self).dispatch(*args, **kwargs)


class SubjectView(DetailView):

    model = Subject
    template_name = 'subject.html'

    def get_object(self, queryset=None):
        obj = Subject.objects.get(id=self.kwargs['pk'])
        return obj

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SubjectView, self).dispatch(*args, **kwargs)


# Views for School Participation Records

# TODO Figure how to wire new school participation record with school later
class CreateSchoolParticipationView(CreateView):

    model = SchoolParticipation
    form_class = SchoolParticipationForm
    template_name = 'edit_schoolparticipation.html'

    def get_success_url(self):
        return reverse('schools-view',
                       kwargs={'pk': self.get_object().school.id})

    def get_context_data(self, **kwargs):

        context = super(CreateSchoolParticipationView, self).get_context_data(**kwargs)
        context['action'] = reverse('schoolparticipations-new', kwargs={'pk': self.get_object().id})
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateSchoolParticipationView, self).dispatch(*args, **kwargs)


class UpdateSchoolParticipationView(UpdateView):

    model = SchoolParticipation
    form_class = SchoolParticipationForm
    template_name = 'edit_schoolparticipation.html'

    def get_success_url(self):
        return reverse('schools-view',
                       kwargs={'pk': self.get_object().school.id})

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
    template_name = 'delete_schoolparticipation.html'

    def get_success_url(self):
        return reverse('schools-list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteSchoolParticipationView, self).dispatch(*args, **kwargs)


class SchoolParticipationView(DetailView):

    model = SchoolParticipation
    template_name = 'schoolparticipation.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SchoolParticipationView, self).dispatch(*args, **kwargs)


# Views for Teacher
class UpdateTeacherView(UpdateView):

    model = Teacher
    template_name = 'edit_teacher.html'

    def get_success_url(self):
        return reverse('teachers-list')

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
    template_name = 'delete_teacher.html'

    def get_success_url(self):
        return reverse('teachers-list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteTeacherView, self).dispatch(*args, **kwargs)


class TeacherView(DetailView):

    model = Teacher
    template_name = 'teacher.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TeacherView, self).dispatch(*args, **kwargs)

# Views for Course
class CourseView(DetailView):

    model = Course
    template_name = 'course.html'

    def get_context_data(self, **kwargs):
        context = super(CourseView, self).get_context_data(**kwargs)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CourseView, self).dispatch(*args, **kwargs)



#Views for Survey
class ListSurveyView(ListView):

    model = Survey
    template_name = 'survey_list.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListSurveyView, self).dispatch(*args, **kwargs)


class CreateSurveyView(CreateView):

    model = Survey
    template_name = 'edit_survey.html'

    def get_success_url(self):
        return reverse('surveys-list')

    def get_context_data(self, **kwargs):

        context = super(CreateSurveyView, self).get_context_data(**kwargs)
        context['action'] = reverse('surveys-new')
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateSurveyView, self).dispatch(*args, **kwargs)


class UpdateSurveyView(UpdateView):

    model = Survey
    template_name = 'update_survey.html'

    def get_success_url(self):
        return reverse('surveys-list')

    def get_context_data(self, **kwargs):
        context = super(UpdateSurveyView, self).get_context_data(**kwargs)
        context['action'] = reverse('surveys-list',
                                    kwargs={'pk': self.get_object().id})
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateSurveyView, self).dispatch(*args, **kwargs)


class DeleteSurveyView(DeleteView):

    model = Survey
    template_name = 'delete_survey.html'

    def get_success_url(self):
        return reverse('surveys-list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteSurveyView, self).dispatch(*args, **kwargs)

class SurveyView(DetailView):

    model = Survey
    template_name = 'survey.html'

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
            context = process_uploaded(newfile, file_type, survey, session_title)
            # Redirect to upload summary after POST
            response = SimpleTemplateResponse('upload_confirm.html', context=context)
            return response
    else:
        form = UploadFileForm()
    return render_to_response('upload.html', {'form': form, 'survey': survey}, context_instance=RequestContext(request))

@login_required
def delete_session(request, pk):
    session = get_object_or_404(ImportSession, pk=pk)
    if request.method == 'POST':
        session.delete()
        return HttpResponseRedirect(reverse('sessions-list'))
    else:
        return render(request, 'delete_session.html', {'session': session})


# View functions for cleaning survey data
@login_required
def clean_survey(request, pk):
    # Read survey ID from parsed pk
    survey_id = pk
    survey = Survey.objects.get(id=survey_id)
    return render_to_response('clean_survey.html', {'survey': survey}, context_instance=RequestContext(request))


#Views for Import Session
class ListSessionView(ListView):

    model = ImportSession
    template_name = 'session_list.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListSessionView, self).dispatch(*args, **kwargs)


class UpdateSessionView(UpdateView):

    model = ImportSession
    template_name = 'edit_session.html'

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