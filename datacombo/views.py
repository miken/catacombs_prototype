import pandas as pd
import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.response import SimpleTemplateResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView

from datacombo.models import Variable, School, Survey, SchoolParticipation, ImportSession, Response, Student
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


class SchoolView(DetailView):

    model = School
    template_name = 'school.html'



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


class SurveyView(DetailView):

    model = Survey
    template_name = 'survey.html'


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
                # Process the selected survey
                survey_id = request.POST['survey']
                survey = Survey.objects.get(id=survey_id)
                # Get the list of variables for this survey
                survey_alphalist = survey.school_set.values_list('alpha', flat=True)

                # Create new import session first
                # First, remember this import session
                session = ImportSession()
                session.title = request.POST['title']
                session.date_created = datetime.datetime.now()
                session.save()

                # Tallies of new objects
                number_of_new_schools = 0
                number_of_new_participations = 0
                number_of_new_students = 0
                number_of_rows = 0

                # List of objects for bulk creation later
                new_schools_list = []
                new_records_list = []
                new_students_list = []
                new_responses_list = []

                # Create a few aggregate dataframe for lookup use later:
                tallies = newcsv.groupby(['School_Short', 'School_Name']).size()
                tallies = tallies.reset_index()
                surveycode = survey.alpha_suffix()
                tallies['abbr'] = tallies['School_Short'].str[:-3]
                tallies['alpha'] = tallies['abbr'] + '-' + surveycode
                tallies = tallies.set_index('School_Short')
                # Create a record of unique triples of PIN, ID and School_Short
                csv_pin = newcsv.groupby(['PIN', 'ID', 'School_Short']).size()
                csv_pin = csv_pin.reset_index()
                # Set PIN as index for faster lookup
                csv_pin = csv_pin.set_index('PIN')
                csv_columns = newcsv.columns.tolist()

                # Create/update schools
                for a in tallies['alpha']:
                    if a in survey_alphalist:
                        pass
                    else:
                        series = tallies[tallies['alpha'] == a]
                        sch_obj = School()
                        sch_obj.abbrev_name = series['abbr'][0]
                        sch_obj.name = series['School_Name'][0]
                        sch_obj.alpha = a
                        sch_obj.imported_thru = session
                        # Append to object list for bulk create later
                        new_schools_list.append(sch_obj)
                        # Add up the tallies
                        number_of_new_schools += 1
                # Bulk create new school objects
                School.objects.bulk_create(new_schools_list)


                # Create/update school participation records
                survey_record_list = survey.schoolparticipation_set.values('legacy_school_short', 'id')
                survey_record_dict = {}
                for valdict in survey_record_list:
                    ss = valdict['legacy_school_short']
                    i = valdict['id']
                    survey_record_dict[ss] = i
                # Get a new set of school records for lookup
                survey_new_sch_list = School.objects.values('abbrev_name', 'id')
                survey_new_sch_dict = {}
                for valdict in survey_new_sch_list:
                    abbr = valdict['abbrev_name']
                    i = valdict['id']
                    survey_new_sch_dict[abbr] = i
                for s in tallies.index:
                    if s in survey_record_dict.keys():
                        pass
                    else:
                        pr_obj = SchoolParticipation()
                        abbr = tallies.get_value(s, 'abbr')
                        pr_obj.school_id = survey_new_sch_dict[abbr]
                        pr_obj.survey = survey
                        survey_round = s[-3:]
                        pr_obj.date_participated = round_time_conversion[survey_round]
                        pr_obj.legacy_school_short = s
                        pr_obj.note = 'Imported on {}'.format(session.date_created)
                        pr_obj.imported_thru = session
                        number_of_new_participations += 1
                        # Append to object list for bulk create later
                        new_records_list.append(pr_obj)
                        # Add up the tallies
                        number_of_new_participations += 1
                #Bulk create new participation objects
                SchoolParticipation.objects.bulk_create(new_records_list)

                # Create/update teacher records

                # Create/update course records

                # Create/update student records
                survey_students = Student.objects.filter(surveyed_in_id__in=survey_record_dict.values())
                survey_student_pin_list = survey_students.values_list('pin', flat=True)
                # Get a new set of participation records for lookup too
                survey_new_pr_list = survey.schoolparticipation_set.values('legacy_school_short', 'id', 'school')
                survey_new_pr_dict = {}
                for valdict in survey_new_pr_list:
                    ss = valdict['legacy_school_short']
                    i = valdict['id']
                    sch_id = valdict['school']
                    survey_new_pr_dict[ss] = (i, sch_id)
                for p in csv_pin.index:
                    if p in survey_student_pin_list:
                        pass
                    else:
                        std_obj = Student()
                        std_obj.pin = p
                        std_obj.response_id = csv_pin.get_value(p, 'ID')
                        #Blank for now
                        #std_obj.course
                        #std_obj.teacher
                        schshort = csv_pin.get_value(p, 'School_Short')
                        std_obj.surveyed_in_id = survey_new_pr_dict[schshort][0]
                        std_obj.imported_thru = session
                        # Append to object list for bulk create later
                        new_students_list.append(std_obj)
                        # Add up the tallies
                        number_of_new_students += 1
                # Bulk create new student objects
                Student.objects.bulk_create(new_students_list)

                # Create/update response records
                survey_varlist = survey.variable_set.values('name', 'id')
                survey_vardict = {}
                for valdict in survey_varlist:
                    varname = valdict['name']
                    varid = valdict['id']
                    survey_vardict[varname] = varid
                # Get new set of student records for lookup too
                survey_new_pr_id_list = [tpl[1] for tpl in survey_new_pr_dict.values()]
                survey_new_std = Student.objects.filter(surveyed_in_id__in=survey_new_pr_id_list)
                survey_new_std_list = survey_new_std.values('pin', 'id')
                survey_new_std_dict = {}
                for valdict in survey_new_std_list:
                    pin = valdict['pin']
                    i = valdict['id']
                    survey_new_std_dict[pin] = i

                # Now create a dictionary with key as the variable name from survey_varlist
                # and value as status of whether that variable exists in the CSV file
                var_status = {}
                for var in survey_vardict.keys():
                    if var in csv_columns:
                        var_status[var] = 1
                    else:
                        var_status[var] = 0
                    for i in newcsv.index:
                        row = newcsv.ix[i]
                        a = row[var]
                        if pd.isnull(a):
                            pass
                        else:
                            resp = Response()
                            resp.question_id = survey_vardict[var]
                            resp.survey = survey
                            resp.answer = a
                            pin = row['PIN']
                            resp.student_id = survey_new_std_dict[pin]
                            # resp.on_course = cse_obj
                            # Assign response to school
                            schshort = csv_pin.get_value(pin, 'School_Short')
                            resp.on_school_id = survey_new_pr_dict[schshort][1]
                            resp.imported_thru = session
                            # Append to object list for bulk create later
                            new_responses_list.append(resp)
                            # Add up the tallies
                            number_of_rows += 1
                        # If the list of responses reach 500, we'll do bulk create and reset the list
                        if len(new_responses_list) == 500:
                            Response.objects.bulk_create(new_responses_list)
                            new_responses_list = []
                # Bulk create new response objects
                Response.objects.bulk_create(new_responses_list)
                new_responses_list = []

                # Load all variables into the context for view rendering
                context['survey_name'] = survey.name
                context['number_of_rows'] = number_of_rows
                context['var_status_dict'] = var_status
                context['number_of_new_schools'] = number_of_new_schools
                context['number_of_new_participations'] = number_of_new_participations
                context['number_of_new_students'] = number_of_new_students
                context['sch_objects'] = School.objects.filter(imported_thru=session)
                context['participation_objects'] = SchoolParticipation.objects.filter(imported_thru=session)
                context['session_id'] = session.id
            # Redirect to upload summary after POST
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