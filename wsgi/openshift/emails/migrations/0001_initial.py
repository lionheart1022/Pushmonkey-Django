# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Email'
        db.create_table('emails_email', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('to_email', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
            ('subject', self.gf('django.db.models.fields.CharField')(default='', max_length=200)),
        ))
        db.send_create_signal('emails', ['Email'])


    def backwards(self, orm):
        # Deleting model 'Email'
        db.delete_table('emails_email')


    models = {
        'emails.email': {
            'Meta': {'object_name': 'Email'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'to_email': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['emails']