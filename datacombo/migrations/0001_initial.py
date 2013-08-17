# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ImportSession'
        db.create_table(u'datacombo_importsession', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'Session with no name', max_length=100)),
            ('date_created', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'datacombo', ['ImportSession'])

        # Adding model 'Survey'
        db.create_table(u'datacombo_survey', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
        ))
        db.send_create_signal(u'datacombo', ['Survey'])

        # Adding model 'Variable'
        db.create_table(u'datacombo_variable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Survey'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'datacombo', ['Variable'])

        # Adding model 'School'
        db.create_table(u'datacombo_school', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alpha', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('abbrev_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('q_code', self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True)),
            ('imported_thru', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.ImportSession'], null=True, on_delete=models.SET_NULL)),
        ))
        db.send_create_signal(u'datacombo', ['School'])

        # Adding model 'SchoolParticipation'
        db.create_table(u'datacombo_schoolparticipation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.School'])),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Survey'])),
            ('date_participated', self.gf('django.db.models.fields.DateField')()),
            ('legacy_school_short', self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True)),
            ('note', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('imported_thru', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.ImportSession'], null=True, on_delete=models.SET_NULL)),
        ))
        db.send_create_signal(u'datacombo', ['SchoolParticipation'])

        # Adding model 'Course'
        db.create_table(u'datacombo_course', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'datacombo', ['Course'])

        # Adding model 'Teacher'
        db.create_table(u'datacombo_teacher', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('salutation', self.gf('django.db.models.fields.CharField')(default='', max_length=10)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.School'])),
        ))
        db.send_create_signal(u'datacombo', ['Teacher'])

        # Adding M2M table for field courses on 'Teacher'
        m2m_table_name = db.shorten_name(u'datacombo_teacher_courses')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('teacher', models.ForeignKey(orm[u'datacombo.teacher'], null=False)),
            ('course', models.ForeignKey(orm[u'datacombo.course'], null=False))
        ))
        db.create_unique(m2m_table_name, ['teacher_id', 'course_id'])

        # Adding model 'Student'
        db.create_table(u'datacombo_student', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pin', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('response_id', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Course'], null=True)),
            ('teacher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Teacher'], null=True)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.School'], null=True)),
            ('imported_thru', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.ImportSession'], null=True)),
        ))
        db.send_create_signal(u'datacombo', ['Student'])

        # Adding model 'Response'
        db.create_table(u'datacombo_response', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Variable'])),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Survey'])),
            ('answer', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Student'], null=True)),
            ('on_teacher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Teacher'], null=True)),
            ('on_school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.School'], null=True)),
            ('imported_thru', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.ImportSession'], null=True)),
        ))
        db.send_create_signal(u'datacombo', ['Response'])


    def backwards(self, orm):
        # Deleting model 'ImportSession'
        db.delete_table(u'datacombo_importsession')

        # Deleting model 'Survey'
        db.delete_table(u'datacombo_survey')

        # Deleting model 'Variable'
        db.delete_table(u'datacombo_variable')

        # Deleting model 'School'
        db.delete_table(u'datacombo_school')

        # Deleting model 'SchoolParticipation'
        db.delete_table(u'datacombo_schoolparticipation')

        # Deleting model 'Course'
        db.delete_table(u'datacombo_course')

        # Deleting model 'Teacher'
        db.delete_table(u'datacombo_teacher')

        # Removing M2M table for field courses on 'Teacher'
        db.delete_table(db.shorten_name(u'datacombo_teacher_courses'))

        # Deleting model 'Student'
        db.delete_table(u'datacombo_student')

        # Deleting model 'Response'
        db.delete_table(u'datacombo_response')


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
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.School']", 'null': 'True'}),
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
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'salutation': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.School']"})
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