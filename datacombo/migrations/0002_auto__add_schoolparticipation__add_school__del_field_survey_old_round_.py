# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SchoolParticipation'
        db.create_table(u'datacombo_schoolparticipation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Survey'])),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.School'])),
            ('date_participated', self.gf('django.db.models.fields.DateField')()),
            ('note', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'datacombo', ['SchoolParticipation'])

        # Adding model 'School'
        db.create_table(u'datacombo_school', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('abbrev_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('q_code', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'datacombo', ['School'])

        # Deleting field 'Survey.old_round_notation'
        db.delete_column(u'datacombo_survey', 'old_round_notation')

        # Deleting field 'Survey.admin_date'
        db.delete_column(u'datacombo_survey', 'admin_date')

        # Adding field 'Survey.code'
        db.add_column(u'datacombo_survey', 'code',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'SchoolParticipation'
        db.delete_table(u'datacombo_schoolparticipation')

        # Deleting model 'School'
        db.delete_table(u'datacombo_school')

        # Adding field 'Survey.old_round_notation'
        db.add_column(u'datacombo_survey', 'old_round_notation',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10),
                      keep_default=False)

        # Adding field 'Survey.admin_date'
        db.add_column(u'datacombo_survey', 'admin_date',
                      self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 8, 14, 0, 0)),
                      keep_default=False)

        # Deleting field 'Survey.code'
        db.delete_column(u'datacombo_survey', 'code')


    models = {
        u'datacombo.response': {
            'Meta': {'object_name': 'Response'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Variable']"}),
            'raw_code': ('django.db.models.fields.IntegerField', [], {}),
            'recode': ('django.db.models.fields.IntegerField', [], {}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Survey']"})
        },
        u'datacombo.school': {
            'Meta': {'object_name': 'School'},
            'abbrev_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'q_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'short': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'surveys': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['datacombo.Survey']", 'through': u"orm['datacombo.SchoolParticipation']", 'symmetrical': 'False'})
        },
        u'datacombo.schoolparticipation': {
            'Meta': {'object_name': 'SchoolParticipation'},
            'date_participated': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.School']"}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Survey']"})
        },
        u'datacombo.survey': {
            'Meta': {'object_name': 'Survey'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'datacombo.variable': {
            'Meta': {'object_name': 'Variable'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'surveys': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Survey']"})
        }
    }

    complete_apps = ['datacombo']