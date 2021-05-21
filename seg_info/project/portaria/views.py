# -*- coding: utf-8 -*-
from core import menu_mixin
from tools.views import base as tools_views

from portaria.forms import (VisitanteForm, VisitanteSearchForm)

from portaria.models import Visitante


class VisitanteListView(
    menu_mixin.ProjetoMenuMixin,
    tools_views.BaseListView
):
    filter_by_user = False
    permission_required = []
    form_class = VisitanteSearchForm
    current_section = 'visitantes'
    sub_current_section = 'visitantes'


class VisitanteCreateView(
    menu_mixin.ProjetoMenuMixin,
    tools_views.BaseCreateView
):
    filter_by_user = False
    permission_required = ''
    current_section = 'visitantes'
    sub_current_section = 'visitantes'
    model = Visitante
    form_class = VisitanteForm


class VisitanteUpdateView(
    menu_mixin.ProjetoMenuMixin,
    tools_views.BaseUpdateView
):
    filter_by_user = False
    detail_url = False
    permission_required = []
    current_section = 'visitantes'
    sub_current_section = 'visitantes'
    model = Visitante
    form_class = VisitanteForm
