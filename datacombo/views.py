import csv
import StringIO
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

            # Guessing file encoding - taken from here:
            #http://jazstudios.blogspot.it/2011/11/python-detect-charset-and-convert-to.html
            content = uploaded_file.read()

            # Unicode detection disabled for now
            #encoding = chardet.detect(content)['encoding']
            #if encoding != 'utf-8':
            #    content = content.decode(encoding, 'replace').encode('utf-8')

            filestream = StringIO.StringIO(content)
            dialect = csv.Sniffer().sniff(content)

            #Create context first to catch all message
            context = {}
            try:
                #Load it as a CSV file
                newcsv = csv.DictReader(filestream.read().splitlines(), dialect=dialect)
            except csv.Error:
                context['csv_file'] = False
            else:
                context['csv_file'] = True
                # Process the selected survey
                selected_survey_id = request.POST['survey']
                selected_survey = Survey.objects.get(id=selected_survey_id)
                # Get the list of variables for this survey
                selected_survey_varlist = selected_survey.variable_set.values_list('name', flat=True)

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

                # List of objects for view rendering later
                new_school_id_list = []
                new_record_id_list = []

                #Start parsing:
                for row in newcsv:
                    # Create/update school
                    schshort = row['School_Short']
                    abbr = schshort[:-3]
                    alpha = '{abbr}-{surveycode}'.format(abbr=abbr, surveycode=selected_survey.alpha_suffix())

                    try:
                        sch_obj = selected_survey.school_set.get(alpha=alpha)
                    except School.DoesNotExist:
                        #If a school does not exist yet, create and then assign it to pr
                        sch_obj = School()
                        sch_obj.abbrev_name = schshort[:-3]
                        sch_obj.name = row['School_Name']
                        sch_obj.alpha = alpha
                        sch_obj.imported_thru = session
                        sch_obj.save()
                        number_of_new_schools += 1
                        new_school_id_list.append(sch_obj.id)

                    # Create/update participation record
                    try:
                        pr = selected_survey.schoolparticipation_set.get(id=sch_obj.id)
                    except SchoolParticipation.DoesNotExist:
                        #If a record does not exist yet, create
                        pr = SchoolParticipation()
                        pr.school = sch_obj
                        pr.survey = selected_survey
                        survey_round = schshort[-3:]
                        pr.date_participated = round_time_conversion[survey_round]
                        pr.legacy_school_short = schshort
                        pr.note = 'Imported on {}'.format(session.date_created)
                        pr.imported_thru = session
                        pr.save()
                        number_of_new_participations += 1
                        new_record_id_list.append(pr.id)
                    # Create/update teacher
                    #
                    # Create/update course
                    #
                    # Create/update student
                    pin = row['PIN']
                    try:
                        std_obj = pr.student_set.get(pin=pin)
                    except Student.DoesNotExist:
                        #If a student does not exist, create and then assign to resp
                        std_obj = Student()
                        std_obj.pin = pin
                        std_obj.response_id = row['ID']
                        #Blank for now
                        #std_obj.course
                        #std_obj.teacher
                        std_obj.surveyed_in = pr
                        std_obj.imported_thru = session
                        std_obj.save()
                        number_of_new_students += 1

                    # Create/update response
                    for var in selected_survey_varlist:
                        # If there's no response for that question, skip it
                        answer = row[var]
                        if answer == '':
                            pass
                        else:
                            answer = int(answer)
                            var_obj = selected_survey.variable_set.get(name=var)
                            resp = Response()
                            resp.question = var_obj
                            resp.survey = selected_survey
                            resp.answer = answer
                            resp.student = std_obj
                            # resp.on_course = cse_obj
                            # Assign response to school
                            resp.on_school = sch_obj
                            resp.imported_thru = session
                            resp.save()

                    # Number of rows
                    number_of_rows += 1


                # List of objects for view rendering later
                new_schools_list = list(School.objects.filter(id__in=new_school_id_list))
                new_records_list = list(SchoolParticipation.objects.filter(id__in=new_record_id_list))

                #Pare this list down for faster lookup
                csv_collist = newcsv.fieldnames
                csv_cols_in_db = [c for c in csv_collist if c in selected_survey_varlist]

                #Now create a dictionary with key as the variable name from selected_survey_varlist
                #and value as status of whether that variable exists in the CSV file
                var_status = {}
                for var in selected_survey_varlist:
                    if var in csv_cols_in_db:
                        var_status[var] = 1
                    else:
                        var_status[var] = 0

                #Load all variables into the context for view rendering
                context['survey_name'] = selected_survey.name
                context['number_of_rows'] = number_of_rows
                context['var_status_dict'] = var_status
                context['number_of_new_schools'] = number_of_new_schools
                context['number_of_new_participations'] = number_of_new_participations
                context['number_of_new_students'] = number_of_new_students
                context['sch_objects'] = new_schools_list
                context['participation_objects'] = new_records_list
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