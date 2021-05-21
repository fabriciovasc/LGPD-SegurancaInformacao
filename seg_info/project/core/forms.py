from django import forms
from core.models import User
from django.db.models import Q


class UserSearchForm(forms.ModelForm):
    nome = forms.CharField(max_length=100, required=False)
    email = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = []
        base_qs = User.objects

    def get_result_queryset(self):
        q = Q()
        if self.is_valid():
            if self.cleaned_data["nome"]:
                q = q & Q(name__icontains=self.cleaned_data["nome"])
            if self.cleaned_data["email"]:
                q = q & Q(email__icontains=self.cleaned_data["email"])
        return User.objects.filter(q)
