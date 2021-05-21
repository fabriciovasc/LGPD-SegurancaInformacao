from collections import OrderedDict

from django.conf import settings

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


class MenuMixin(object):
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


class PaginationQueryStringMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        query_string = self.request.GET.copy()
        query_string.pop('page', '1')
        context['query_string'] = query_string.urlencode()
        return context
