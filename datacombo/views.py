import pandas as pd
import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.response import SimpleTemplateResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView

from datacombo.models import Variable, School, Survey, SchoolParticipation, ImportSession
from datacombo.forms import UploadFileForm
from datacombo.helpers import round_time_conversion



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

#View functions for handling file uploads
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            #Process the uploaded file
            uploaded_file = request.FILES['file']
            #Create context first to catch all message
            context = {}
            try:
                #Load it as a CSV file
                newcsv = pd.read_csv(uploaded_file)
            except pd._parser.CParserError:
                context['csv_file'] = False
            else:
                context['csv_file'] = True
                #Process the selected survey
                selected_survey_id = request.POST['survey']
                selected_survey = Survey.objects.get(id=selected_survey_id)
                #Get the list of variables for this survey
                selected_survey_varlist = selected_survey.variable_set.values_list('name', flat=True)
                #Get the list of schools for this survey
                selected_survey_schshort_list = selected_survey.school_set.values_list('short', flat=True)

                #Now turn attention back to newcsv
                tallies = newcsv.groupby(['School_Short', 'School_Name']).size()
                tallies.name = 'Number of Rows'
                tallies = tallies.reset_index()
                tallies = tallies.set_index('School_Short')
                csv_rowcount = len(newcsv)
                csv_collist = newcsv.columns.tolist()
                csv_schshort_list = newcsv['School_Short'].unique().tolist()
                #Compare the list of schools in CSV with list of schools in database to determine which new schools to add
                csv_schshorts_to_add = [s for s in csv_schshort_list if s not in selected_survey_schshort_list]
                number_of_new_schools = len(csv_schshorts_to_add)

                #Now create school objects for these schools
                #First, remember this import session
                session = ImportSession()
                session.title = request.POST['title']
                session.date_created = datetime.datetime.now()
                #If success, save this session
                session.save()

                csv_sch_object_list = []
                csv_schpart_object_list = []
                for schshort in csv_schshorts_to_add:
                    #Define school
                    sch_object = School()
                    sch_object.short = schshort
                    sch_object.name = tallies.get_value(schshort, 'School_Name')
                    sch_object.abbrev_name = schshort[:-3]
                    sch_object.imported_thru = session
                    sch_object.save()
                    csv_sch_object_list.append(sch_object)

                    #Define participation
                    schpart = SchoolParticipation()
                    round = schshort[-3:]
                    schpart.school = sch_object
                    schpart.survey = selected_survey
                    schpart.date_participated = round_time_conversion[round]
                    schpart.imported_thru = session
                    schpart.save()
                    csv_schpart_object_list.append(schpart)


                #Pare this list down for faster lookup
                csv_cols_in_db = [c for c in csv_collist if c in selected_survey_varlist]

                #Now create a dictionary with key as the variable name from selected_survey_varlist
                #and value as status of whether that variable exists in the CSV file
                var_status = {}
                for var in selected_survey_varlist:
                    if var in csv_cols_in_db:
                        var_status[var] = 1
                    else:
                        var_status[var] = 0

                #School List

                #Load all variables into the context for view rendering
                context['survey_name'] = selected_survey.name
                context['number_of_rows'] = csv_rowcount
                context['var_status_dict'] = var_status
                context['number_of_new_schools'] = number_of_new_schools
                context['sch_objects'] = csv_sch_object_list
                context['participation_objects'] = csv_schpart_object_list
                context['session_id'] = session.id
            #Redirect to upload summary after POST
            response = SimpleTemplateResponse('upload_confirm.html', context=context)
            return response
    else:
        form = UploadFileForm()
    return render_to_response('upload.html', {'form': form}, context_instance=RequestContext(request))


def delete_session(request, pk):
    session = get_object_or_404(ImportSession, pk=pk)
    if request.method == 'POST':
        session.delete()
        return HttpResponseRedirect(reverse('sessions-list'))
    else:
        #session = get_object_or_404(ImportSession, pk=pk)
        return render(request, 'delete_session.html', {'session': session})



#Views for Import Session
class ListSessionView(ListView):

    model = ImportSession
    template_name = 'session_list.html'


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