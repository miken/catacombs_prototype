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
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
        ))
        db.send_create_signal(u'datacombo', ['Survey'])

        # Adding model 'ImportSession'
        db.create_table(u'datacombo_importsession', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'Session with no name', max_length=100)),
            ('import_type', self.gf('django.db.models.fields.CharField')(default='Undefined', max_length=10)),
            ('date_created', self.gf('django.db.models.fields.DateField')()),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Survey'])),
        ))
        db.send_create_signal(u'datacombo', ['ImportSession'])

        # Adding model 'SummaryMeasure'
        db.create_table(u'datacombo_summarymeasure', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Survey'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'datacombo', ['SummaryMeasure'])

        # Adding model 'Variable'
        db.create_table(u'datacombo_variable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Survey'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('qraw', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('demographic', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('in_loop', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('in_report', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('summary_measure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.SummaryMeasure'], null=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'datacombo', ['Variable'])

        # Adding model 'School'
        db.create_table(u'datacombo_school', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alpha', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('abbrev_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('q_code', self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True)),
            ('imported_thru', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.ImportSession'], null=True)),
        ))
        db.send_create_signal(u'datacombo', ['School'])

        # Adding model 'SchoolParticipation'
        db.create_table(u'datacombo_schoolparticipation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.School'])),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Survey'])),
            ('date_participated', self.gf('django.db.models.fields.DateField')()),
            ('legacy_school_short', self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True)),
            ('note', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('imported_thru', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.ImportSession'], null=True)),
        ))
        db.send_create_signal(u'datacombo', ['SchoolParticipation'])

        # Adding model 'Subject'
        db.create_table(u'datacombo_subject', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'datacombo', ['Subject'])

        # Adding model 'Course'
        db.create_table(u'datacombo_course', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Subject'])),
            ('classroom_size', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('legacy_survey_index', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('feedback_given_in', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.SchoolParticipation'])),
            ('imported_thru', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.ImportSession'], null=True)),
        ))
        db.send_create_signal(u'datacombo', ['Course'])

        # Adding model 'Teacher'
        db.create_table(u'datacombo_teacher', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('salutation', self.gf('django.db.models.fields.CharField')(default='', max_length=10)),
            ('feedback_given_in', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.SchoolParticipation'])),
            ('legacy_survey_index', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('imported_thru', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.ImportSession'], null=True)),
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
            ('pin', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('response_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('surveyed_thru', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.SchoolParticipation'])),
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
            ('on_course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Course'], null=True)),
            ('on_schoolrecord', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.SchoolParticipation'], null=True)),
            ('legacy_survey_index', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('imported_thru', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.ImportSession'], null=True)),
        ))
        db.send_create_signal(u'datacombo', ['Response'])


    def backwards(self, orm):
        # Deleting model 'Survey'
        db.delete_table(u'datacombo_survey')

        # Deleting model 'ImportSession'
        db.delete_table(u'datacombo_importsession')

        # Deleting model 'SummaryMeasure'
        db.delete_table(u'datacombo_summarymeasure')

        # Deleting model 'Variable'
        db.delete_table(u'datacombo_variable')

        # Deleting model 'School'
        db.delete_table(u'datacombo_school')

        # Deleting model 'SchoolParticipation'
        db.delete_table(u'datacombo_schoolparticipation')

        # Deleting model 'Subject'
        db.delete_table(u'datacombo_subject')

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
            'Meta': {'ordering': "['name']", 'object_name': 'Course'},
            'classroom_size': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'feedback_given_in': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.SchoolParticipation']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_thru': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.ImportSession']", 'null': 'True'}),
            'legacy_survey_index': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Subject']"})
        },
        u'datacombo.importsession': {
            'Meta': {'object_name': 'ImportSession'},
            'date_created': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_type': ('django.db.models.fields.CharField', [], {'default': "'Undefined'", 'max_length': '10'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Survey']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'Session with no name'", 'max_length': '100'})
        },
        u'datacombo.response': {
            'Meta': {'object_name': 'Response'},
            'answer': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'demographic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_loop': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'in_report': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'qraw': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'summary_measure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.SummaryMeasure']", 'null': 'True'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Survey']"})
        }
    }

    complete_apps = ['datacombo']