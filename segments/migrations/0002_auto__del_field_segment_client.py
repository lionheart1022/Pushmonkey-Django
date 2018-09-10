# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Segment.client'
        db.delete_column(u'segments_segment', 'client_id')


    def backwards(self, orm):
        # Adding field 'Segment.client'
        db.add_column(u'segments_segment', 'client',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['clients.ClientProfile']),
                      keep_default=False)


    models = {
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
        },
        u'segments.segment': {
            'Meta': {'object_name': 'Segment'},
            'account_key': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'device': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['pushmonkey.Device']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'web_service_device': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['pushmonkey.WebServiceDevice']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['segments']