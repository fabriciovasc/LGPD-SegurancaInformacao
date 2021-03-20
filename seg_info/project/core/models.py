# -*- coding: utf-8 -*-
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        now = timezone.now()
        if not email:
            raise ValueError('O email é obrigatório')
        email = UserManager.normalize_email(email)
        user = self.model(email=email, is_active=True, is_superuser=False,
                          last_login=now, date_joined=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('e-mail', unique=True)
    nome = models.CharField(verbose_name=u'Nome', max_length=100)
    is_active = models.BooleanField('ativo', default=True,)
    is_staff = models.BooleanField('administrador', default=False,)
    date_joined = models.DateTimeField('data de cadastro', auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('nome', )

    class Meta:
        verbose_name = u'Usuário'
        verbose_name_plural = u'Usuários'

    def __str__(self):
        return u"%s (%s)" % (self.nome, self.email)


class UserAdd(models.Model):
    '''
        classe abstrata armazena user que criou registro
    '''
    user_add = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_created_by", editable=False, on_delete=models.CASCADE)
    date_add = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        abstract = True


class UserUpd(models.Model):
    '''
        classe abstrata armazena user que Editou registro
    '''
    user_upd = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_modified_by", editable=False, on_delete=models.CASCADE)
    date_upd = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True
