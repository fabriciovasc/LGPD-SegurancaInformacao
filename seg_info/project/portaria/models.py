from django.db import models
from core.models import (UserAdd, UserUpd)
from simple_history.models import HistoricalRecords

class Visitante(UserAdd, UserUpd):

    class Sexo:
        MASCULINO = 1
        FEMININO = 2
        choices = [
            (1, 'Masculino'),
            (2, 'Feminino'),
        ]

    # Dados Cadastrais
    nome = models.CharField(
        verbose_name="Nome Completo",
        max_length=300,
        blank=False,
        null=False
    )
    sexo = models.SmallIntegerField(
        verbose_name="Gênero",
        choices=Sexo.choices
    )
    email = models.EmailField(
        verbose_name="E-mail"
    )
    cpf = models.CharField(
        verbose_name="CPF",
        max_length=20,
        blank=False,
        null=False
    )
    ddd = models.CharField(
        verbose_name="DDD",
        max_length=4,
        blank=False,
        null=False
    )
    celular = models.CharField(
        verbose_name="Celular",
        max_length=10,
        blank=False,
        null=False
    )
    ddd2 = models.CharField(
        verbose_name="DDD",
        max_length=4,
        blank=True,
        null=True
    )
    telefone = models.CharField(
        verbose_name="Telefone Fixo",
        max_length=10,
        blank=True,
        null=True
    )
    observacoes = models.TextField(
        verbose_name="Observações sobre o visitante",
        blank=True,
        null=True
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.nome
