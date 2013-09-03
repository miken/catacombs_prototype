from django.contrib import admin
from datacombo.models import Survey, School, SchoolParticipation, Variable, VarMap


class VariableInline(admin.TabularInline):
    model = Variable
    extra = 1


class VarMapInline(admin.TabularInline):
	model = VarMap
	extra = 1


class SurveyAdmin(admin.ModelAdmin):
    fields = ['name', 'code']
    inlines = [VariableInline, VarMapInline]

admin.site.register(Survey, SurveyAdmin)


class SchoolParticipationAdmin(admin.ModelAdmin):
    fields = ['school', 'survey', 'date_participated', 'note']
    list_display = ('school', 'survey', 'date_participated', 'note')

admin.site.register(SchoolParticipation, SchoolParticipationAdmin)


class SchoolAdmin(admin.ModelAdmin):
    fields = ['name', 'abbrev_name', 'alpha', 'q_code']

admin.site.register(School, SchoolAdmin)
