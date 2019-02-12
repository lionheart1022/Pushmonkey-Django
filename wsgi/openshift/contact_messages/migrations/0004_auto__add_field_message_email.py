# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Message.email'
        db.add_column('contact_messages_message', 'email',
                      self.gf('django.db.models.fields.EmailField')(default='', max_length=200),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Message.email'
        db.delete_column('contact_messages_message', 'email')


    models = {
        'contact_messages.message': {
            'Meta': {'object_name': 'Message'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'max_length': '900'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['contact_messages']