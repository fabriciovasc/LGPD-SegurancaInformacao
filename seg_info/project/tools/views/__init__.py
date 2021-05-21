from django.apps import apps
from django.views.generic.edit import FormMixin
from django.views.generic.list import ListView

from .mixins import PaginationQueryStringMixin


get_model = apps.get_model


class SearchFormListView(PaginationQueryStringMixin, FormMixin, ListView):
    '''
        Classe de view para colocar um filtro
        na ListView
    '''

    http_method_names = ['get']
    filter_by_user = False
    by_user_method = 'by_user'

    def get_form_kwargs(self):

        kw = super().get_form_kwargs()
        kw['data'] = {}
        if self.request.GET:
            kw['data'] = self.request.GET
        elif kw['initial']:
            kw['data'] = kw['initial']
        return kw

    def get_form(self, form_class):
        return form_class(**self.get_form_kwargs())

    def get_queryset(self):
        if self.form.is_valid():
            object_list = self.form.get_result_queryset()
        else:
            object_list = self.form.Meta.base_qs.none()

        if self.filter_by_user:
            object_list = getattr(object_list, self.by_user_method)(self.request.user)

        return object_list

    def get(self, request, *args, **kwargs):
        self.form = self.get_form(self.get_form_class())
        self.object_list = self.get_queryset()

        context = self.get_context_data(
            object_list=self.object_list,
            form=self.form,
            url_params=request.GET.urlencode()
        )
        return self.render_to_response(context)
