from django import forms
from tools import forms as tools_forms
from portaria.models import Visitante


class VisitanteSearchForm(tools_forms.BaseSearchForm):
    class Meta:
        base_qs = Visitante.objects.filter()
        search_fields = [
            'nome__icontains',
            'cpf__icontains',
        ]


class VisitanteForm(
    forms.ModelForm
):

    class Meta:
        model = Visitante
        fields = [
            'nome',
            'sexo',
            'email',
            'cpf',
            'ddd',
            'celular',
            'ddd2',
            'telefone',
            'observacoes'
        ]
