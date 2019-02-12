# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Message'
        db.create_table('contact_messages_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('message', self.gf('django.db.models.fields.TextField')(max_length=900)),
        ))
        db.send_create_signal('contact_messages', ['Message'])


    def backwards(self, orm):
        # Deleting model 'Message'
        db.delete_table('contact_messages_message')


    models = {
        'contact_messages.message': {
            'Meta': {'object_name': 'Message'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'max_length': '900'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['contact_messages']