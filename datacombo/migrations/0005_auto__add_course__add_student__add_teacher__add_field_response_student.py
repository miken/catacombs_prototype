# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Course'
        db.create_table(u'datacombo_course', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'datacombo', ['Course'])

        # Adding model 'Student'
        db.create_table(u'datacombo_student', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pin', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('response_id', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Course'], null=True)),
            ('teacher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Teacher'], null=True)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.School'], null=True)),
        ))
        db.send_create_signal(u'datacombo', ['Student'])

        # Adding model 'Teacher'
        db.create_table(u'datacombo_teacher', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('salutation', self.gf('django.db.models.fields.CharField')(max_length=10)),
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

        # Adding field 'Response.student'
        db.add_column(u'datacombo_response', 'student',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Student'], null=True),
                      keep_default=False)

        # Adding field 'Response.on_teacher'
        db.add_column(u'datacombo_response', 'on_teacher',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.Teacher'], null=True),
                      keep_default=False)

        # Adding field 'Response.on_school'
        db.add_column(u'datacombo_response', 'on_school',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['datacombo.School'], null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Course'
        db.delete_table(u'datacombo_course')

        # Deleting model 'Student'
        db.delete_table(u'datacombo_student')

        # Deleting model 'Teacher'
        db.delete_table(u'datacombo_teacher')

        # Removing M2M table for field courses on 'Teacher'
        db.delete_table(db.shorten_name(u'datacombo_teacher_courses'))

        # Deleting field 'Response.student'
        db.delete_column(u'datacombo_response', 'student_id')

        # Deleting field 'Response.on_teacher'
        db.delete_column(u'datacombo_response', 'on_teacher_id')

        # Deleting field 'Response.on_school'
        db.delete_column(u'datacombo_response', 'on_school_id')


    models = {
        u'datacombo.course': {
            'Meta': {'object_name': 'Course'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'datacombo.response': {
            'Meta': {'object_name': 'Response'},
            'answer': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
        u'datacombo.student': {
            'Meta': {'object_name': 'Student'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['datacombo.Course']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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