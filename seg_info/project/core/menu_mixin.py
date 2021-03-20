from django.urls import reverse_lazy
from tools.views.mixins import MenuMixin
from rules.contrib.views import PermissionRequiredMixin


class ProjetoMenuMixin(MenuMixin, PermissionRequiredMixin):
    permission_required = 'true'

    def get_menu(self):
        return {
            'administracao': {
                'label': 'Administração',
                'perm': '',
                'icon': 'fa-cogs',
                'url': '#',
                'active': False,
                'subsections': [
                    ('usuarios', reverse_lazy('user_list'), 'Usuários', ''),
                ]
            },
            'visitantes': {
                'label': 'Visitante',
                'perm': '',
                'icon': 'fa-cogs',
                'url': '#',
                'active': False,
                'subsections': [
                    ('visitantes', reverse_lazy('visitante_list'), 'Visitantes', ''),
                ]
            },
        }
