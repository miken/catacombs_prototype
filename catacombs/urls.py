from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import datacombo.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', datacombo.views.home_or_login, name='root'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login-view'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
    url(r'^home/$', datacombo.views.HomeView.as_view(), name='home-view'),
    url(r'^upload/$', datacombo.views.upload_file, name='upload'),

    # ===== SURVEY WORK =====
    # Surveys can only be added, edited, or deleted via the admin interface
    url(r'^surveys/(?P<pk>\d+)/$', datacombo.views.SurveyView.as_view(), name='surveys-view',),
    # Upload new CSV data to survey
    url(r'^surveys/(?P<pk>\d+)/upload$', datacombo.views.upload_file, name='surveys-upload',),
    # Clean school / course records below reporting thresholds
    url(r'^surveys/(?P<pk>\d+)/clean$', datacombo.views.clean_survey, name='surveys-clean',),
    # Variable Mapping
    url(r'^surveys/(?P<pk>\d+)/map$', datacombo.views.variable_map, name='surveys-map',),
    # Add a new variable to survey
    url(r'^surveys/(?P<pk>\d+)/vars/add$', datacombo.views.add_var, name='var-add',),
    # Add a new variable map
    url(r'^surveys/(?P<pk>\d+)/map/add$', datacombo.views.add_varmap, name='varmap-add',),
    # Edit a variable map
    url(r'^vars/maps/(?P<pk>\d+)/$', datacombo.views.UpdateVarMapView.as_view(), name='varmap-edit',),
    # Delete a variable map
    url(r'^vars/maps/(?P<pk>\d+)/delete$', datacombo.views.DeleteVarMapView.as_view(), name='varmap-delete',),
    # Variables
    url(r'^vars/$', datacombo.views.ListVariableView.as_view(), name='variables-list',),
    url(r'^vars/new$', datacombo.views.CreateVariableView.as_view(), name='variables-new',),
    url(r'^vars/edit/(?P<pk>\d+)/$', datacombo.views.UpdateVariableView.as_view(),
        name='variables-edit',),
    url(r'^vars/delete/(?P<pk>\d+)/$', datacombo.views.DeleteVariableView.as_view(),
        name='variables-delete',),

    # Schools
    url(r'^schools/$', datacombo.views.ListSchoolView.as_view(), name='schools-list',),
    url(r'^schools/new$', datacombo.views.CreateSchoolView.as_view(), name='schools-new',),
    url(r'^schools/edit/(?P<pk>\d+)/$', datacombo.views.UpdateSchoolView.as_view(),
        name='schools-edit',),
    url(r'^schools/delete/(?P<pk>\d+)/$', datacombo.views.DeleteSchoolView.as_view(),
        name='schools-delete',),
    url(r'^schools/(?P<pk>\d+)/$', datacombo.views.SchoolView.as_view(),
        name='schools-view',),

    # School Participations
    # Creating new school participations record is not ready yet
    url(r'^schools/(?P<pk>\d+)/records/new$', datacombo.views.add_school_record, name='schoolparticipations-new',),
    url(r'^schools/records/edit/(?P<pk>\d+)/$', datacombo.views.UpdateSchoolParticipationView.as_view(),
        name='schoolparticipations-edit',),
    url(r'^schools/records/delete/(?P<pk>\d+)/$', datacombo.views.DeleteSchoolParticipationView.as_view(),
        name='schoolparticipations-delete',),
    url(r'^schools/records/(?P<pk>\d+)/$', datacombo.views.SchoolParticipationView.as_view(),
        name='schoolparticipations-view',),

    # Teachers
    #url(r'^teachers/$', datacombo.views.ListTeacherView.as_view(), name='teachers-list',),
    #url(r'^teachers/new$', datacombo.views.CreateTeacherView.as_view(), name='teachers-new',),
    url(r'^teachers/edit/(?P<pk>\d+)/$', datacombo.views.UpdateTeacherView.as_view(), name='teachers-edit',),
    url(r'^teachers/delete/(?P<pk>\d+)/$', datacombo.views.DeleteTeacherView.as_view(), name='teachers-delete',),
    url(r'^teachers/(?P<pk>\d+)/$', datacombo.views.TeacherView.as_view(),
        name='teachers-view',),

    # Subjects
    url(r'^subjects/$', datacombo.views.ListSubjectView.as_view(), name='subjects-list',),
    url(r'^subjects/new$', datacombo.views.CreateSubjectView.as_view(), name='subjects-new',),
    url(r'^subjects/edit/(?P<pk>\d+)/$', datacombo.views.UpdateSubjectView.as_view(),
        name='subjects-edit',),
    url(r'^subjects/delete/(?P<pk>\d+)/$', datacombo.views.DeleteSubjectView.as_view(),
        name='subjects-delete',),
    url(r'^subjects/(?P<pk>\d+)/$', datacombo.views.SubjectView.as_view(),
        name='subjects-view',),

    # Courses
    url(r'^courses/edit/(?P<pk>\d+)/$', datacombo.views.UpdateCourseView.as_view(), name='courses-edit',),
    url(r'^courses/delete/(?P<pk>\d+)/$', datacombo.views.DeleteCourseView.as_view(), name='courses-delete',),
    url(r'^courses/(?P<pk>\d+)/$', datacombo.views.CourseView.as_view(), name='courses-view',),

    #Import Sessions
    url(r'^sessions/$', datacombo.views.ListSessionView.as_view(), name='sessions-list',),
    url(r'^sessions/edit/(?P<pk>\d+)/$', datacombo.views.UpdateSessionView.as_view(),
        name='sessions-edit',),
    url(r'^sessions/delete/(?P<pk>\d+)/$', datacombo.views.delete_session,
        name='sessions-delete',),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # Django-RQ
    url(r'^django-rq/', include('django_rq.urls')),
)

urlpatterns += staticfiles_urlpatterns()
