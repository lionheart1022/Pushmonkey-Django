# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Message.created_at'
        db.add_column('contact_messages_message', 'created_at',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'Message.updated_at'
        db.add_column('contact_messages_message', 'updated_at',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Message.created_at'
        db.delete_column('contact_messages_message', 'created_at')

        # Deleting field 'Message.updated_at'
        db.delete_column('contact_messages_message', 'updated_at')


    models = {
        'contact_messages.message': {
            'Meta': {'object_name': 'Message'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'max_length': '900'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['contact_messages']