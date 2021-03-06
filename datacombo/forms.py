from django import forms

from datacombo.models import SchoolParticipation, Variable, VarMap, CSVExport, CustomRecode


class UploadFileForm(forms.Form):
    required_css_class = 'alert alert-danger'

    title = forms.CharField(max_length=100)
    file = forms.FileField()
    file_type_choices = (
        ('panel', 'Qualtrics Panel'),
        ('raw', 'Qualtrics Raw Export'),
        ('legacy', 'Legacy Data'),
    )
    file_type = forms.ChoiceField(choices=file_type_choices)


class SchoolParticipationForm(forms.ModelForm):
    class Meta:
        model = SchoolParticipation
        fields = ['survey', 'date_participated', 'legacy_school_short', 'note']


class VarMapForm(forms.ModelForm):
    class Meta:
        model = VarMap
        fields = ['raw_name', 'variable']


class CustomRecodeForm(forms.ModelForm):
    class Meta:
        model = CustomRecode
        fields = ['variable', 'orig_code', 'recode']


class VarForm(forms.ModelForm):
    class Meta:
        model = Variable
        fields = ['name', 'description', 'qual', 'summary_measure', 'active']


class CSVExportForm(forms.ModelForm):
    class Meta:
        model = CSVExport
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'size': 100, 'maxlength': 100})
        }
