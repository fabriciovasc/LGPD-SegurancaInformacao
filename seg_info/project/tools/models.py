from django.conf import settings
from django.db import models


class UserAdd(models.Model):
    '''
        classe abstrata armazena user que criou registro
    '''
    user_add = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(app_label)s_%(class)s_created_by",
        editable=False,
        on_delete=models.CASCADE
    )
    date_add = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        abstract = True


class UserUpd(models.Model):
    '''
        classe abstrata armazena user que Editou registro
    '''
    user_upd = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(app_label)s_%(class)s_modified_by",
        editable=False,
        on_delete=models.CASCADE
    )
    date_upd = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True
