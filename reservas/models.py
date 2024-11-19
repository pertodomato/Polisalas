from django.db import models
from django.contrib.auth.models import AbstractUser

# Modelo de Usuário Personalizado
class Usuario(AbstractUser):
    is_grupo_extensao = models.BooleanField(default=False)
    is_administracao_predial = models.BooleanField(default=False)

# Grupo de Extensão
class GrupoExtensao(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=20)
    nome_representante = models.CharField(max_length=100)
    telefone_representante = models.CharField(max_length=20)
    email_representante = models.EmailField()

    def __str__(self):
        return self.usuario.username

# Prédio
class Predio(models.Model):
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200)

    def __str__(self):
        return self.nome

# Administração Predial
class AdministracaoPredial(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    departamento = models.CharField(max_length=100)
    predio = models.OneToOneField(Predio, on_delete=models.CASCADE, related_name='administracao')

    def __str__(self):
        return f"{self.departamento} - {self.predio.nome}"

# Sala
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

# Solicitação
class Solicitacao(models.Model):
    STATUS_CHOICES = [
        ('Em análise', 'Em análise'),
        ('Aprovada', 'Aprovada'),
        ('Rejeitada', 'Rejeitada'),
    ]

    solicitante = models.ForeignKey(GrupoExtensao, on_delete=models.CASCADE)
    predio = models.ForeignKey(Predio, on_delete=models.CASCADE)
    salas = models.ManyToManyField(Sala)
    data = models.DateField()
    horario = models.TimeField()
    duracao = models.DurationField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Em análise')
    descricao = models.TextField(blank=True, null=True)
    justificativa = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Solicitação {self.id} - {self.solicitante.usuario.username}"
