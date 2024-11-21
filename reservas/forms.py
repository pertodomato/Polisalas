from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, AdministracaoPredial, Solicitacao, Sala, Predio
from datetime import datetime, timedelta

class RegistroUsuarioForm(UserCreationForm):
    telefone = forms.CharField(max_length=20, required=False)
    nome_representante = forms.CharField(max_length=100, required=False)
    telefone_representante = forms.CharField(max_length=20, required=False)
    email_representante = forms.EmailField(required=False)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2', 'telefone', 'nome_representante', 'telefone_representante', 'email_representante']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.telefone = self.cleaned_data.get('telefone')
        user.nome_representante = self.cleaned_data.get('nome_representante')
        user.telefone_representante = self.cleaned_data.get('telefone_representante')
        user.email_representante = self.cleaned_data.get('email_representante')
        if commit:
            user.save()
        return user

class CriarAdministradorPredialForm(UserCreationForm):
    email = forms.EmailField(required=True)
    predio = forms.ModelChoiceField(queryset=Predio.objects.all(), required=True)
    departamento = forms.CharField(max_length=100)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2', 'predio', 'departamento']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_building_administrator = True
        if commit:
            user.save()
            AdministracaoPredial.objects.create(
                usuario=user,
                predio=self.cleaned_data['predio'],
                departamento=self.cleaned_data['departamento'],
            )
        return user

class SolicitacaoForm(forms.ModelForm):
    salas = forms.ModelMultipleChoiceField(
        queryset=Sala.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    class Meta:
        model = Solicitacao
        fields = ['salas', 'data', 'horario', 'duracao', 'descricao']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'horario': forms.TimeInput(attrs={'type': 'time'}),
            'duracao': forms.NumberInput(attrs={'type': 'number', 'min': 0.5, 'step': 0.5}),
        }

    def __init__(self, *args, **kwargs):
        predio = kwargs.pop('predio', None)
        super(SolicitacaoForm, self).__init__(*args, **kwargs)
        if predio:
            self.fields['salas'].queryset = Sala.objects.filter(predio=predio)
        else:
            self.fields['salas'].queryset = Sala.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        salas = cleaned_data.get('salas')
        data = cleaned_data.get('data')
        horario = cleaned_data.get('horario')
        duracao = cleaned_data.get('duracao')

        if salas and data and horario and duracao:
            horario_inicio = datetime.combine(data, horario)
            horario_fim = horario_inicio + timedelta(hours=duracao)

            for sala in salas:
                conflitos = Solicitacao.objects.filter(
                    salas=sala,
                    data=data,
                    status='Aprovada'
                ).exclude(
                    pk=self.instance.pk
                ).filter(
                    horario__lt=horario_fim.time(),
                    horario__gte=horario_inicio.time()
                )

                if conflitos.exists():
                    self.add_error('salas', f"A sala {sala.nome} já está reservada no horário especificado.")

        return cleaned_data

class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['nome', 'capacidade', 'numero_projetores', 'numero_computadores', 'ar_condicionado', 'giz_canetao']
        widgets = {
            'ar_condicionado': forms.CheckboxInput(),
            'giz_canetao': forms.Select(choices=[('Giz', 'Giz'), ('Canetão', 'Canetão')]),
        }

class PredioForm(forms.ModelForm):
    class Meta:
        model = Predio
        fields = ['nome', 'endereco']
