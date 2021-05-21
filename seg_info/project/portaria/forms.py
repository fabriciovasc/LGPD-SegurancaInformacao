from django import forms
from portaria.models import Visitante
from django.db.models import Q


class VisitanteSearchForm(forms.ModelForm):
    nome = forms.CharField(max_length=100, required=False)
    email = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Visitante
        fields = []
        base_qs = Visitante.objects

    def get_result_queryset(self):
        q = Q()
        if self.is_valid():
            if self.cleaned_data["nome"]:
                q = q & Q(name__icontains=self.cleaned_data["nome"])
            if self.cleaned_data["email"]:
                q = q & Q(email__icontains=self.cleaned_data["email"])
        return Visitante.objects.filter(q)


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
