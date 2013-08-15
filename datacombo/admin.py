from django.contrib import admin
from datacombo.models import Survey, School, SchoolParticipation, Variable


class VariableInline(admin.TabularInline):
    model = Variable
    extra = 1


class SurveyAdmin(admin.ModelAdmin):
    fields = ['name', 'code']
    inlines = [VariableInline]

admin.site.register(Survey, SurveyAdmin)


class SchoolParticipationAdmin(admin.ModelAdmin):
    fields = ['school', 'survey', 'date_participated', 'note']
    list_display = ('school', 'survey', 'date_participated', 'note')

admin.site.register(SchoolParticipation, SchoolParticipationAdmin)


class SchoolAdmin(admin.ModelAdmin):
    fields = ['name', 'abbrev_name', 'short', 'q_code']

admin.site.register(School, SchoolAdmin)
