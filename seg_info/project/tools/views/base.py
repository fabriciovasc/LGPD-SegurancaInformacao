# coding: utf-8
from django.views.generic import edit

from tools import views as tools_views
from tools.views import mixins as tools_mixins


class BaseView(
    tools_mixins.MenuMixin,
):
    pass


class BaseListView(
    BaseView,
    tools_mixins.GetModelMixin,
    tools_mixins.CreateUpdateURLMixin,
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
    tools_mixins.UserAddUpdViewMixin,
    tools_mixins.GetModelMixin,
    tools_mixins.ListURLMixin,
    edit.CreateView,
):
    pass


class BaseUpdateView(
    BaseView,
    tools_mixins.SuccessURLMixin,
    tools_mixins.UserAddUpdViewMixin,
    tools_mixins.GetModelMixin,
    tools_mixins.ListURLMixin,
    edit.UpdateView
):
    pass
