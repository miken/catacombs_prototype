from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import datacombo.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', datacombo.views.HomeView.as_view(), name='home-view'),
    url(r'^upload/$', datacombo.views.upload_file, name='upload'),

    #Variables
    url(r'^vars/$', datacombo.views.ListVariableView.as_view(), name='variables-list',),
    url(r'^vars/new$', datacombo.views.CreateVariableView.as_view(), name='variables-new',),
    url(r'^vars/edit/(?P<pk>\d+)/$', datacombo.views.UpdateVariableView.as_view(),
        name='variables-edit',),
    url(r'^vars/delete/(?P<pk>\d+)/$', datacombo.views.DeleteVariableView.as_view(),
        name='variables-delete',),

    #Schools
    url(r'^schools/$', datacombo.views.ListSchoolView.as_view(), name='schools-list',),
    url(r'^schools/new$', datacombo.views.CreateSchoolView.as_view(), name='schools-new',),
    url(r'^schools/edit/(?P<pk>\d+)/$', datacombo.views.UpdateSchoolView.as_view(),
        name='schools-edit',),
    url(r'^schools/delete/(?P<pk>\d+)/$', datacombo.views.DeleteSchoolView.as_view(),
        name='schools-delete',),
    url(r'^schools/(?P<pk>\d+)/$', datacombo.views.SchoolView.as_view(),
        name='schools-view',),

    #Surveys - We're gonna disable this for now
    #url(r'^surveys/$', datacombo.views.ListSurveyView.as_view(), name='surveys-list',),
    #url(r'^surveys/new$', datacombo.views.CreateSurveyView.as_view(), name='surveys-new',),
    #url(r'^surveys/edit/(?P<pk>\d+)/$', datacombo.views.UpdateSurveyView.as_view(), name='surveys-edit',),
    #url(r'^surveys/delete/(?P<pk>\d+)/$', datacombo.views.DeleteSurveyView.as_view(), name='surveys-delete',),
    url(r'^surveys/(?P<pk>\d+)/upload$', datacombo.views.upload_file,
        name='surveys-upload',),
    url(r'^surveys/(?P<pk>\d+)/$', datacombo.views.SurveyView.as_view(),
        name='surveys-view',),

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
)

urlpatterns += staticfiles_urlpatterns()
