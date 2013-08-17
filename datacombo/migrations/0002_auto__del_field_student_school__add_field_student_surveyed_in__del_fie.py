# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Student.school'
        db.delete_column(u'datacombo_student', 'school_id')

        # Adding field 'Student.surveyed_in'
        db.add_column(u'datacombo_student', 'surveyed_in',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['datacombo.SchoolParticipation']),
                      keep_default=False)

        # Deleting field 'Teacher.school'
        db.delete_column(u'datacombo_teacher', 'school_id')

        # Adding field 'Teacher.feedback_given_in'
        db.add_column(u'datacombo_teacher', 'feedback_given_in',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['datacombo.SchoolParticipation']),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Student.school'
        db.add_column(u'datacombo_student', 'school',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.School'], null=True),
                      keep_default=False)

        # Deleting field 'Student.surveyed_in'
        db.delete_column(u'datacombo_student', 'surveyed_in_id')

        # Adding field 'Teacher.school'
        db.add_column(u'datacombo_teacher', 'school',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['datacombo.School']),
                      keep_default=False)

        # Deleting field 'Teacher.feedback_given_in'
        db.delete_column(u'datacombo_teacher', 'feedback_given_in_id')


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
            'Meta': {'ordering': "['name']", 'object_name': 'School'},
            'abbrev_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'alpha': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_thru': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.ImportSession']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'q_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'}),
            'surveys': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['datacombo.Survey']", 'through': u"orm['datacombo.SchoolParticipation']", 'symmetrical': 'False'})
        },
        u'datacombo.schoolparticipation': {
            'Meta': {'ordering': "['date_participated']", 'object_name': 'SchoolParticipation'},
            'date_participated': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_thru': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.ImportSession']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'legacy_school_short': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
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
            'surveyed_in': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.SchoolParticipation']"}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Teacher']", 'null': 'True'})
        },
        u'datacombo.survey': {
            'Meta': {'ordering': "['code']", 'object_name': 'Survey'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'datacombo.teacher': {
            'Meta': {'object_name': 'Teacher'},
            'courses': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['datacombo.Course']", 'symmetrical': 'False'}),
            'feedback_given_in': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.SchoolParticipation']"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'salutation': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'})
        },
        u'datacombo.variable': {
            'Meta': {'ordering': "['name']", 'object_name': 'Variable'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Survey']"})
        }
    }

    complete_apps = ['datacombo']