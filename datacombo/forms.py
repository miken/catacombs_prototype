from django import forms


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
