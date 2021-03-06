# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ShowCatalog'
        db.create_table(u'core_showcatalog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['ShowCatalog'])

        # Adding model 'ShowCatalogItem'
        db.create_table(u'core_showcatalogitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('catalog', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.ShowCatalog'])),
            ('show', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Show'])),
        ))
        db.send_create_signal(u'core', ['ShowCatalogItem'])


    def backwards(self, orm):
        # Deleting model 'ShowCatalog'
        db.delete_table(u'core_showcatalog')

        # Deleting model 'ShowCatalogItem'
        db.delete_table(u'core_showcatalogitem')


    models = {
        u'core.animal': {
            'Meta': {'object_name': 'Animal'},
            'birthdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'breed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Breed']"}),
            'chip': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'color_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'color_ru': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'father': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'animal_father_set'", 'null': 'True', 'to': u"orm['core.Animal']"}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kennel': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'kennel_address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'kennel_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'mark': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'mother': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'animal_mother_set'", 'null': 'True', 'to': u"orm['core.Animal']"}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'name_ru': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'})
        },
        u'core.animalowner': {
            'Meta': {'ordering': "('-id',)", 'object_name': 'AnimalOwner'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'animal': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Animal']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'})
        },
        u'core.animalpedigreenumber': {
            'Meta': {'object_name': 'AnimalPedigreeNumber'},
            'animal': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Animal']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.animaltitle': {
            'Meta': {'object_name': 'AnimalTitle'},
            'animal': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Animal']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        u'core.breed': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Breed'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'core.doctemplate': {
            'Meta': {'object_name': 'DocTemplate'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'page_format': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.doctemplateelement': {
            'Meta': {'object_name': 'DocTemplateElement'},
            'code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'doc_template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.DocTemplate']"}),
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'top': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        u'core.show': {
            'Meta': {'ordering': "('-date',)", 'object_name': 'Show'},
            'check_in': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'core.showcatalog': {
            'Meta': {'object_name': 'ShowCatalog'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'core.showcatalogitem': {
            'Meta': {'object_name': 'ShowCatalogItem'},
            'catalog': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.ShowCatalog']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'show': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Show']"})
        },
        u'core.showclass': {
            'Meta': {'object_name': 'ShowClass'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.showmember': {
            'Meta': {'unique_together': "(('show', 'animal', 'showclass'),)", 'object_name': 'ShowMember'},
            'animal': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Animal']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'show': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Show']"}),
            'showclass': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.ShowClass']"})
        }
    }

    complete_apps = ['core']