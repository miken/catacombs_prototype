# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CSVExport'
        db.create_table(u'datacombo_csvexport', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'No name', max_length=100)),
            ('csv', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('date_requested', self.gf('django.db.models.fields.DateField')()),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Survey'])),
            ('export_type', self.gf('django.db.models.fields.CharField')(default='Undefined', max_length=10)),
            ('file_status', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'datacombo', ['CSVExport'])


    def backwards(self, orm):
        # Deleting model 'CSVExport'
        db.delete_table(u'datacombo_csvexport')


    models = {
        u'datacombo.course': {
            'Meta': {'ordering': "['name']", 'object_name': 'Course'},
            'classroom_size': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'feedback_given_in': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.SchoolParticipation']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_thru': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.ImportSession']", 'null': 'True'}),
            'legacy_survey_index': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Subject']"})
        },
        u'datacombo.csvexport': {
            'Meta': {'object_name': 'CSVExport'},
            'csv': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'date_requested': ('django.db.models.fields.DateField', [], {}),
            'export_type': ('django.db.models.fields.CharField', [], {'default': "'Undefined'", 'max_length': '10'}),
            'file_status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Survey']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'No name'", 'max_length': '100'})
        },
        u'datacombo.importsession': {
            'Meta': {'object_name': 'ImportSession'},
            'date_created': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_type': ('django.db.models.fields.CharField', [], {'default': "'Undefined'", 'max_length': '10'}),
            'number_of_rows': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parse_status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Survey']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'Session with no name'", 'max_length': '100'})
        },
        u'datacombo.response': {
            'Meta': {'object_name': 'Response'},
            'answer': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16384'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_thru': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.ImportSession']", 'null': 'True'}),
            'legacy_survey_index': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'on_course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Course']", 'null': 'True'}),
            'on_schoolrecord': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.SchoolParticipation']", 'null': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Variable']"}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Student']", 'null': 'True'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Survey']"})
        },
        u'datacombo.school': {
            'Meta': {'ordering': "['name']", 'object_name': 'School'},
            'abbrev_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'alpha': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_thru': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.ImportSession']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'q_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'}),
            'surveys': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['datacombo.Survey']", 'through': u"orm['datacombo.SchoolParticipation']", 'symmetrical': 'False'})
        },
        u'datacombo.schoolparticipation': {
            'Meta': {'ordering': "['date_participated']", 'object_name': 'SchoolParticipation'},
            'date_participated': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_thru': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.ImportSession']", 'null': 'True'}),
            'legacy_school_short': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.School']"}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Survey']"})
        },
        u'datacombo.student': {
            'Meta': {'object_name': 'Student'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_thru': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.ImportSession']", 'null': 'True'}),
            'pin': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'response_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'surveyed_thru': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.SchoolParticipation']"})
        },
        u'datacombo.subject': {
            'Meta': {'object_name': 'Subject'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'datacombo.summarymeasure': {
            'Meta': {'object_name': 'SummaryMeasure'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Survey']"})
        },
        u'datacombo.survey': {
            'Meta': {'object_name': 'Survey'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'datacombo.teacher': {
            'Meta': {'ordering': "['legacy_survey_index']", 'object_name': 'Teacher'},
            'courses': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['datacombo.Course']", 'symmetrical': 'False'}),
            'feedback_given_in': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.SchoolParticipation']"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_thru': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.ImportSession']", 'null': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'legacy_survey_index': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'salutation': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'})
        },
        u'datacombo.variable': {
            'Meta': {'ordering': "['name']", 'object_name': 'Variable'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'qual': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'summary_measure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.SummaryMeasure']", 'null': 'True', 'blank': 'True'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Survey']"})
        },
        u'datacombo.varmap': {
            'Meta': {'object_name': 'VarMap'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'raw_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Survey']"}),
            'variable': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Variable']"})
        },
        u'datacombo.varmatchrecord': {
            'Meta': {'object_name': 'VarMatchRecord'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'raw_var': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.VarMap']", 'null': 'True', 'blank': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.ImportSession']"}),
            'var': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Variable']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['datacombo']