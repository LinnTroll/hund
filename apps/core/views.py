# -*- coding: utf-8 -*-
import os
import json
import xlwt
from tempfile import mkdtemp
from subprocess import call

from django.conf import settings
from django.db.models import Q, Count, get_model
from django.views.generic import View, TemplateView, ListView, UpdateView, CreateView, DetailView, DeleteView
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, Http404
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout

from .models import (Breed, Animal, AnimalPedigreeNumber, AnimalOwner, AnimalTitle, ShowClass,
                     ShowGroup, ShowMember, Show,
                     ShowCatalog, ShowCatalogItem,
                     DocTemplate, DocTemplateElement)
from .forms import (AnimalForm, DoctplSelectForm, AnimalPedigreeNumberForm, AnimalOwnerForm, AnimalTitleForm,
                    ShowGroupCreateForm,
                    ShowCreateForm, ShowMemberCreateForm, ShowMemberAdditionCreateForm,
                    ShowCatalogItemForm, DocTemplateForm)
from utils.utils import prepare_pedigree_number_number


class IndexView(TemplateView):
    template_name = 'frontend/index.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('core_animals_list')
        else:
            return redirect('core_login')


class LoginView(TemplateView):
    template_name = 'frontend/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('core_animals_list')
        self.form = AuthenticationForm(request, request.POST or None)
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.form.is_valid():
            user = authenticate(username=self.form.cleaned_data['username'],
                                password=self.form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('core_index')

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(LoginView, self).get_context_data(**kwargs)
        context_data['form'] = self.form
        return context_data


class LogoutView(View):
    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return redirect('core_index')


class AnimalsListView(ListView):
    extended = False
    template_name = 'frontend/animals_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')
        return super(AnimalsListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Animal.objects.order_by('breed__name', 'gender', 'birthdate')
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(animalpedigreenumber__number__icontains=search) |
                Q(name_ru__icontains=search) |
                Q(name_en__icontains=search) |
                Q(mark__icontains=search) |
                Q(chip__icontains=search) |
                Q(reg_number__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context_data = super(AnimalsListView, self).get_context_data(**kwargs)
        context_data['extended'] = self.extended
        return context_data


# Export all dogs from catalog to xls table
class AnimalsListExportXLSView(View):
    def dispatch(self, request, *args, **kwargs):
        response = HttpResponse(mimetype="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename=file.xls'

        if not request.user.is_authenticated():
            return redirect('core_index')

        our_animals = Animal.objects.filter(is_our=True)

        wb = xlwt.Workbook()
        ws = wb.add_sheet(u'Собаки')

        rc = 0

        h_style = xlwt.XFStyle()
        h_pattern = xlwt.Pattern()
        h_pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        h_pattern.pattern_fore_colour = xlwt.Style.colour_map['lavender']
        h_style.pattern = h_pattern

        alignment = xlwt.Alignment()
        alignment.vert = xlwt.Alignment.VERT_CENTER
        h_style.alignment = alignment

        ws.write(0, 0, u'№п/п', h_style)
        ws.write(0, 1, u'Порода, пол, цвет, дата вступл.', h_style)
        ws.write(0, 2, u'Кличка', h_style)
        ws.write(0, 3, u'Документы', h_style)
        ws.write(0, 4, u'Дата рождения', h_style)
        ws.write(0, 5, u'Владелец', h_style)
        ws.write(0, 6, u'Телефон, адрес, email, место работы', h_style)
        ws.write(0, 7, u'регистр. №', h_style)

        ws.row(0).height_mismatch = True
        ws.row(0).height = 22 * 20

        for r, animal in enumerate(our_animals):
            cols = [
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                [],
            ]

            # 0
            cols[0].append(u'%s' % (r + 1))

            # 1
            if animal.breed:
                cols[1].append(u'%s' % animal.breed)

            _color = animal.get_color()
            _gender_and_color = u', '.join(filter(bool, [u'%s' % animal.get_gender_label(), _color]))

            cols[1].append(_gender_and_color)

            _reg_date = animal.get_reg_date_human()
            if _reg_date:
                cols[1].append(_reg_date)

            if animal.chip:
                cols[1].append(u'Чип: %s' % animal.chip)

            if animal.mark:
                cols[1].append(u'Клеймо: %s' % animal.mark)

            # 2
            cols[2].append(u'%s' % animal.get_display())

            if animal.father:
                cols[2].append(u'Отец: %s' % animal.father.get_display())

            if animal.mother:
                cols[2].append(u'Мать: %s' % animal.mother.get_display())

            # 3
            pedigree_numbers = animal.animalpedigreenumber_set.all()
            for pedigree_number in pedigree_numbers:
                cols[3].append(u'%s' % pedigree_number.number)

            # 4
            _birthdate = animal.get_birthdate_human()
            if _birthdate:
                cols[4].append(u'%s' % _birthdate)

            # 5
            _owner = animal.get_last_owner()
            if _owner:
                cols[5].append(u'%s' % _owner.name)

            # 6
            if _owner:
                if _owner.phone:
                    cols[6].append(u'%s' % _owner.phone)
                if _owner.address:
                    cols[6].append(u'%s' % _owner.address)
                if _owner.email:
                    cols[6].append(u'%s' % _owner.email)
                if _owner.work:
                    cols[6].append(u'%s' % _owner.work)

            # 7
            if animal.reg_number:
                cols[7].append(u'%s' % animal.reg_number)

            cols_max_rows = max(map(lambda x: len(x), cols))

            for n in xrange(cols_max_rows):
                rc += 1

                for cn, col in enumerate(cols):
                    style = xlwt.XFStyle()

                    font = xlwt.Font()
                    font.height = 10 * 20

                    borders = xlwt.Borders()

                    if n == 0:
                        borders.top = xlwt.Borders.MEDIUM

                    if r == len(our_animals) - 1:
                        if n == cols_max_rows - 1:
                            borders.bottom = xlwt.Borders.MEDIUM

                    if cn == 1 and n > 0:
                        font.height = 9 * 20

                    if cn == 2 and n > 0:
                        font.height = 9 * 20

                    if cn == 4:
                        font.height = 9 * 20

                    col_val = u''

                    if n < len(col):
                        col_val = col[n]

                    style.borders = borders
                    style.font = font

                    ws.write(rc, cn, col_val, style)

        ws.col(0).width = 80 * 20
        ws.col(1).width = 400 * 20
        ws.col(2).width = 500 * 20
        ws.col(3).width = 260 * 20
        ws.col(4).width = 200 * 20
        ws.col(5).width = 400 * 20
        ws.col(6).width = 500 * 20
        ws.col(7).width = 200 * 20

        wb.save(response)

        return response


class AnimalEditView(DetailView):
    template_name = 'frontend/animal_form.html'
    model = Animal

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')
        return super(AnimalEditView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(AnimalEditView, self).get_context_data(**kwargs)
        context_data['animal_data'] = json.dumps(self.object.as_dict())
        return context_data


class AnimalAddView(TemplateView):
    template_name = 'frontend/animal_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')
        return super(AnimalAddView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(AnimalAddView, self).get_context_data(**kwargs)
        context_data['animal_data'] = json.dumps(None)
        return context_data


class DocTplListView(ListView):
    template_name = 'frontend/doctpl_list.html'
    model = DocTemplate

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')
        return super(DocTplListView, self).dispatch(request, *args, **kwargs)


class DocTplAddView(CreateView):
    template_name = 'frontend/doctpl_form.html'
    form_class = DocTemplateForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')
        return super(DocTplAddView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('core_doctpl_edit', kwargs={'pk': self.object.pk})


class DocTplEditView(UpdateView):
    mode = 'default'
    template_name = 'frontend/doctpl_form.html'
    model = DocTemplate
    form_class = DocTemplateForm
    avail_models = [
        ['core', 'animal'],
        ['core', 'showmember'],
    ]

    def dispatch(self, request, *args, **kwargs):
        if self.mode in ['print_preview', 'print_done']:
            self.model_class = None
            self.instance = None
            self.instances = []

            self._pk = request.GET.get('pk', None)
            self._pks = request.GET.get('pks', None)
            self._model = request.GET.get('model', None)

            self.pks = []

            if self._pks:
                self.pks = self._pks.split(',')

            if (self._pk or self.pks) and self._model:
                _model_bits = self._model.split('.')
                if len(_model_bits) == 2:
                    _app_label, _model_name = _model_bits
                    self.model_class = get_model(_app_label, _model_name)

                    if self.model_class:
                        if self._pk:
                            try:
                                self.instance = self.model_class.objects.get(pk=self._pk)
                            except self.model_class.DoesNotExist:
                                pass
                        if self.pks:
                            self.instances = self.model_class.objects.filter(pk__in=self.pks)
                            if self.instances.exists():
                                self.instance = self.instances[0]

            if not self.instance:
                raise Http404

        return super(DocTplEditView, self).dispatch(request, *args, **kwargs)

    def get_pathfield_data(self, instance, name):
        path_bits = name.split('__')

        inst = instance
        result = None

        for bit in path_bits:

            result = getattr(inst, bit, None)

            if hasattr(result, '__call__'):
                result = result()

            inst = result

            if result is None:
                break

        if result is not None:
            if not isinstance(result, unicode):
                result = u'%s' % result

        return result

    def get_object(self, queryset=None):
        if self.mode == 'default':
            return super(DocTplEditView, self).get_object(queryset)

        if self.mode in ['print_preview', 'print_done']:
            _object = self.model.objects.get(pk=self.request.GET['tpl'])

            _settings = None

            if (_object.settings):
                try:
                    _settings = json.loads(_object.settings)
                except (TypeError, ValueError):
                    pass

            if _settings and _settings.get('items'):
                _items = _settings['items']
                for _item in _items:
                    _item['value'] = self.get_pathfield_data(self.instance, _item['field']['name']) or ''

                _settings['items'] = _items

                _object.settings = json.dumps(_settings)

            return _object
        return None

    def get_success_url(self):
        return reverse('core_doctpl_edit', kwargs={'pk': self.object.pk})

    def get_models_data(self):
        models_list = [get_model(*x) for x in self.avail_models]
        data_list = [{
                         'app_label': x._meta.app_label,
                         'model_name': x._meta.model_name,
                         'verbose_name': x._meta.verbose_name,
                         'fields': x._print_fields_map(),
                     } for x in models_list]
        return data_list

    def get_context_data(self, **kwargs):
        context_data = super(DocTplEditView, self).get_context_data(**kwargs)
        models_data = self.get_models_data()
        context_data['models_data'] = models_data
        context_data['models_data_json'] = json.dumps(models_data)
        context_data['mode'] = self.mode
        return context_data


class DocTplSelectView(TemplateView):
    template_name = 'frontend/doctpl_select.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')
        self.form = DoctplSelectForm(request.POST or None)
        return super(DocTplSelectView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(DocTplSelectView, self).get_context_data(**kwargs)
        context_data['form'] = self.form
        return context_data


class DocTplPrintSelectView(ListView):
    template_name = 'frontend/doctpl_print_select.html'
    model = DocTemplate

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')

        self.model_class = None
        self.instance = None
        self.instances = []

        self._pk = request.GET.get('pk', None)
        self._pks = request.GET.get('pks', None)
        self._model = request.GET.get('model', None)

        self.pks = []

        if self._pks:
            self.pks = self._pks.split(',')

        if (self._pk or self.pks) and self._model:
            _model_bits = self._model.split('.')
            if len(_model_bits) == 2:
                _app_label, _model_name = _model_bits
                self.model_class = get_model(_app_label, _model_name)

                if self.model_class:
                    if self._pk:
                        try:
                            self.instance = self.model_class.objects.get(pk=self._pk)
                        except self.model_class.DoesNotExist:
                            pass
                    if self.pks:
                        self.instances = self.model_class.objects.filter(pk__in=self.pks)
                        if self.instances.exists():
                            self.instance = self.instances[0]

        if not self.instance:
            raise Http404

        return super(DocTplPrintSelectView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(DocTplPrintSelectView, self).get_context_data(**kwargs)
        context_data['model_meta'] = self.model_class._meta
        context_data['instance'] = self.instance
        context_data['pks'] = self._pks
        return context_data


# Generate document pdf for print
class DocTplPrintPDFView(View):
    def make_pdf_document(self, tmp_pdf_file, _pk, _model, _tpl, _bg, page_size, orientation):
        web_page_url = self.request.build_absolute_uri(
            u'%s?pk=%s&model=%s&tpl=%s&bg=%s' % (reverse('core_doctpl_print_done'), _pk, _model, _tpl, _bg))

        wkhtmltopdf_bin = settings.WKHTMLTOPDF_BIN
        if not isinstance(wkhtmltopdf_bin, list):
            wkhtmltopdf_bin = [wkhtmltopdf_bin, ]

        call(wkhtmltopdf_bin + [
            '-B', '0',
            '-L', '0',
            '-R', '0',
            '-T', '0',
            '--page-size', page_size,
            '--orientation', orientation,
            web_page_url,
            tmp_pdf_file
        ])

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')

        _pk = request.GET.get('pk', None)
        _pks = request.GET.get('pks', None)
        _model = request.GET['model']
        _tpl = request.GET['tpl']
        _bg = request.GET['bg']

        pks = []

        if _pks:
            pks = _pks.split(',')

        doc_tpl = DocTemplate.objects.get(pk=_tpl)

        _page_size, _orientation = doc_tpl.page_format.split('-')

        page_size = _page_size.upper()
        orientation = {'port': 'Portrait', 'album': 'Landscape'}[_orientation]
        _po = {'port': 'P', 'album': 'A'}[_orientation]

        tmp_dir = mkdtemp()

        tmp_pdf_file = None

        if len(pks) == 1:
            _pk = pks[0]
            pks = []

        if _pk:
            tmp_pdf_file = os.path.join(tmp_dir, '%s.pdf' % _model)
            self.make_pdf_document(tmp_pdf_file, _pk, _model, _tpl, _bg, page_size, orientation)

        if pks:
            pdf_pathces = []

            for pk in pks:
                _tmp_pdf_file = os.path.join(tmp_dir, '%s-%s.pdf' % (_model, pk))
                self.make_pdf_document(_tmp_pdf_file, pk, _model, _tpl, _bg, page_size, orientation)
                pdf_pathces.append(_tmp_pdf_file)

            if pdf_pathces:
                tmp_pdf_file = os.path.join(tmp_dir, '%s.pdf' % _model)
                call(['pdfunite', ] + pdf_pathces + [tmp_pdf_file, ])

        if tmp_pdf_file:
            fsock = open(tmp_pdf_file, "r").read()
            response = HttpResponse(fsock, content_type='application/pdf')

            _postfix = ''

            if _pk:
                _postfix += '-%s' % _pk

            if _bg == 'no':
                _postfix += '-nobg'

            response['Content-Disposition'] = 'attachment; filename="%s-%s-%s%s.pdf"' % (
            _model, page_size, _po, _postfix)
            return response

        raise Http404


class AjaxBreedSearchView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        q = request.GET.get('q', None)
        breeds = Breed.objects.none()
        if q:
            breeds = Breed.objects.filter(name__icontains=q)[:10]
        return HttpResponse(json.dumps([x.as_dict() for x in breeds]), content_type='application/json')


class AjaxAnimalCreateView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        errors = {}
        warnings = []
        data = json.loads(request.body)

        animal = None
        animal_id = data.get('id', None)

        try:
            animal = Animal.objects.get(pk=animal_id)
        except:
            pass

        form = AnimalForm(data, instance=animal)

        if not form.is_valid():
            errors.update(dict(form.errors))

        pedigree_numbers = filter(lambda x: x and x.get('number', None), data.get('pedigree_numbers', []))

        if len(pedigree_numbers) > 0:
            for pedigree_number in pedigree_numbers:
                ap_form = AnimalPedigreeNumberForm(data={'number': pedigree_number['number']})
                if not ap_form.is_valid():
                    error_values = ap_form.errors.values()
                    if error_values:
                        errors['pedigree_numbers'] = list(error_values[0])
                else:
                    number = pedigree_number.get('number', None)
                    if number:
                        all_animals = Animal.objects.all()
                        if animal:
                            all_animals = all_animals.exclude(pk=animal.pk)

                        prepared_number = prepare_pedigree_number_number(number)

                        exist_number_animals = all_animals.filter(
                            animalpedigreenumber__parsed_number=prepared_number).distinct()
                        if exist_number_animals.exists():
                            errors['pedigree_numbers'] = [u'Собака с таким номером родословной уже существует']

                            warnings.append({
                                'field': 'pedigree_numbers',
                                'number': number,
                                'animals': [x.as_dict() for x in exist_number_animals]
                            })
        else:
            errors['pedigree_numbers'] = [u'Вы должны ввести хотябы 1 номер родословной', ]

        owners = filter(lambda x: x and any(x.values()), data.get('owners', []))

        for owner in owners:
            owner_form = AnimalOwnerForm(data=owner)
            if not owner_form.is_valid():
                error_values = owner_form.errors.values()
                if error_values:
                    errors['owners'] = list(error_values[0])

        titles = filter(lambda x: x and any(x.values()), data.get('titles', []))

        for title in titles:
            title_form = AnimalTitleForm(data=title)
            if not title_form.is_valid():
                error_values = title_form.errors.values()
                if error_values:
                    errors['titles'] = list(error_values[0])

        if errors or warnings:
            return HttpResponse(json.dumps({
                'status': 'fail',
                'warnings': warnings,
                'errors': errors,
            }))
        else:
            animal = form.save()

            # pedigree numbers
            exists_pedigree_numbers_ids = set([x[0] for x in animal.animalpedigreenumber_set.values_list('id')])
            new_pedigree_numbers_ids = set(filter(bool, [x['id'] for x in pedigree_numbers]))

            fordel_pedigree_numbers_ids = exists_pedigree_numbers_ids - new_pedigree_numbers_ids

            if fordel_pedigree_numbers_ids:
                AnimalPedigreeNumber.objects.filter(pk__in=fordel_pedigree_numbers_ids).delete()

            for pedigree_number in pedigree_numbers:
                pedigree_number_instance = None

                pedigree_number_id = pedigree_number.get('id', None)
                if pedigree_number_id:
                    try:
                        pedigree_number_instance = AnimalPedigreeNumber.objects.get(pk=pedigree_number_id)
                    except AnimalPedigreeNumber.DoesNotExist:
                        pass

                if pedigree_number_instance:
                    if pedigree_number_instance.number != pedigree_number['number']:
                        pedigree_number_instance.number = pedigree_number['number']
                        pedigree_number_instance.save()
                else:
                    AnimalPedigreeNumber.objects.create(number=pedigree_number['number'], animal=animal)

            # owners
            exists_owners_ids = set([x[0] for x in animal.animalowner_set.values_list('id')])
            new_owners_ids = set(filter(bool, [x['id'] for x in owners]))

            fordel_owners_ids = exists_owners_ids - new_owners_ids

            if fordel_owners_ids:
                AnimalOwner.objects.filter(pk__in=fordel_owners_ids).delete()

            for owner in owners:
                owner_instance = None

                owner_id = owner.get('id', None)
                if owner_id:
                    try:
                        owner_instance = AnimalOwner.objects.get(pk=owner_id)
                    except AnimalOwner.DoesNotExist:
                        pass

                if owner_instance:
                    owner_instance.name = owner['name']
                    owner_instance.address = owner['address']
                    owner_instance.phone = owner['phone']
                    owner_instance.email = owner['email']
                    owner_instance.work = owner['work']
                    owner_instance.save()
                else:
                    AnimalOwner.objects.create(
                        animal=animal,
                        name=owner['name'],
                        address=owner['address'],
                        phone=owner['phone'],
                        email=owner['email'],
                    )

            # titles
            exists_titles_ids = set([x[0] for x in animal.animaltitle_set.values_list('id')])
            new_titles_ids = set(filter(bool, [x['id'] for x in titles]))

            fordel_titles_ids = exists_titles_ids - new_titles_ids

            if fordel_titles_ids:
                AnimalTitle.objects.filter(pk__in=fordel_titles_ids).delete()

            for title in titles:
                title_instance = None

                title_id = title.get('id', None)
                if title_id:
                    try:
                        title_instance = AnimalTitle.objects.get(pk=title_id)
                    except AnimalTitle.DoesNotExist:
                        pass

                if title_instance:
                    title_instance.title = title['title']
                    title_instance.info = title['info']
                    title_instance.save()
                else:
                    AnimalTitle.objects.create(
                        animal=animal,
                        title=title['title'],
                        info=title['info'],
                    )

            ancestors = data.get('ancestors', None)

            ancestors[''] = {'pk': animal.pk}

            real_pairs = []

            for key, ancestor in ancestors.items():
                if key:
                    child_key = key[:len(key) - 1]
                    _child = ancestors.get(child_key, None)
                    _gender = key[len(key) - 1]
                    _parent_field = {'m': 'father', 'f': 'mother'}[_gender]

                    if _child and ancestor:
                        real_pairs.append([child_key, key])
                        _child_pk = _child.get('pk', None)
                        _parent_pk = ancestor.get('pk', None)
                        if _child_pk and _parent_pk:
                            _child_obj = Animal.objects.get(pk=_child_pk)
                            _parent_obj = Animal.objects.get(pk=_parent_pk)
                            setattr(_child_obj, _parent_field, _parent_obj)
                            _child_obj.save()

            animal = Animal.objects.get(pk=animal.pk)

            ancestors = animal.get_ancestors()
            ancestors[''] = {'pk': animal.pk}

            for key, ancestor in ancestors.items():
                if key:
                    child_key = key[:len(key) - 1]
                    _child = ancestors.get(child_key, None)
                    _gender = key[len(key) - 1]
                    _parent_field = {'m': 'father', 'f': 'mother'}[_gender]

                    if _child and ancestor:
                        if not [child_key, key] in real_pairs:
                            _child_pk = _child.get('pk', None)
                            if _child_pk:
                                _child_obj = Animal.objects.get(pk=_child_pk)
                                setattr(_child_obj, _parent_field, None)
                                _child_obj.save()

            return HttpResponse(json.dumps({
                'status': 'success',
                'pk': animal.pk,
                'urls': {
                    'core_animals_list': reverse('core_animals_list'),
                    'core_animals_edit': reverse('core_animals_edit', kwargs={'pk': animal.pk}),
                },
                'data': animal.as_dict(),
            }))


class AjaxAnimalSearchView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        q = request.GET.get('q', None)
        gender = request.GET.get('gender', None)
        breed = request.GET.get('breed', None)
        animals = Animal.objects.none()
        if q:
            animals = Animal.objects.all()
            if gender:
                animals = animals.filter(gender=gender)
            if breed:
                animals = animals.filter(breed__pk=breed)
            animals = animals.filter(
                Q(name_ru__icontains=q) |
                Q(name_en__icontains=q) |
                Q(mark__icontains=q) |
                Q(chip__icontains=q) |
                Q(animalpedigreenumber__number__icontains=q)
            ).distinct()[:10]
        return HttpResponse(json.dumps([x.as_dict() for x in animals]), content_type='application/json')


class ShowGroupsListView(ListView):
    model = ShowGroup
    template_name = 'frontend/show_group_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')
        return super(ShowGroupsListView, self).dispatch(request, *args, **kwargs)


class ShowGroupsAddView(CreateView):
    model = Show
    form_class = ShowGroupCreateForm
    template_name = 'frontend/show_group_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')
        return super(ShowGroupsAddView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('core_show_groups_list')


class ShowGroupsEditView(UpdateView):
    model = ShowGroup
    form_class = ShowGroupCreateForm
    template_name = 'frontend/show_group_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')
        return super(ShowGroupsEditView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('core_show_groups_edit', kwargs={'pk': self.object.pk})

    def get_has_add_list(self):
        add_items = ShowMember.objects.filter(show__group=self.object, add_list=True)
        return add_items.exists()

    def get_context_data(self, **kwargs):
        context_data = super(ShowGroupsEditView, self).get_context_data(**kwargs)
        context_data['has_add_list'] = self.get_has_add_list()
        return context_data


class ShowGroupsEditCheckInView(TemplateView):
    checkin_mode = 'do_close'
    template_name = 'frontend/show_group_checkin.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')
        return super(ShowGroupsEditCheckInView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.group = ShowGroup.objects.get(pk=self.kwargs['pk'])
        if not request.user.is_authenticated():
            return HttpResponseForbidden()
        action = request.POST.get('action', None)
        if action:
            if action == 'close':
                if not self.group.check_in:
                    self.group.check_in = True
                    self.group.numerate_members()
                    showcatalog = ShowCatalog.objects.create()
                    for show in self.group.show_set.all():
                        ShowCatalogItem.objects.create(catalog=showcatalog, show=show)
                    self.group.catalog = showcatalog
                    self.group.save()
            if action == 'open':
                if self.group.check_in:
                    self.group.check_in = False
                    self.group.catalog = None
                    for show in self.group.show_set.all():
                        for show_member in show.showmember_set.all():
                            show_member.number = None
                            show_member.save()
                    self.group.save()
            return redirect(reverse('core_show_groups_edit', kwargs={'pk': self.group.pk}))
        return HttpResponseBadRequest()

    def get_context_data(self, **kwargs):
        context_data = super(ShowGroupsEditCheckInView, self).get_context_data(**kwargs)
        context_data['object'] = ShowGroup.objects.get(pk=self.kwargs['pk'])
        context_data['checkin_mode'] = self.checkin_mode
        return context_data


class ShowGroupDeleteView(DeleteView):
    model = ShowGroup
    template_name = 'frontend/show_group_delete.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')
        return super(ShowGroupDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('core_show_groups_list')


class ShowAddView(CreateView):
    model = Show
    form_class = ShowCreateForm
    template_name = 'frontend/show_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.group = ShowGroup.objects.get(pk=self.kwargs['group'])
        if not request.user.is_authenticated():
            return redirect('core_index')
        return super(ShowAddView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.group = self.group
        return super(ShowAddView, self).form_valid(form)

    def get_success_url(self):
        return reverse('core_show_groups_edit', kwargs={'pk': self.group.pk})

    def get_context_data(self, **kwargs):
        context_data = super(ShowAddView, self).get_context_data(**kwargs)
        context_data['group'] = self.group
        return context_data


class ShowEditView(UpdateView):
    model = Show
    form_class = ShowCreateForm
    template_name = 'frontend/show_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.group = ShowGroup.objects.get(pk=self.kwargs['group'])
        if not request.user.is_authenticated():
            return redirect('core_index')
        return super(ShowEditView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.group = self.group

        for show_member in self.object.showmember_set.all():
            for field in ['res_rate', 'res_title']:
                res_name = show_member.res_form[field].html_name
                if res_name in self.request.POST:
                    res_val = self.request.POST[res_name] or None
                    setattr(show_member, field, res_val)
                    show_member.save()

        return super(ShowEditView, self).form_valid(form)

    def get_success_url(self):
        return reverse('core_show_edit', kwargs={'group': self.group.pk, 'pk': self.object.pk})

    def get_object_list(self):
        return self.object.showmember_set.filter(add_list=False)

    def get_object_add_list(self):
        return self.object.showmember_set.filter(add_list=True).order_by('number')

    def get_context_data(self, **kwargs):
        context_data = super(ShowEditView, self).get_context_data(**kwargs)
        context_data['object_list'] = self.get_object_list()
        context_data['object_add_list'] = self.get_object_add_list()
        context_data['group'] = self.group
        return context_data


class ShowDeleteView(DeleteView):
    model = Show
    template_name = 'frontend/show_delete.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')
        return super(ShowDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('core_show_groups_edit', kwargs={'pk': self.kwargs['group']})


class ShowMemberCreateView(CreateView):
    model = ShowMember
    # form_class =
    template_name = 'frontend/show_member_form.html'

    def get_parent_instance(self, *args, **kwargs):
        return Show.objects.get(pk=kwargs['pk'])

    def dispatch(self, request, *args, **kwargs):
        self.group = ShowGroup.objects.get(pk=self.kwargs['group'])
        if not request.user.is_authenticated():
            return redirect('core_index')

        self.parent_instance = self.get_parent_instance(*args, **kwargs)
        # print "###", self.group.check_in
        return super(ShowMemberCreateView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        if self.group.check_in:
            return ShowMemberAdditionCreateForm
        else:
            return ShowMemberCreateForm

    def get_form(self, form_class):
        if self.group.check_in:
            print form_class
            return form_class(self.request.POST or None, show=self.parent_instance)
        else:
            return form_class(self.request.POST or None)

    def form_valid(self, form):
        form.instance.show = self.parent_instance
        self.object = form.save()
        return super(ShowMemberCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('core_show_edit', kwargs={'group': self.group.pk, 'pk': self.parent_instance.pk})

    def get_context_data(self, **kwargs):
        context_data = super(ShowMemberCreateView, self).get_context_data(**kwargs)
        context_data['group'] = self.group
        return context_data


class ShowMemberDeleteView(DeleteView):
    model = ShowMember
    template_name = 'frontend/show_member_delete.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')
        return super(ShowMemberDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('core_show_edit', kwargs={'pk': self.object.show.pk, 'group': self.object.show.group.pk})


class ShowPrintMembersView(TemplateView):
    template_name = 'documents/members/index.html'

    def get_context_data(self, **kwargs):
        context_data = super(ShowPrintMembersView, self).get_context_data(**kwargs)
        show = Show.objects.get(pk=kwargs['pk'])
        members = ShowMember.objects.filter(show=show)
        context_data['show'] = show
        context_data['members'] = members
        return context_data


class ShowPrintMembersPDFView(View):
    def dispatch(self, request, *args, **kwargs):
        show = Show.objects.get(pk=kwargs['pk'])
        web_page_url = request.build_absolute_uri(reverse('core_show_members_print',
                                                          kwargs={'pk': kwargs['pk'], 'group': kwargs['group']}))

        wkhtmltopdf_bin = settings.WKHTMLTOPDF_BIN
        if not isinstance(wkhtmltopdf_bin, list):
            wkhtmltopdf_bin = [wkhtmltopdf_bin, ]

        tmp_dir = mkdtemp()

        tmp_pdf_file = os.path.join(tmp_dir, 'show-%s.pdf' % show.pk)

        call(wkhtmltopdf_bin + [
            '--page-size', 'A4',
            '--orientation', 'Portrait',
            web_page_url,
            tmp_pdf_file
        ])

        fsock = open(tmp_pdf_file, "r").read()
        response = HttpResponse(fsock, content_type='application/pdf')

        response['Content-Disposition'] = 'attachment; filename="show-%s.pdf"' % show.pk
        return response


class ShowPrintCertlistView(TemplateView):
    template_name = 'documents/certlist/index.html'

    def get_context_data(self, **kwargs):
        context_data = super(ShowPrintCertlistView, self).get_context_data(**kwargs)
        group = ShowGroup.objects.get(pk=kwargs['pk'])
        members = ShowMember.objects.filter(show__group=group, res_title=kwargs['title']).order_by('number')
        shows = Show.objects.filter(group=group)
        context_data['members'] = members
        context_data['shows'] = shows
        context_data['title_name'] = dict(ShowMember.TITLE_CHOICES)[kwargs['title']]
        return context_data


class ShowPrintCertlistPDFView(View):
    def dispatch(self, request, *args, **kwargs):
        group = ShowGroup.objects.get(pk=kwargs['pk'])
        web_page_url = request.build_absolute_uri(reverse('core_show_certlist_print',
                                                          kwargs={'pk': kwargs['pk'], 'title': kwargs['title']}))

        wkhtmltopdf_bin = settings.WKHTMLTOPDF_BIN
        if not isinstance(wkhtmltopdf_bin, list):
            wkhtmltopdf_bin = [wkhtmltopdf_bin, ]

        tmp_dir = mkdtemp()

        tmp_pdf_file = os.path.join(tmp_dir, 'certlist-%s.pdf' % group.pk)

        call(wkhtmltopdf_bin + [
            '--page-size', 'A4',
            '--orientation', 'Portrait',
            web_page_url,
            tmp_pdf_file
        ])

        fsock = open(tmp_pdf_file, "r").read()
        response = HttpResponse(fsock, content_type='application/pdf')

        response['Content-Disposition'] = 'attachment; filename="certlist-%s.pdf"' % group.pk
        return response


class ShowCertlistSetNumbersView(TemplateView):
    template_name = 'frontend/show_group_setcertnumbers.html'

    def dispatch(self, request, *args, **kwargs):
        self.group = ShowGroup.objects.get(pk=kwargs['pk'])
        self.title = kwargs['title']
        self.members = ShowMember.objects.filter(show__group=self.group, res_title=self.title)
        return super(ShowCertlistSetNumbersView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(ShowCertlistSetNumbersView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        valid_pks = [int(x.pk) for x in self.members]

        for key, val in request.POST.items():
            if key.startswith('member_cert_'):
                pk = int(key[12:])
                if pk in valid_pks:
                    _member = ShowMember.objects.get(pk=pk)
                    _member.cert_number = val
                    _member.save()
        return redirect(reverse('core_show_certlist_set_numbers', kwargs={'pk': self.group.pk, 'title': self.title}))
        # return super(ShowCertlistSetNumbersView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(ShowCertlistSetNumbersView, self).get_context_data(**kwargs)
        context_data['members'] = self.members
        context_data['group'] = self.group
        context_data['title_name'] = dict(ShowMember.TITLE_CHOICES)[self.title]
        return context_data


class CatalogListView(ListView):
    template_name = 'frontend/show_catalog_list.html'
    model = ShowCatalog

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')
        return super(CatalogListView, self).dispatch(request, *args, **kwargs)


class CatalogAddView(CreateView):
    template_name = 'frontend/show_catalog_form.html'
    model = ShowCatalog

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')
        return super(CatalogAddView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('core_show_catalogs_detail', kwargs={'pk': self.object.pk})


class CatalogDetailView(DetailView):
    template_name = 'frontend/show_catalog_detail.html'
    model = ShowCatalog

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')
        return super(CatalogDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(CatalogDetailView, self).get_context_data(**kwargs)
        context_data['showitems'] = self.object.showcatalogitem_set.all()
        return context_data


class CatalogAddShowitemlView(CreateView):
    template_name = 'frontend/show_catalog_addshowitem.html'
    model = ShowCatalogItem
    form_class = ShowCatalogItemForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')

        self.showcatalog = ShowCatalog.objects.get(pk=kwargs['pk'])
        return super(CatalogAddShowitemlView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.catalog = self.showcatalog
        form.save()
        return super(CatalogAddShowitemlView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context_data = super(CatalogAddShowitemlView, self).get_context_data(**kwargs)
        context_data['object'] = self.showcatalog
        return context_data

    def get_success_url(self):
        return reverse('core_show_catalogs_detail', kwargs={'pk': self.showcatalog.pk})


class ExportCatalogHTMLView(DetailView):
    model = ShowCatalog
    template_name = 'documents/catalog/index.html'

    def get_members(self):
        add_list = False
        if self.request.GET.get('add_list', None) == 'yes':
            add_list = True

        members = []
        for catalogitem in self.object.showcatalogitem_set.all():
            showmembers = ShowMember.objects.filter(show__pk=catalogitem.show.pk, add_list=add_list)
            for showmember in showmembers:
                showmember.show = catalogitem.show
            members += list(showmembers)
        return members

    def get_context_data(self, **kwargs):
        context_data = super(ExportCatalogHTMLView, self).get_context_data(**kwargs)
        context_data['members'] = self.get_members()
        return context_data


class ExportCatalogPDFView(View):
    def get(self, request, *args, **kwargs):
        mode = request.GET.get('mode', 'native')
        psize = request.GET.get('psize', 'A5')
        pside = request.GET.get('pside', None)

        web_page_url = request.build_absolute_uri(reverse('core_export_catalog_html', kwargs={'pk': kwargs['pk']}))

        if request.GET.get('add_list', None):
            web_page_url = u'%s?add_list=%s' % (web_page_url, request.GET['add_list'])

        wkhtmltopdf_bin = settings.WKHTMLTOPDF_BIN
        if not isinstance(wkhtmltopdf_bin, list):
            wkhtmltopdf_bin = [wkhtmltopdf_bin, ]
        tmp_dir = mkdtemp()

        fn_postfix = ''

        tmp_pdf_file = os.path.join(tmp_dir, 'catalog.pdf')
        tmp_pdf_book_file = os.path.join(tmp_dir, 'catalog-book.pdf')
        tmp_ps_orig_file = os.path.join(tmp_dir, 'catalog.ps')
        tmp_ps_book_file = os.path.join(tmp_dir, 'catalog-book.ps')
        tmp_ps_snup_file = os.path.join(tmp_dir, 'catalog-snup.ps')
        tmp_ps_select_file = os.path.join(tmp_dir, 'catalog-select.ps')

        call(wkhtmltopdf_bin + [
            '--page-size', psize,
            '--orientation', 'Portrait',
            web_page_url,
            tmp_pdf_file
        ])

        if mode == 'book':
            call(['pdf2ps', tmp_pdf_file, tmp_ps_orig_file])
            call(['psbook', tmp_ps_orig_file, tmp_ps_book_file])
            call(['psnup', '-l', '-2', '-s1', tmp_ps_book_file, tmp_ps_snup_file])
            if pside:
                call(['psselect', '-%s' % pside, tmp_ps_snup_file, tmp_ps_select_file])
                tmp_ps_snup_file = tmp_ps_select_file
                fn_postfix = '-%s' % pside
            call(['ps2pdf', '-dAutoRotatePages=0', tmp_ps_snup_file, tmp_pdf_book_file])
            result_pdf = tmp_pdf_book_file
        else:
            result_pdf = tmp_pdf_file

        fsock = open(result_pdf, "r").read()
        response = HttpResponse(fsock, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="catalog-%s%s.pdf"' % (mode, fn_postfix)
        return response


class AnimalsStatisticView(TemplateView):
    template_name = 'frontend/statistic.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('core_index')
        return super(AnimalsStatisticView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(AnimalsStatisticView, self).get_context_data(**kwargs)
        animals = Animal.objects.all()
        animals_our = animals.filter(is_our=True)
        context_data['total_count'] = animals.count()
        context_data['total_count_gm'] = animals.filter(gender='m').count()
        context_data['total_count_gf'] = animals.filter(gender='f').count()
        context_data['our_count'] = animals_our.count()
        context_data['reg_count'] = animals_our.exclude(reg_number=None).count()
        context_data['breed_count'] = animals.values('breed').annotate(Count('breed')).count()
        return context_data
