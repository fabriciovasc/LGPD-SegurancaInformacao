# coding: utf-8

from collections import OrderedDict

from django.views import generic
from django.views.generic import edit

from tools import views as tools_views
from tools.views import mixins as tools_mixins
from tools.views import multiform as tools_multiform


class BaseView(
    tools_mixins.MenuMixin,
    tools_mixins.PageInfoMixin
):
    pass


class BaseDetailView(
    BaseView,
    tools_mixins.GetModelMixin,
    tools_mixins.CreateUpdateURLMixin,
    tools_mixins.ListURLMixin,
    generic.DetailView
):
    url_delete_redirect = None
    show_btn_delete = True
    number_of_columns = 3
    fields = []
    exclude_fields = [
        "id",
        "user_add",
        "user_upd",
        "date_add",
        "date_upd",
    ]

    def get_url_delete_redirect(self):
        return self.url_delete_redirect

    def get_show_btn_delete(self):
        return self.show_btn_delete

    def get_exclude_fields(self):
        return self.exclude_fields

    def get_fields(self):
        meta_fields_names = [f.name for f in self.model._meta.fields]
        if self.fields:
            fields = []
            for f in self.fields:
                if f in meta_fields_names:
                    fields.append(self.model._meta.get_field(f))
            return fields
        else:
            return self.model._meta.fields

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        data = OrderedDict()
        for f in self.get_fields():
            if f.name in self.get_exclude_fields():
                continue
            if f.choices:
                value = getattr(self.object, "get_%s_display" % f.name)()
            else:
                value = getattr(self.object, f.name)
            data[f.name] = (f.verbose_name, value)
        ctx['data'] = self.data_as_columns(data.values())
        app_model = "%s.%s" % (self.model._meta.app_label, self.model._meta.model_name)
        ctx['app_model'] = app_model
        ctx['url_delete_redirect'] = self.get_url_delete_redirect()
        ctx['show_btn_delete'] = self.show_btn_delete
        return ctx

    def data_as_columns(self, items):
        """Recebe uma tupla (field_name, value) retorna lista com colunas
        contendo cada item da tupla passada."""

        try:
            items = list(items)
        except (ValueError, TypeError):
            return [items]
        item_gen = (n for n in items)
        rows = []
        can_iterate = True
        while can_iterate:
            col = []
            rows.append(col)
            for i in range(self.number_of_columns):
                try:
                    col.append(next(item_gen))
                except StopIteration:
                    can_iterate = False
        return rows


class BaseListView(
    BaseView,
    tools_mixins.GetModelMixin,
    tools_mixins.CreateUpdateURLMixin,
    tools_mixins.DetailURLMixin,
    tools_views.SearchFormListView,
):
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        if 'paginate_by' in self.request.GET:
            self.request.session['paginate_by'] = int(self.request.GET['paginate_by'])
        return super(BaseListView, self).get(request, *args, **kwargs)

    def get_fields(self):
        fields = list(self.form.fields.keys())
        try:
            fields.remove('q')
        except ValueError:
            pass
        try:
            fields.remove('order_by')
        except ValueError:
            pass
        return fields

    def get_context_data(self, *args, **kwargs):
        self.model = self.get_model()
        ctx = super(BaseListView, self).get_context_data(*args, **kwargs)
        app_model = "%s.%s" % (self.model._meta.app_label, self.model._meta.model_name)
        ctx['request_path'] = self.request.path
        ctx['total_object_list'] = self.form.Meta.base_qs.all().count()
        ctx['total_filter_list'] = ctx['page_obj'].paginator.count
        ctx['app_model'] = app_model
        ctx['has_advanced_search'] = len(self.get_fields()) >= 1
        ctx['paginate_by'] = self.get_paginate_by(None)
        ctx['order_by'] = self.request.GET.get('order_by', None)
        return ctx

    def get_paginate_by(self, queryset):
        if 'paginate_by' in self.request.session:
            return int(self.request.session['paginate_by'])
        if 'paginate_by' in self.request.GET:
            return int(self.request.GET['paginate_by'])
        return self.paginate_by


class BaseCreateView(
    BaseView,
    tools_mixins.SuccessURLMixin,
    tools_mixins.FormMessagesMixin,
    tools_mixins.UserAddUpdViewMixin,
    tools_mixins.AddWidgetViewForm,
    tools_mixins.GetModelMixin,
    tools_mixins.ListURLMixin,
    edit.CreateView,
):
    pass


class BaseUpdateView(
    BaseView,
    tools_mixins.SuccessURLMixin,
    tools_mixins.FormMessagesMixin,
    tools_mixins.UserAddUpdViewMixin,
    tools_mixins.AddWidgetViewForm,
    tools_mixins.GetModelMixin,
    tools_mixins.ListURLMixin,
    tools_mixins.DetailURLMixin,
    edit.UpdateView
):
    pass


class BaseFormsetCreateView(
    BaseView,
    tools_mixins.UserAddUpdViewMixin,
    tools_mixins.GetModelMixin,
    tools_mixins.ListURLMixin,
    tools_multiform.FormsetsMixin,
    edit.CreateView
):
    def get_formset_kwargs(self):
        kw = self.get_form_kwargs()
        kw[self.get_model_name()] = self.get_object()
        return kw

    def get_model_name(self):
        return self.model._meta.model_name


class BaseFormsetUpdateView(
    BaseView,
    tools_mixins.UserAddUpdViewMixin,
    tools_mixins.GetModelMixin,
    tools_mixins.ListURLMixin,
    tools_multiform.FormsetsMixin,
    edit.UpdateView
):
    def get_formset_kwargs(self):
        kw = self.get_form_kwargs()
        kw[self.get_model_name()] = self.get_object()
        return kw

    def get_model_name(self):
        return self.model._meta.model_name
