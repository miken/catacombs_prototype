from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.response import SimpleTemplateResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView

from datacombo.models import Variable, School, Survey
from datacombo.forms import UploadFileForm

import pandas as pd


#Index View
class HomeView(TemplateView):

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['all_surveys'] = Survey.objects.all()
        return context


#Views for Variable
class ListVariableView(ListView):

    model = Variable
    template_name = 'variable_list.html'


class CreateVariableView(CreateView):

    model = Variable
    template_name = 'edit_variable.html'

    def get_success_url(self):
        return reverse('variables-list')

    def get_context_data(self, **kwargs):

        context = super(CreateVariableView, self).get_context_data(**kwargs)
        context['action'] = reverse('variables-new')

        return context


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


class DeleteVariableView(DeleteView):

    model = Variable
    template_name = 'delete_variable.html'

    def get_success_url(self):
        return reverse('variables-list')

#Views for School
class ListSchoolView(ListView):

    model = School
    template_name = 'school_list.html'


class CreateSchoolView(CreateView):

    model = School
    template_name = 'edit_school.html'

    def get_success_url(self):
        return reverse('schools-list')

    def get_context_data(self, **kwargs):

        context = super(CreateSchoolView, self).get_context_data(**kwargs)
        context['action'] = reverse('schools-new')

        return context


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


class DeleteSchoolView(DeleteView):

    model = School
    template_name = 'delete_school.html'

    def get_success_url(self):
        return reverse('schools-list')


#Views for Survey
class ListSurveyView(ListView):

    model = Survey
    template_name = 'survey_list.html'


class CreateSurveyView(CreateView):

    model = Survey
    template_name = 'edit_survey.html'

    def get_success_url(self):
        return reverse('surveys-list')

    def get_context_data(self, **kwargs):

        context = super(CreateSurveyView, self).get_context_data(**kwargs)
        context['action'] = reverse('surveys-new')

        return context


class UpdateSurveyView(UpdateView):

    model = Survey
    template_name = 'edit_survey.html'

    def get_success_url(self):
        return reverse('surveys-list')

    def get_context_data(self, **kwargs):

        context = super(UpdateSurveyView, self).get_context_data(**kwargs)
        context['action'] = reverse('surveys-edit',
                                    kwargs={'pk': self.get_object().id})

        return context


class DeleteSurveyView(DeleteView):

    model = Survey
    template_name = 'delete_survey.html'

    def get_success_url(self):
        return reverse('surveys-list')


class UploadSurveyView(UpdateView):

    model = Survey
    template_name = 'update_survey.html'

    def get_success_url(self):
        return reverse('home-view')

    def get_context_data(self, **kwargs):
        context = super(UploadSurveyView, self).get_context_data(**kwargs)
        context['action'] = reverse('surveys-upload',
                                    kwargs={'pk': self.get_object().id})

        return context


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            #Do something with uploaded_file
            newcsv = pd.read_csv(uploaded_file)
            number_of_rows = len(newcsv)
            col_list = newcsv.columns.tolist()
            context = {}
            context['number_of_rows'] = number_of_rows
            context['col_list'] = col_list
            #Redirect to upload summary after POST
            response = SimpleTemplateResponse('upload_summary.html', context=context)
            return response
    else:
        form = UploadFileForm()
    return render_to_response('upload.html',
                              {'form': form},
                              context_instance=RequestContext(request))
