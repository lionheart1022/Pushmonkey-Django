# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'PushPackage.cert_pem'
        db.delete_column('pushmonkey_pushpackage', 'cert_pem')

        # Deleting field 'PushPackage.cert_p12'
        db.delete_column('pushmonkey_pushpackage', 'cert_p12')

        # Deleting field 'PushPackage.key_pem'
        db.delete_column('pushmonkey_pushpackage', 'key_pem')


    def backwards(self, orm):
        # Adding field 'PushPackage.cert_pem'
        db.add_column('pushmonkey_pushpackage', 'cert_pem',
                      self.gf('django.db.models.fields.files.FileField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'PushPackage.cert_p12'
        db.add_column('pushmonkey_pushpackage', 'cert_p12',
                      self.gf('django.db.models.fields.files.FileField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'PushPackage.key_pem'
        db.add_column('pushmonkey_pushpackage', 'key_pem',
                      self.gf('django.db.models.fields.files.FileField')(default='', max_length=100),
                      keep_default=False)


    models = {
        'pushmonkey.device': {
            'Meta': {'object_name': 'Device'},
            'account_key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ported': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        },
        'pushmonkey.pushmessage': {
            'Meta': {'object_name': 'PushMessage'},
            'account_key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'body': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'custom': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'device_num': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'opened_num': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'url_args': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'})
        },
        'pushmonkey.pushpackage': {
            'Meta': {'object_name': 'PushPackage'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'website_push_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['pushmonkey']