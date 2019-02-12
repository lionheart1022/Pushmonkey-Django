# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Plan.user'
        db.delete_column('plans_plan', 'user_id')


    def backwards(self, orm):
        # Adding field 'Plan.user'
        db.add_column('plans_plan', 'user',
                      self.gf('django.db.models.fields.related.OneToOneField')(default='', to=orm['auth.User'], unique=True),
                      keep_default=False)


    models = {
        'plans.plan': {
            'Meta': {'object_name': 'Plan'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'end_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '50'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['plans']