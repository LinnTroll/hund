# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Breed'
        db.create_table(u'core_breed', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal(u'core', ['Breed'])

        # Adding model 'Animal'
        db.create_table(u'core_animal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name_ru', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('breed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Breed'])),
            ('color_ru', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('color_en', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('birthdate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('mark', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('chip', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('father', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='animal_father_set', null=True, to=orm['core.Animal'])),
            ('mother', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='animal_mother_set', null=True, to=orm['core.Animal'])),
            ('kennel', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('kennel_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('kennel_address', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['Animal'])

        # Adding model 'AnimalPedigreeNumber'
        db.create_table(u'core_animalpedigreenumber', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('animal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Animal'])),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['AnimalPedigreeNumber'])

        # Adding model 'AnimalOwner'
        db.create_table(u'core_animalowner', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('animal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Animal'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['AnimalOwner'])

        # Adding model 'AnimalTitle'
        db.create_table(u'core_animaltitle', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('animal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Animal'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('info', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['AnimalTitle'])

        # Adding model 'Show'
        db.create_table(u'core_show', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('check_in', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['Show'])

        # Adding model 'ShowClass'
        db.create_table(u'core_showclass', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'core', ['ShowClass'])

        # Adding model 'ShowMember'
        db.create_table(u'core_showmember', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('show', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Show'])),
            ('animal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Animal'])),
            ('showclass', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.ShowClass'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['ShowMember'])

        # Adding unique constraint on 'ShowMember', fields ['show', 'animal', 'showclass']
        db.create_unique(u'core_showmember', ['show_id', 'animal_id', 'showclass_id'])

        # Adding model 'DocTemplate'
        db.create_table(u'core_doctemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('page_format', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal(u'core', ['DocTemplate'])

        # Adding model 'DocTemplateElement'
        db.create_table(u'core_doctemplateelement', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('doc_template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.DocTemplate'])),
            ('code', self.gf('django.db.models.fields.CharField')(default='', max_length=250, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')(default='')),
            ('left', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('top', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('width', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['DocTemplateElement'])


    def backwards(self, orm):
        # Removing unique constraint on 'ShowMember', fields ['show', 'animal', 'showclass']
        db.delete_unique(u'core_showmember', ['show_id', 'animal_id', 'showclass_id'])

        # Deleting model 'Breed'
        db.delete_table(u'core_breed')

        # Deleting model 'Animal'
        db.delete_table(u'core_animal')

        # Deleting model 'AnimalPedigreeNumber'
        db.delete_table(u'core_animalpedigreenumber')

        # Deleting model 'AnimalOwner'
        db.delete_table(u'core_animalowner')

        # Deleting model 'AnimalTitle'
        db.delete_table(u'core_animaltitle')

        # Deleting model 'Show'
        db.delete_table(u'core_show')

        # Deleting model 'ShowClass'
        db.delete_table(u'core_showclass')

        # Deleting model 'ShowMember'
        db.delete_table(u'core_showmember')

        # Deleting model 'DocTemplate'
        db.delete_table(u'core_doctemplate')

        # Deleting model 'DocTemplateElement'
        db.delete_table(u'core_doctemplateelement')


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