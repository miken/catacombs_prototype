from django import forms

from datacombo.models import Survey


def get_survey_list():
    all_surveys = Survey.objects.all()
    survey_list = []
    for s in all_surveys:
        survey_list.append((s.id, s.name))
    return survey_list


class UploadFileForm(forms.Form):
    survey_list = get_survey_list()
    survey = forms.ChoiceField(choices=survey_list)
    file = forms.FileField()
