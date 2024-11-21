from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime, timedelta
from django.conf import settings

class Usuario(AbstractUser):
    is_building_administrator = models.BooleanField(default=False)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    nome_representante = models.CharField(max_length=100, blank=True, null=True)
    telefone_representante = models.CharField(max_length=20, blank=True, null=True)
    email_representante = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.username

class Predio(models.Model):
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200)

    def __str__(self):
        return self.nome

class AdministracaoPredial(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    departamento = models.CharField(max_length=100)
    predio = models.OneToOneField(Predio, on_delete=models.CASCADE, related_name='administracao')

    def __str__(self):
        return f"{self.departamento} - {self.predio.nome}"

class Sala(models.Model):
    nome = models.CharField(max_length=50)
    predio = models.ForeignKey(Predio, on_delete=models.CASCADE, related_name='salas')
    capacidade = models.IntegerField()
    numero_projetores = models.IntegerField()
    numero_computadores = models.IntegerField()
    ar_condicionado = models.BooleanField(default=False)
    giz_canetao = models.CharField(max_length=10)  # 'Giz' ou 'Canetão'

    def __str__(self):
        return f"{self.nome} - {self.predio.nome}"

class Solicitacao(models.Model):
    STATUS_CHOICES = [
        ('Em análise', 'Em análise'),
        ('Aprovada', 'Aprovada'),
        ('Rejeitada', 'Rejeitada'),
    ]

    solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    predio = models.ForeignKey(Predio, on_delete=models.CASCADE)
    salas = models.ManyToManyField(Sala)
    data = models.DateField()
    horario = models.TimeField()
    duracao = models.FloatField()  # Duração em horas
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Em análise')
    descricao = models.TextField(blank=True, null=True)
    justificativa = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Solicitação {self.id} - {self.solicitante.username}"

    @property
    def horario_inicio(self):
        return datetime.combine(self.data, self.horario)

    @property
    def horario_fim(self):
        return self.horario_inicio + timedelta(hours=self.duracao)
