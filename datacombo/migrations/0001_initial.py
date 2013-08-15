# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Survey'
        db.create_table(u'datacombo_survey', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('admin_date', self.gf('django.db.models.fields.DateField')()),
            ('old_round_notation', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'datacombo', ['Survey'])

        # Adding model 'Variable'
        db.create_table(u'datacombo_variable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('surveys', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Survey'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'datacombo', ['Variable'])

        # Adding model 'Response'
        db.create_table(u'datacombo_response', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Variable'])),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Survey'])),
            ('raw_code', self.gf('django.db.models.fields.IntegerField')()),
            ('recode', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'datacombo', ['Response'])


    def backwards(self, orm):
        # Deleting model 'Survey'
        db.delete_table(u'datacombo_survey')

        # Deleting model 'Variable'
        db.delete_table(u'datacombo_variable')

        # Deleting model 'Response'
        db.delete_table(u'datacombo_response')


    models = {
        u'datacombo.response': {
            'Meta': {'object_name': 'Response'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Variable']"}),
            'raw_code': ('django.db.models.fields.IntegerField', [], {}),
            'recode': ('django.db.models.fields.IntegerField', [], {}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Survey']"})
        },
        u'datacombo.survey': {
            'Meta': {'object_name': 'Survey'},
            'admin_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'old_round_notation': ('django.db.models.fields.CharField', [], {'max_length': '10'})
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