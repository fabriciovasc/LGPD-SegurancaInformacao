from core import models
from tools import forms as tools_forms


class UserSearchForm(tools_forms.BaseSearchForm):
    class Meta:
        base_qs = models.User.objects.filter(
            is_active=True
        )
        search_fields = [
            'nome',
            'email',
        ]
