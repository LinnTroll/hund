# -*- coding: utf-8 -*-
from django import forms

from .models import (Animal, AnimalPedigreeNumber, AnimalOwner, AnimalTitle, DocTemplate, Show, ShowMember, ShowGroup,
                     ShowCatalogItem, Owner, Kennel)


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal

    def clean(self):
        cleaned_data = super(AnimalForm, self).clean()

        name_ru = cleaned_data.get('name_ru', None)
        name_en = cleaned_data.get('name_en', None)

        if not name_ru and not name_en:
            msg = u'Должна быть заполнена либо русская либо английская кличка.'
            raise forms.ValidationError(msg)

        return cleaned_data

    def clean_reg_number(self):
        reg_number = self.cleaned_data.get('reg_number', None)

        animals = Animal.objects.all()

        if self.instance:
            animals = animals.exclude(pk=self.instance.pk)

        if reg_number:
            if animals.filter(reg_number=reg_number).exists():
                raise forms.ValidationError(u'Регистрационный номер уже занят')

        return reg_number


class AnimalPedigreeNumberForm(forms.ModelForm):
    class Meta:
        model = AnimalPedigreeNumber
        fields = ('number',)


class AnimalOwnerForm(forms.ModelForm):
    class Meta:
        model = AnimalOwner
        exclude = ('animal',)


class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner


class KennelForm(forms.ModelForm):
    class Meta:
        model = Kennel


class AnimalTitleForm(forms.ModelForm):
    class Meta:
        model = AnimalTitle
        exclude = ('animal',)


class DoctplSelectForm(forms.Form):
    animal = forms.ModelChoiceField(queryset=Animal.objects.all())
    tpl = forms.ModelChoiceField(queryset=DocTemplate.objects.all())


class ShowCreateForm(forms.ModelForm):
    class Meta:
        model = Show

    def __init__(self, *args, **kwargs):
        super(ShowCreateForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs.update({'data-ng-datepicker': None})


class ShowGroupCreateForm(forms.ModelForm):
    class Meta:
        model = ShowGroup


class ShowMemberCreateForm(forms.ModelForm):
    class Meta:
        model = ShowMember
        fields = ('animal', 'showclass')


class ShowMemberAdditionCreateForm(forms.ModelForm):
    class Meta:
        model = ShowMember
        fields = ('animal', 'showclass', 'number')

    def __init__(self, *args, **kwargs):
        self.show = kwargs['show']
        del kwargs['show']
        super(ShowMemberAdditionCreateForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'number':
                field.required = True

    def clean(self):
        cleaned_data = super(ShowMemberAdditionCreateForm, self).clean()
        _number = cleaned_data.get('number', None)

        number = None

        try:
            number = int(_number)
            if number < 1:
                number = None
        except (TypeError, ValueError):
            pass

        if not number:
            raise forms.ValidationError(u'Введите номер')

        if number in [x.number for x in self.show.showmember_set.all()]:
            raise forms.ValidationError(u'Номер уже использован')

        return cleaned_data


class ShowMemberResultForm(forms.ModelForm):
    class Meta:
        model = ShowMember
        fields = ('res_rate', 'res_title')

    def add_prefix(self, field_name):
        if self.instance and self.instance.pk:
            field_name = '%s_row_%s' % (field_name, self.instance.pk)
        return super(ShowMemberResultForm, self).add_prefix(field_name)


class ShowCatalogItemForm(forms.ModelForm):
    class Meta:
        model = ShowCatalogItem
        exclude = ('catalog',)


class DocTemplateForm(forms.ModelForm):
    class Meta:
        model = DocTemplate
