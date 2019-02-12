# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Device.website_push_id'
        db.delete_column('pushmonkey_device', 'website_push_id')

        # Adding field 'Device.account_key'
        db.add_column('pushmonkey_device', 'account_key',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True),
                      keep_default=False)

        # Deleting field 'PushMessage.website_push_id'
        db.delete_column('pushmonkey_pushmessage', 'website_push_id')

        # Adding field 'PushMessage.account_key'
        db.add_column('pushmonkey_pushmessage', 'account_key',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Device.website_push_id'
        db.add_column('pushmonkey_device', 'website_push_id',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True),
                      keep_default=False)

        # Deleting field 'Device.account_key'
        db.delete_column('pushmonkey_device', 'account_key')

        # Adding field 'PushMessage.website_push_id'
        db.add_column('pushmonkey_pushmessage', 'website_push_id',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True),
                      keep_default=False)

        # Deleting field 'PushMessage.account_key'
        db.delete_column('pushmonkey_pushmessage', 'account_key')


    models = {
        'pushmonkey.device': {
            'Meta': {'object_name': 'Device'},
            'account_key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        },
        'pushmonkey.pushmessage': {
            'Meta': {'object_name': 'PushMessage'},
            'account_key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'body': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'device_num': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'url_args': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'})
        }
    }

    complete_apps = ['pushmonkey']