# -*- coding: utf-8 -*-
import re
import json
from itertools import chain, product

from django.db import models
from django.core.urlresolvers import reverse

from apps.core.utils.page_formats import PAGE_FORMATS_INFO_CHOICES, PAGE_FORMATS_INFO
from apps.core.utils.utils import prepare_pedigree_number_number

from pytils import dt


class BreedGroup(models.Model):
    name = models.CharField(max_length=250)

    class Meta:
        verbose_name = u'Группа'
        verbose_name_plural = u'Группы'
        ordering = ('name', )

    def __unicode__(self):
        return self.name


class Breed(models.Model):
    group = models.ForeignKey(BreedGroup, blank=True, null=True, verbose_name=u'Группа')
    name = models.CharField(max_length=250)

    class Meta:
        verbose_name = u'Порода'
        verbose_name_plural = u'Породы'
        ordering = ('name', )

    def as_dict(self):
        return {
            'id': self.pk,
            'text': self.name,
        }

    def __unicode__(self):
        return self.name


class Animal(models.Model):
    GENDER_CHOICES = (
        ('m', u'К'),
        ('f', u'С'),
    )

    name_ru = models.CharField(u'Кличка (ru)', max_length=250, blank=True, null=True)
    name_en = models.CharField(u'Кличка (en)', max_length=250, blank=True, null=True)
    short_name = models.CharField(u'Короткое имя', max_length=60, blank=True, null=True)

    gender = models.CharField(u'Пол', max_length=1, choices=GENDER_CHOICES)
    breed = models.ForeignKey(Breed, verbose_name=u'Порода')

    color_ru = models.CharField(u'Цвет (ru)', max_length=100, blank=True, null=True)
    color_en = models.CharField(u'Цвет (en)', max_length=100, blank=True, null=True)

    birthdate = models.DateField(u'Дата рождения', blank=True, null=True)

    mark = models.CharField(u'Клеймо', max_length=60, blank=True, null=True)
    chip = models.CharField(u'Чип', max_length=60, blank=True, null=True)

    father = models.ForeignKey('self', verbose_name=u'Отец', blank=True, null=True, related_name='animal_father_set')
    mother = models.ForeignKey('self', verbose_name=u'Мать', blank=True, null=True, related_name='animal_mother_set')

    # kennel = models.CharField(u'Питомник/клуб', max_length=100, blank=True, null=True)
    # kennel_name = models.CharField(u'Заводчик', max_length=100, blank=True, null=True)
    # kennel_address = models.CharField(u'Адрес заводчика', max_length=250, blank=True, null=True)

    photo = models.ImageField(u'Фото', upload_to='animals', blank=True, null=True)

    is_our = models.BooleanField(u'Наш', blank=True, default=False)
    reg_number = models.CharField(u'Рег. №', max_length=64, blank=True, null=True)
    reg_date = models.DateField(u'Дата регистрации', blank=True, null=True)

    created_at = models.DateTimeField(u'Создан', auto_now_add=True)

    class Meta:
        verbose_name = u'Животное'
        verbose_name_plural = u'Животные'

    def save(self, *args, **kwargs):
        if not self.reg_number:
            self.reg_number = None
        super(Animal, self).save(*args, **kwargs)

    def get_ancestors_count(self):
        tc = 0
        if self.father:
            tc += self.father.get_ancestors_count() + 1
        if self.mother:
            tc += self.mother.get_ancestors_count() + 1
        return tc

    def get_display(self):
        return u'%s' % (self.name_ru or self.name_en, )

    def get_color(self):
        if self.color_ru or self.color_en:
            return u'%s' % (self.color_ru or self.color_en, )
        return None

    def get_birthdate_formated(self):
        if self.birthdate:
            return self.birthdate.isoformat()
        return None

    def get_birthdate_human(self):
        if self.birthdate:
            return dt.ru_strftime(u"%d %B %Y", self.birthdate, inflected=True)
        return None

    def get_pedigree_numbers(self):
        pedigree_numbers_qs = self.animalpedigreenumber_set.all()
        pedigree_numbers = [x.as_dict() for x in pedigree_numbers_qs]
        if not pedigree_numbers:
            pedigree_numbers = [{'id': None, 'number': ''}, ]
        return pedigree_numbers

    def get_last_pedigree_number(self):
        pedigree_numbers = self.animalpedigreenumber_set.all()
        if pedigree_numbers:
            pedigree_number = pedigree_numbers[0]
            return pedigree_number.number
        return None

    def get_owners(self):
        owners_qs = self.animalowner_set.all()
        owners = [x.as_dict() for x in owners_qs]
        if not owners:
            owners = [{
                'id': None,
                'data': {
                    'name': '',
                    'address': '',
                    'phone': '',
                    'email': '',
                    'work': '',
                },
            }, ]
        return owners

    def get_kennels(self):
        kennels_qs = self.animalkennel_set.all()
        kennels = [x.as_dict() for x in kennels_qs]
        if not kennels:
            kennels = [{
                'id': None,
                'data': {
                    'name': '',
                    'address': '',
                    'breeder': ''
                },
            }, ]
        return kennels

    def get_last_owner(self):
        owners = self.animalowner_set.all()
        if owners:
            return owners[0]
        return None

    def get_last_kennel(self):
        kennels = self.animalkennel_set.all()
        if kennels:
            return kennels[0]
        return None

    def get_titles(self):
        titles_qs = self.animaltitle_set.all()
        titles = [x.as_dict() for x in titles_qs]
        if not titles:
            titles = [{
                'id': None,
                'title': '',
                'info': '',
            }, ]
        return titles

    def get_ancestor_by_role(self, role):
        _item = self
        for x in role:
            #print "###", x, _item.pk, self.father
            _item = getattr(_item, {'m': 'father', 'f': 'mother'}[x], None)
            if not _item:
                return None
        return _item

    def get_ancestors(self):
        ancestors = {}
        ancestor_roles = [''.join(x) for x in chain(*[product(['m', 'f'], repeat=x+1) for x in xrange(4)])]
        for role in ancestor_roles:
            ancestors[role] = None
            ancestor = self.get_ancestor_by_role(role)
            if ancestor:
                ancestors[role] = ancestor.as_dict(no_ancestors=True)
        return ancestors

    def get_reg_date_formated(self):
        if self.reg_date:
            return self.reg_date.isoformat()
        return None

    def get_reg_date_human(self):
        if self.reg_date:
            return dt.ru_strftime(u"%d %B %Y", self.reg_date, inflected=True)
        return None

    def get_absolute_url(self):
        if self.pk:
            return reverse('core_animals_edit', kwargs={'pk': self.pk})
        return u''

    def as_dict(self, no_ancestors=False):
        data = {
            'id': self.pk,
            'pk': self.pk,
            'text': self.get_display(),
            'name_ru': self.name_ru,
            'name_en': self.name_en,
            'short_name': self.short_name,
            'gender': self.gender,
            'color_ru': self.color_ru,
            'color_en': self.color_en,
            'birthdate': self.get_birthdate_formated(),
            'mark': self.mark,
            'chip': self.chip,
            # 'kennel': self.kennel,
            # 'kennel_name': self.kennel_name,
            # 'kennel_address': self.kennel_address,
            'breed': self.breed.pk,
            'breed_data': self.breed.as_dict(),
            'pedigree_numbers': self.get_pedigree_numbers(),
            'owners': self.get_owners(),
            'kennels': self.get_kennels(),
            'titles': self.get_titles(),
            'is_our': self.is_our,
            'reg_number': self.reg_number,
            'reg_date': self.get_reg_date_formated(),
            'absolute_url': self.get_absolute_url(),
        }
        if not no_ancestors:
            data['ancestors'] = self.get_ancestors()
        return data

    def get_gender_label(self):
        return {
            'm': u'Кобель',
            'f': u'Сука',
        }[self.gender]

    @classmethod
    def _print_fields_map(cls):
        return [
            ('get_display', u'Имя'),
            ('get_gender_label', u'Пол'),
            ('breed__name', u'Порода'),
            ('get_last_pedigree_number', u'Номер родословной'),
            ('get_color', u'Цвет'),
            ('get_birthdate_human', u'Дата рождения'),
            ('mark', u'Клеймо'),
            ('chip', u'Чип'),
            ('father__get_display', u'Имя отца'),
            ('mother__get_display', u'Имя матери'),
            ('get_last_owner__owner__name', u'Владелец'),

            ('get_last_kennel__kennel__name', u'Питомник'),
            ('get_last_kennel__kennel__breeder', u'Заводчик'),
            ('get_last_kennel__kennel__address', u'Адрес заводчика'),

            # ('kennel', u'Питомник'),
            # ('kennel_name', u'Заводчик'),
            # ('kennel_address', u'Адрес заводчика'),
        ]

    def __unicode__(self):
        return self.get_display()


class AnimalPedigreeNumber(models.Model):
    animal = models.ForeignKey(Animal, verbose_name=u'Животное')
    number = models.CharField(u'Номер родословной', max_length=100)
    parsed_number = models.CharField(u'Подготовленный номер', max_length=100, blank=True, default=u'')

    created_at = models.DateTimeField(u'Создан', auto_now_add=True)

    class Meta:
        verbose_name = u'Номер родословной'
        verbose_name_plural = u'Номера родословных'
        ordering = ('-created_at', )

    def save(self, *args, **kwargs):
        self.number = self.number.strip()
        self.parsed_number = prepare_pedigree_number_number(self.number)
        super(AnimalPedigreeNumber, self).save(*args, **kwargs)

    def get_display(self):
        return u'%s, %s' % (self.animal, self.number)

    def as_dict(self):
        return {
            'id': self.pk,
            'number': self.number,
        }

    def __unicode__(self):
        return self.get_display()


class Owner(models.Model):
    name = models.CharField(u'Имя', max_length=100)
    address = models.CharField(u'Адрес', max_length=250, blank=True, null=True)
    phone = models.CharField(u'Телефон', max_length=60, blank=True, null=True)
    email = models.CharField(u'Email', max_length=1000, blank=True, null=True)
    work = models.CharField(u'Место работы', max_length=2000, blank=True, null=True)
    created_at = models.DateTimeField(u'Создан', auto_now_add=True)

    class Meta:
        verbose_name = u'Владелец'
        verbose_name_plural = u'Владельцы'
        ordering = ('-id', )

    def get_display(self):
        return self.name

    def as_dict(self):
        return {
            'id': self.pk,
            'pk': self.pk,
            'text': self.get_display(),
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'work': self.work,
        }

    def __unicode__(self):
        return self.get_display()


class AnimalOwner(models.Model):
    animal = models.ForeignKey(Animal, verbose_name=u'Животное')
    owner = models.ForeignKey(Owner, verbose_name=u'Владелец')

    class Meta:
        verbose_name = u'Владелец животного'
        verbose_name_plural = u'Владелецы животных'

    def get_display(self):
        return u'%s, %s' % (self.animal, self.owner)

    def as_dict(self):
        return {
            'id': self.id,
            'data': self.owner.as_dict(),
        }

    def __unicode__(self):
        return self.get_display()


class Kennel(models.Model):
    name = models.CharField(u'Питомник/клуб', max_length=100, blank=True, null=True)
    breeder = models.CharField(u'Заводчик', max_length=100, blank=True, null=True)
    address = models.CharField(u'Адрес заводчика', max_length=250, blank=True, null=True)

    class Meta:
        verbose_name = u'Питомник'
        verbose_name_plural = u'Питомники'
        ordering = ('-id', )

    def get_display(self):
        return self.name

    def as_dict(self):
        return {
            'id': self.pk,
            'pk': self.pk,
            'text': self.get_display(),
            'name': self.name,
            'breeder': self.breeder,
            'address': self.address,
        }

    def __unicode__(self):
        return self.get_display()


class AnimalKennel(models.Model):
    animal = models.ForeignKey(Animal, verbose_name=u'Животное')
    kennel = models.ForeignKey(Kennel, verbose_name=u'Питомник')

    class Meta:
        verbose_name = u'Питомник животного'
        verbose_name_plural = u'Питомники животных'

    def get_display(self):
        return u'%s, %s' % (self.animal, self.kennel)

    def as_dict(self):
        return {
            'id': self.id,
            'data': self.kennel.as_dict(),
        }

    def __unicode__(self):
        return self.get_display()


class AnimalTitle(models.Model):
    animal = models.ForeignKey(Animal, verbose_name=u'Животное')
    title = models.CharField(u'Титул', max_length=60)
    info = models.CharField(u'Уточнение', max_length=60, blank=True, null=True)
    created_at = models.DateTimeField(u'Создан', auto_now_add=True)

    def as_dict(self):
        return {
            'id': self.pk,
            'title': self.title,
            'info': self.info,
        }

    class Meta:
        verbose_name = u'Титул'
        verbose_name_plural = u'Титулы'


class ShowGroup(models.Model):
    check_in = models.BooleanField(u'Регистрация закрыта', default=False)
    catalog = models.OneToOneField('ShowCatalog', verbose_name='Каталог', blank=True, null=True)
    created_at = models.DateTimeField(u'Создан', auto_now_add=True)

    def numerate_members(self):
        shows = self.show_set.all()
        animals = Animal.objects.filter(showmember__show__group=self).distinct()
        # animals_num_map = dict([(int(x.id), None) for x in animals])
        counter = 0
        for show in shows:
            show_members = show.showmember_set.all()
            for show_member in show_members:
                animal_id = int(show_member.animal.id)
                #animal_number = animals_num_map.get(animal_id, None)
                counter += 1
                animal_number = counter
                show_member.number = animal_number
                show_member.save()

    def __unicode__(self):
        shows = self.show_set.all()
        if shows:
            return u', '.join([u'%s' % x for x in shows])
        return u'Нет выставок'

    class Meta:
        verbose_name = u'Группа выставок'
        verbose_name_plural = u'Группа выставок'
        ordering = ('-created_at', )


class Show(models.Model):
    group = models.ForeignKey(ShowGroup, verbose_name=u'Группа', blank=True, null=True)
    title = models.CharField(u'Название выставки', max_length=250)
    date = models.DateField(u'Дата проведения', )
    judge = models.CharField(u'Судья', max_length=250, blank=True, default='')
    assistant = models.CharField(u'Секретарь', max_length=250, blank=True, default='')
    # check_in = models.BooleanField(u'Регистрация закрыта', default=False)
    created_at = models.DateTimeField(u'Создан', auto_now_add=True)

    # def numerate_members(self):
    #     members = self.showmember_set.all()
    #     for n, member in enumerate(members):
    #         member.number = n + 1
    #         member.save()

    # def save(self, *args, **kwargs):
    #     if self.pk:
    #         oi = Show.objects.get(pk=self.pk)
    #         if self.check_in and not oi.check_in:
    #             self.numerate_members()
    #     super(Show, self).save(*args, **kwargs)

    def get_date_human(self):
        if self.date:
            return dt.ru_strftime(u"%d %B %Y", self.date, inflected=True)
        return None

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'Выставка'
        verbose_name_plural = u'Выставки'
        ordering = ('id', )


class ShowClass(models.Model):
    title = models.CharField(u'Название', max_length=100)

    def __unicode__(self):
        return self.title

    def get_short_title(self):
        if self.title.lower().startswith(u'класс '):
            return self.title[6:].capitalize()
        return self.title

    @property
    def short_title(self):
        return self.get_short_title()

    class Meta:
        verbose_name = u'Класс выставки'
        verbose_name_plural = u'Класс выставки'


class ShowMember(models.Model):
    RATE_CHOICES = (
        ('b4', u'Правильно выращен'),
        ('b5', u'Образцово выращен'),
        ('3', u'Удовлетворительно'),
        ('4', u'Хорошо'),
        ('4+', u'Очень хорошо'),
        ('5', u'Отлично'),
    )

    TITLE_CHOICES = (
        ('cac', u'CAC'),
        ('rcac', u'R.CAC'),
        ('bjc', u'BJC'),
    )

    show = models.ForeignKey(Show, verbose_name=u'Выставка')
    animal = models.ForeignKey(Animal, verbose_name=u'Животное')
    number = models.PositiveIntegerField(u'Номер', blank=True, null=True)
    add_list = models.BooleanField(u'Дополнительный список', blank=True, default=False)
    showclass = models.ForeignKey(ShowClass, verbose_name=u'Класс')

    res_rate = models.CharField(u'Оценка', max_length=32, choices=RATE_CHOICES, blank=True, null=True)
    res_title = models.CharField(u'Титул', max_length=32, choices=TITLE_CHOICES, blank=True, null=True)

    cert_number = models.CharField(u'Номер сертификата', max_length=64, blank=True, default='')

    created_at = models.DateTimeField(u'Создан', auto_now_add=True)

    def save(self, *args, **kwargs):
        # Autonumerate show members
        if self.pk is None and self.show and self.show.group and self.show.group.check_in:
            self.add_list = True
            if self.number is None:
                group_show_members = ShowMember.objects.filter(show__group=self.show.group).distinct()
                numbers = map(int, filter(bool, [x.number for x in group_show_members]))
                if numbers:
                    max_number = max(numbers)
                else:
                    max_number = 1
                self.number = max_number + 1
        super(ShowMember, self).save(*args, **kwargs)

    @classmethod
    def _print_fields_map(cls):
        animal_fields = [('animal__%s' % x[0], x[1]) for x in models.get_model('core', 'animal')._print_fields_map()]
        return animal_fields + [
            ('number', u'Номер'),
            ('showclass__get_short_title', u'Класс'),
            ('show__title', u'Название выставки'),
            ('show__get_date_human', u'Дата выставки'),
            ('show__judge', u'Судья'),
            ('show__assistant', u'Секретарь'),
            ('get_res_rate_display', u'Оценка'),
            ('get_res_title_display', u'Титул'),
            ('cert_number', u'Номер сертификата'),
        ]

    def __unicode__(self):
        return u'%s %s %s' % (self.show, self.animal, self.showclass)

    def get_res_form(self):
        from .forms import ShowMemberResultForm
        form = ShowMemberResultForm(data=None, instance=self)
        return form

    @property
    def res_form(self):
        return self.get_res_form()

    class Meta:
        verbose_name = u'Участник выставки'
        verbose_name_plural = u'Участники выставки'
        unique_together = ('show', 'animal', 'showclass')
        ordering = ('animal__breed__name', 'showclass__pk', '-animal__gender', 'animal__name_ru')


class ShowCatalog(models.Model):
    created_at = models.DateTimeField(u'Создан', auto_now_add=True)

    def __unicode__(self):
        return u'Каталог #%s: %s' % (self.pk, u', '.join([u'%s' % x.show for x in self.showcatalogitem_set.all()]))

    class Meta:
        verbose_name = u'Каталог'
        verbose_name_plural = u'Каталог'
        ordering = ('-id', )


class ShowCatalogItem(models.Model):
    catalog = models.ForeignKey(ShowCatalog, verbose_name=u'Каталог')
    show = models.ForeignKey(Show, verbose_name=u'Выставка')

    def __unicode__(self):
        return self.show.title

    class Meta:
        ordering = ('show__id', )
        verbose_name = u'Выставка в каталоге'
        verbose_name_plural = u'Выставка в каталоге'


class DocTemplate(models.Model):
    title = models.CharField(max_length=100)
    page_format = models.CharField(max_length=32, choices=PAGE_FORMATS_INFO_CHOICES)
    image = models.ImageField(upload_to='docs')
    settings = models.TextField(u'Настройки', blank=True, null=True)
    created_at = models.DateTimeField(u'Создан', auto_now_add=True)

    def get_page_params(self):
        return dict(PAGE_FORMATS_INFO)[self.page_format]

    @property
    def page_params(self):
        return self.get_page_params()

    def __unicode__(self):
        return self.title

    def get_settings(self):
        if self.settings:
            try:
                _settings = json.loads(self.settings)
                return _settings
            except (TypeError, ValueError):
                pass
        return None

    def get_settings_model(self):
        _settings = self.get_settings()
        if _settings:
            _model_data = _settings.get('model', None)
            if _model_data:
                _app_label = _model_data.get('app_label', None)
                _model_name = _model_data.get('model_name', None)
                if _app_label and _model_name:
                    _model = models.get_model(_app_label, _model_name)
                    return _model
        return None

    def get_settings_model_verbose_name(self):
        _model = self.get_settings_model()
        if _model:
            return _model._meta.verbose_name
        return None


class DocTemplateElement(models.Model):
    doc_template = models.ForeignKey(DocTemplate)
    code = models.CharField(max_length=250, blank=True, default='')
    content = models.TextField(default='', blank=True)

    left = models.IntegerField(default=0)
    top = models.IntegerField(default=0)
    width = models.PositiveIntegerField(default=None, blank=True, null=True)
    height = models.PositiveIntegerField(default=None, blank=True, null=True)

    font_size = models.PositiveIntegerField(default=14, blank=True, null=True)
    line_height = models.PositiveIntegerField(default=None, blank=True, null=True)
    letter_spacing = models.IntegerField(default=None, blank=True, null=True)

    def __unicode__(self):
        return u'%s, %s: %s' % (self.doc_template, self.code, self.content[:100])

