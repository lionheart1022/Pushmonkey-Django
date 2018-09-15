# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Coupon.start_at'
        db.delete_column('coupons_coupon', 'start_at')

        # Deleting field 'Coupon.string'
        db.delete_column('coupons_coupon', 'string')

        # Deleting field 'Coupon.updated_at'
        db.delete_column('coupons_coupon', 'updated_at')

        # Deleting field 'Coupon.user'
        db.delete_column('coupons_coupon', 'user_id')

        # Deleting field 'Coupon.created_at'
        db.delete_column('coupons_coupon', 'created_at')

        # Deleting field 'Coupon.end_at'
        db.delete_column('coupons_coupon', 'end_at')

        # Deleting field 'Coupon.type'
        db.delete_column('coupons_coupon', 'type')

        # Deleting field 'Coupon.plan'
        db.delete_column('coupons_coupon', 'plan')


    def backwards(self, orm):
        # Adding field 'Coupon.start_at'
        db.add_column('coupons_coupon', 'start_at',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Coupon.string'
        db.add_column('coupons_coupon', 'string',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True),
                      keep_default=False)

        # Adding field 'Coupon.updated_at'
        db.add_column('coupons_coupon', 'updated_at',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True),
                      keep_default=False)

        # Adding field 'Coupon.user'
        db.add_column('coupons_coupon', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Coupon.created_at'
        db.add_column('coupons_coupon', 'created_at',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'Coupon.end_at'
        db.add_column('coupons_coupon', 'end_at',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'Coupon.type'
        db.add_column('coupons_coupon', 'type',
                      self.gf('django.db.models.fields.CharField')(default='monthly', max_length=40),
                      keep_default=False)

        # Adding field 'Coupon.plan'
        db.add_column('coupons_coupon', 'plan',
                      self.gf('django.db.models.fields.IntegerField')(default=1, max_length=40),
                      keep_default=False)


    models = {
        'coupons.coupon': {
            'Meta': {'object_name': 'Coupon'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'redeemed': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['coupons']