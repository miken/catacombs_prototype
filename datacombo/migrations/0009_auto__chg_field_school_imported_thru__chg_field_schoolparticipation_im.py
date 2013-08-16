# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'School.imported_thru'
        db.alter_column(u'datacombo_school', 'imported_thru_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.ImportSession'], null=True, on_delete=models.SET_NULL))

        # Changing field 'SchoolParticipation.imported_thru'
        db.alter_column(u'datacombo_schoolparticipation', 'imported_thru_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.ImportSession'], null=True, on_delete=models.SET_NULL))

    def backwards(self, orm):

        # Changing field 'School.imported_thru'
        db.alter_column(u'datacombo_school', 'imported_thru_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.ImportSession'], null=True))

        # Changing field 'SchoolParticipation.imported_thru'
        db.alter_column(u'datacombo_schoolparticipation', 'imported_thru_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.ImportSession'], null=True))

    models = {
        u'datacombo.course': {
            'Meta': {'object_name': 'Course'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'datacombo.importsession': {
            'Meta': {'object_name': 'ImportSession'},
            'date_created': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'Session with no name'", 'max_length': '100'})
        },
        u'datacombo.response': {
            'Meta': {'object_name': 'Response'},
            'answer': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_thru': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.ImportSession']", 'null': 'True'}),
            'on_school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.School']", 'null': 'True'}),
            'on_teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Teacher']", 'null': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Variable']"}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Student']", 'null': 'True'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Survey']"})
        },
        u'datacombo.school': {
            'Meta': {'object_name': 'School'},
            'abbrev_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_thru': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.ImportSession']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'q_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'short': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'surveys': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['datacombo.Survey']", 'through': u"orm['datacombo.SchoolParticipation']", 'symmetrical': 'False'})
        },
        u'datacombo.schoolparticipation': {
            'Meta': {'object_name': 'SchoolParticipation'},
            'date_participated': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_thru': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.ImportSession']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.School']"}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Survey']"})
        },
        u'datacombo.student': {
            'Meta': {'object_name': 'Student'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Course']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_thru': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.ImportSession']", 'null': 'True'}),
            'pin': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'response_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.School']", 'null': 'True'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Teacher']", 'null': 'True'})
        },
        u'datacombo.survey': {
            'Meta': {'object_name': 'Survey'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'datacombo.teacher': {
            'Meta': {'object_name': 'Teacher'},
            'courses': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['datacombo.Course']", 'symmetrical': 'False'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'salutation': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.School']"})
        },
        u'datacombo.variable': {
            'Meta': {'object_name': 'Variable'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Survey']"})
        }
    }

    complete_apps = ['datacombo']