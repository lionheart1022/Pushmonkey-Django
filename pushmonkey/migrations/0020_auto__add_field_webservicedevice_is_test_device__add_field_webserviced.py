# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'WebServiceDevice.is_test_device'
        db.add_column(u'pushmonkey_webservicedevice', 'is_test_device',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'WebServiceDevice.tested'
        db.add_column(u'pushmonkey_webservicedevice', 'tested',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'WebServiceDevice.is_test_device'
        db.delete_column(u'pushmonkey_webservicedevice', 'is_test_device')

        # Deleting field 'WebServiceDevice.tested'
        db.delete_column(u'pushmonkey_webservicedevice', 'tested')


    models = {
        u'pushmonkey.batch': {
            'Meta': {'object_name': 'Batch'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'push_message': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pushmonkey.PushMessage']"}),
            'resp': ('django.db.models.fields.TextField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        },
        u'pushmonkey.device': {
            'Meta': {'object_name': 'Device'},
            'account_key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ported': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        },
        u'pushmonkey.pushmessage': {
            'Meta': {'object_name': 'PushMessage'},
            'account_key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'body': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'custom': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'device_num': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'opened_num': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'url_args': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'})
        },
        u'pushmonkey.pushpackage': {
            'Meta': {'object_name': 'PushPackage'},
            'cert_p12': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'cert_pem': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'key_pem': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'website_push_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'website_push_id_created': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'pushmonkey.webservicedevice': {
            'Meta': {'object_name': 'WebServiceDevice'},
            'account_key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'chrome': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'endpoint': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_test_device': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mozilla': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subscription_id': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tested': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['pushmonkey']