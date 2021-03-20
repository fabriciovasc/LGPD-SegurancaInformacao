import csv

from collections import OrderedDict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ImproperlyConfigured
from django.forms import models as model_forms
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from django.urls import reverse_lazy


try:
    SIDEBAR_MENU = settings.SIDEMENU
except AttributeError:
    SIDEBAR_MENU = None

try:
    SIDEBAR_MENU_ADM = settings.SIDEMENU_ADM
except AttributeError:
    SIDEBAR_MENU_ADM = None

try:
    adm_menu_perms = settings.ADM_MENU_PERMS
except AttributeError:
    adm_menu_perms = []


from tools.forms import UserAddUpdFormMixin


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls):
        return login_required(super().as_view())


class MenuMixin(object):
    """Gera as opções para o menu da sidebar (template base.html)"""
    current_section = None  # string exatamente igual ao label do menu
    sub_current_section = None  # string exatamente igual ao label do menu
    menus = {}
    menus_adm = {}

    def assembly_menu(self, menu):
        sections = OrderedDict()
        if self.request.user.is_anonymous:
            return {}
        for section_str, section in menu.items():
            section_name = section['label']
            if section['perm']:
                has_perm_menu = self.request.user.has_perm(section['perm'])
            else:
                has_perm_menu = True
            if has_perm_menu:
                sections[section_name] = {}
                sections[section_name]['icon'] = section['icon']
                sections[section_name]['section'] = section_str
                sections[section_name]['url'] = section['url']
                sections[section_name]['active'] = self.current_section == section_str
                sections[section_name]['subsections'] = []

                for sub_section_str, url, label, perm in section['subsections']:
                    if perm:
                        has_perm_submenu = self.request.user.has_perm(perm)
                    else:
                        has_perm_submenu = True

                    if has_perm_submenu:
                        sections[section_name]['subsections'].append({
                            'url': url,
                            'label': label,
                            'active': self.sub_current_section == sub_section_str
                        })
        return sections

    def get_menu(self):
        return SIDEBAR_MENU or self.menus

    def get_menu_adm(self):
        return SIDEBAR_MENU_ADM or self.menus_adm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['current_section'] = self.current_section
        context['secoes'] = self.assembly_menu(self.get_menu())
        if not adm_menu_perms or adm_menu_perms and self.request.user.has_perms(adm_menu_perms):
            context['secoes_adm'] = self.assembly_menu(self.get_menu_adm())
        return context


class PageInfoMixin(object):
    """Adiciona informações sobre a view, para disponibilizar no Template"""
    pagename = ""
    sub_pagename = ""

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['pagename'] = self.get_pagename()
        context['sub_pagename'] = self.get_sub_pagename()
        return context

    def get_pagename(self):
        return self.pagename

    def get_sub_pagename(self):
        return self.sub_pagename


class CreateUpdateURLMixin(object):
    create_url = None
    update_url = None
    create_update_url = None

    def get_create_update_url(self, op='create'):
        model = self.get_model()
        self_url = getattr(self, "%s_url" % op)
        if self.create_update_url is False:
            return None
        elif self.create_update_url:
            return self.create_update_url
        elif self_url is False:
            return None
        elif self_url:
            return self_url
        elif hasattr(model, 'get_url'):
            return model.get_url()
        elif hasattr(model, 'get_create_update_url'):
            return model.get_create_update_url()
        else:
            return "%s_form" % model.__name__.lower()

    def get_create_url(self):
        if self.create_url is False:
            return None
        return self.get_create_update_url()

    def get_update_url(self):
        if self.update_url is False:
            return None
        return self.get_create_update_url(op='update')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['create_url'] = self.get_create_url()
        context['update_url'] = self.get_update_url()
        return context


class DetailURLMixin(object):
    detail_url = None

    def get_detail_url(self):
        detail_url = ''
        model = self.get_model()
        if self.detail_url is False:
            return None
        elif self.detail_url:
            detail_url = self.detail_url
        elif hasattr(model, 'get_detail_url'):
            detail_url = model.get_detail_url()
        else:
            detail_url = "%s_detail" % model.__name__.lower()
        return detail_url

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['detail_url'] = self.get_detail_url()
        return context


class ListURLMixin(object):
    list_url = None

    def get_list_url(self):
        list_url = ''
        model = self.get_model()
        if self.list_url is False:
            return None
        elif self.list_url:
            list_url = self.list_url
        elif hasattr(model, 'get_list_url'):
            list_url = model.get_list_url()
        else:
            list_url = "%s_list" % model.__name__.lower()

        return list_url

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['list_url'] = self.get_list_url()
        return context


class GetModelMixin(object):
    def get_model(self):
        model = None
        try:
            model = self.model
        except AttributeError:
            pass
        if not model and hasattr(self, 'form_class'):
            try:
                model = self.form_class.Meta.base_qs.model
            except AttributeError:
                model = self.form_class.Meta.model
        return model

    @property
    def verbose_name(self):
        return self.get_model()._meta.verbose_name

    @property
    def verbose_name_plural(self):
        return self.get_model()._meta.verbose_name_plural

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['model_verbose_name'] = self.verbose_name
        context['model_verbose_name_plural'] = self.verbose_name_plural
        return context


class NavTabMixin(object):
    active_tab = ''
    nav_items = []

    def get_active_tab(self):
        return self.active_tab

    def get_nav_items(self):
        return self.nav_items

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['nav_items'] = self.get_nav_items()
        ctx['active_tab'] = self.get_active_tab()
        return ctx


class UserAddUpdViewMixin(object):
    '''
    mixin para pegar request.user e atribuir ao user add e upd dos modelos
    '''

    def get_form_kwargs(self, *args, **kwargs):
        '''
        recupera o user e o passa como request_user para o form
        '''
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs['request_user'] = self.request.user
        return kwargs

    def get_form_class(self, *args, **kwargs):
        '''
        pega o formulário do modelo e cria um novo q herda do mixin UserAddUpdFormMixin
        que recebe o request user e o coloca no user_add, user_upd
        '''
        form_class = super().get_form_class(*args, **kwargs)
        return type(form_class.__name__, (UserAddUpdFormMixin, form_class), {})


class FailureMessageMixin(object):
    '''
        Add a failure message on unsuccessful form submission
    '''
    failure_message = 'Verifique os erros abaixo e corríja-os antes de enviar os dados novamente.'

    def form_invalid(self, form):
        response = super().form_invalid(form)
        failure_message = self.get_failure_message(form.errors)
        if failure_message:
            messages.error(self.request, failure_message, extra_tags='danger')
        return response

    def get_failure_message(self, errors):
        return errors


class FormMessagesMixin(SuccessMessageMixin, FailureMessageMixin):
    success_message = 'Dados salvos com sucesso!'


class RedirectSuccessURL(object):
    def get_success_url(self):
        if 'next_url' in self.request.GET:
            return self.request.GET['next_url']
        return super().get_success_url()


class SuccessURLMixin(RedirectSuccessURL):
    def get_success_url(self):
        try:
            return super().get_success_url()
        except Exception:
            return reverse_lazy(self.get_list_url())


class AddWidgetViewForm(object):
    widgets = None

    def get_form_class(self):
        if self.fields is not None and self.form_class:
            raise ImproperlyConfigured(
                "Specifying both 'fields' and 'form_class' is not permitted."
            )
        if self.form_class:
            return self.form_class
        else:
            if self.model is not None:
                model = self.model
            elif hasattr(self, 'object') and self.object is not None:
                model = self.object.__class__
            else:
                model = self.get_queryset().model
            if self.fields is None:
                raise ImproperlyConfigured(
                    "Using ModelFormMixin (base class of %s) without "
                    "the 'fields' attribute is prohibited." % self.__class__.__name__
                )
            return model_forms.modelform_factory(
                model,
                fields=self.fields,
                widgets=self.widgets
            )


class ContentTypeMixin(object):

    content_type = None

    def render_to_response(self, context, **response_kwargs):
        if not self.content_type:
            raise ImproperlyConfigured("MimeTypeMixin rquires a definition of content_type")
        response_kwargs['content_type'] = self.content_type
        return super().render_to_response(context, **response_kwargs)


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        return context


class PaginationQueryStringMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        query_string = self.request.GET.copy()
        query_string.pop('page', '1')
        context['query_string'] = query_string.urlencode()
        return context


