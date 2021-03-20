from django import forms as dj_forms
from django.contrib import messages
from django.db import transaction
from django.forms import models as model_forms
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.base import ContextMixin
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import ProcessFormView

from tools.forms import CustomInlineFormSet


class MultiFormMixin(ContextMixin):
    form_classes = {}
    prefixes = {}
    success_urls = {}
    grouped_forms = {}
    initial = {}
    prefix = None
    success_url = None

    def get_form_classes(self):
        return self.form_classes

    def get_forms(self, form_classes, form_names=None, bind_all=False):
        return dict([(key, self._create_form(key, klass, (form_names and key in form_names) or bind_all))
                     for key, klass in form_classes.items()])

    def get_form_kwargs(self, form_name, bind_form=False):
        kwargs = {}
        individual_kwargs = {}
        individual_kwargs_name = 'get_%s_form_kwargs' % form_name
        if hasattr(self, individual_kwargs_name):
            individual_kwargs = getattr(self, individual_kwargs_name)()

        kwargs.update({'initial': self.get_initial(form_name)})
        kwargs.update({'prefix': self.get_prefix(form_name)})

        if bind_form:
            kwargs.update(self._bind_form_data())

        kwargs.update(individual_kwargs)
        return kwargs

    def forms_valid(self, forms, form_name=None, form_names=None):
        if form_name:
            form_valid_method = '%s_form_valid' % form_name
            if hasattr(self, form_valid_method):
                return getattr(self, form_valid_method)(forms[form_name])
            else:
                return HttpResponseRedirect(self.get_success_url(form_name))
        else:
            for form_name in form_names:
                if hasattr(self, form_valid_method):
                    getattr(self, form_valid_method)(forms[form_name])
            return HttpResponseRedirect(self.get_success_url(form_name))

    def forms_invalid(self, forms):
        return self.render_to_response(self.get_context_data(forms=forms))

    def get_initial(self, form_name):
        initial_method = 'get_%s_initial' % form_name
        if hasattr(self, initial_method):
            return getattr(self, initial_method)()
        else:
            return self.initial.copy()

    def get_prefix(self, form_name):
        return self.prefixes.get(form_name, self.prefix)

    def get_success_url(self, form_name=None):
        return self.success_urls.get(form_name, self.success_url)

    def _create_form(self, form_name, klass, bind_form):
        form_kwargs = self.get_form_kwargs(form_name, bind_form)
        form_create_method = 'create_%s_form' % form_name
        if hasattr(self, form_create_method):
            form = getattr(self, form_create_method)(**form_kwargs)
        else:
            form = klass(**form_kwargs)
        return form

    def _bind_form_data(self):
        if self.request.method in ('POST', 'PUT'):
            return{'data': self.request.POST,
                   'files': self.request.FILES, }
        return {}


class ProcessMultipleFormsView(ProcessFormView):

    def get(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        forms = self.get_forms(form_classes)
        return self.render_to_response(self.get_context_data(forms=forms))

    def post(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        form_name = request.POST.get('action')
        if self._individual_exists(form_name):
            return self._process_individual_form(form_name, form_classes)
        elif self._group_exists(form_name):
            return self._process_grouped_forms(form_name, form_classes)
        else:
            return self._process_all_forms(form_classes)

    def _individual_exists(self, form_name):
        return form_name in self.form_classes

    def _group_exists(self, group_name):
        return group_name in self.grouped_forms

    def _process_individual_form(self, form_name, form_classes):
        forms = self.get_forms(form_classes, (form_name,))
        form = forms.get(form_name)
        if not form:
            return HttpResponseForbidden()
        elif form.is_valid():
            return self.forms_valid(forms, form_name)
        else:
            return self.forms_invalid(forms)

    def _process_grouped_forms(self, group_name, form_classes):
        form_names = [
            form_name
            for form_name in self.grouped_forms[group_name]
            if form_name in form_classes.keys()
        ]
        forms = self.get_forms(form_classes, form_names)
        if all([forms.get(form_name).is_valid() for form_name in form_names]):
            return self.forms_valid(forms, form_names=form_names)
        else:
            return self.forms_invalid(forms)

    def _process_all_forms(self, form_classes):
        forms = self.get_forms(form_classes, None, True)
        if all([form.is_valid() for form in forms.values()]):
            return self.forms_valid(forms, form_names=self.form_classes.keys())
        else:
            return self.forms_invalid(forms)


class BaseMultiFormsView(
    TemplateResponseMixin,
    MultiFormMixin,
    ProcessMultipleFormsView
):
    pass


class MultiFormsView(BaseMultiFormsView):

    """
    A view for displaying several forms, and rendering a template response.
    """


class MultiFormsModelView(BaseMultiFormsView):
    pk_url_kwargs = {}
    models = {}
    fields = {}

    def __init__(self, *args, **kwargs):
        self.objects = None
        super().__init__(*args, **kwargs)

    def get_model(self, form_name):
        try:
            return self.models[form_name]
        except KeyError:
            return self.form_classes[form_name]._meta.model

    def get_pk_url_kwargs(self):
        kwargs = {}
        for form_name in self.form_classes:
            kwargs[form_name] = "%s_pk" % form_name
        for name in self.models:
            kwargs[name] = "%s_pk" % name
        for name, kwarg in self.pk_url_kwargs.items():
            kwargs[name] = kwarg
        return kwargs

    def get_objects(self):
        if self.objects:
            return self.objects
        objects = {}
        for obj_name, kwarg in self.get_pk_url_kwargs().items():
            model = self.get_model(obj_name)
            if self.kwargs[kwarg] == '0':
                obj = None
            else:
                obj = get_object_or_404(model, pk=self.kwargs[kwarg])
            objects[obj_name] = obj
        self.objects = objects
        return objects

    def get_object(self, form_name):
        if self.objects:
            return self.objects[form_name]
        else:
            return self.get_objects()[form_name]

    def get_form_kwargs(self, form_name, bind_form):
        kwargs = super().get_form_kwargs(form_name, bind_form)
        kwargs['instance'] = self.get_object(form_name)
        return kwargs

    def get(self, request, *args, **kwargs):
        self.objects = self.get_objects()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.objects = self.get_objects()
        return super().post(request, *args, **kwargs)

    def forms_valid(self, forms, form_name=None, form_names=None):
        if form_name:
            form_valid_method = '%s_form_valid' % form_name
            if hasattr(self, form_valid_method):
                return getattr(self, form_valid_method)(forms[form_name])
            else:
                self.objects[form_name] = forms[form_name].save()
                return HttpResponseRedirect(self.get_success_url(form_name))
        else:
            for form_name in form_names:
                self.objects[form_name] = forms[form_name].save()
            return HttpResponseRedirect(self.get_success_url(form_name))

    def get_form_classes(self):
        if self.models:
            for name, model in self.models.items():
                if name not in self.form_classes:
                    self.form_classes[name] = model_forms.modelform_factory(
                        self.models.get(name),
                        fields=self.fields.get(name, '__all__')
                    )
        return self.form_classes


class FormsetsMixin(object):
    """Mixin for rendering multiple formsets with foreign keys (inline formsets)

        Attributes
            formset_classes(list(ModelForm)): ModelForm Classes to produce
               inline formsets.

        Author: @Bruno
        Improvements: @zokis
    """
    failure_message = 'Verifique os erros abaixo e corríja-os antes de enviar os dados novamente.'
    success_message = 'Dados salvos com sucesso!'
    formset_classes = []
    custom_inline_formset = CustomInlineFormSet
    min_num = 1
    extra = 0
    max_num = 5

    def get_formset(self, formset_class):
        RelatedFormSet = dj_forms.inlineformset_factory(
            self.model,
            formset_class.Meta.model,
            formset_class,
            self.custom_inline_formset,
            min_num=self.min_num,
            extra=self.extra,
            max_num=self.max_num
        )
        modelformset = RelatedFormSet(
            **self.get_formset_kwargs()
        )
        return {
            formset_class.__name__.lower() + 'set': modelformset
        }

    def get_object(self, qs=None):
        if self.pk_url_kwarg in self.kwargs:
            return super().get_object(qs)
        return None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        for formset_class in self.formset_classes:
            context.update(self.get_formset(formset_class))
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        context = self.get_context_data()
        forms = {}
        for formset_class in self.formset_classes:
            forms.update(self.get_formset(formset_class))
        context.update(forms)
        formset_is_valid = all(formset.is_valid() for formset in forms.values())
        if form.is_valid() and formset_is_valid:
            return self.form_valid(form, forms, context)
        else:
            return self.form_invalid(form, forms, context)

    def form_valid(self, form, forms, context):
        try:
            with transaction.atomic():
                self.object = instance = form.save()
                for formset in forms.values():
                    formset.instance = instance
                    formset.save()
            success_message = self.get_success_message(form.cleaned_data)
            if success_message:
                messages.success(self.request, success_message)

        except Exception:
            return self.form_invalid(form, forms, context)

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, forms, context):
        failure_message = self.get_failure_message(form.errors)
        if failure_message:
            messages.error(self.request, failure_message, extra_tags='danger')
        return self.render_to_response(context)

    def get_failure_message(self, errors):
        return self.failure_message % errors

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data
