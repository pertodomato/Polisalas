from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, GrupoExtensao, AdministracaoPredial, Solicitacao, Sala, Predio

# Formulário de Registro para Grupo de Extensão
class RegistroUsuarioForm(UserCreationForm):

    telefone = forms.CharField(max_length=20)
    nome_representante = forms.CharField(max_length=100)
    telefone_representante = forms.CharField(max_length=20)
    email_representante = forms.EmailField()

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2', 'telefone', 'nome_representante', 'telefone_representante', 'email_representante']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_grupo_extensao = True
        if commit:
            user.save()
            GrupoExtensao.objects.create(
                usuario=user,
                telefone=self.cleaned_data['telefone'],
                nome_representante=self.cleaned_data['nome_representante'],
                telefone_representante=self.cleaned_data['telefone_representante'],
                email_representante=self.cleaned_data['email_representante'],
            )
        return user




class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['nome', 'capacidade', 'numero_projetores', 'numero_computadores', 'ar_condicionado', 'giz_canetao']
        widgets = {
            'ar_condicionado': forms.CheckboxInput(),
            'giz_canetao': forms.Select(choices=[('Giz', 'Giz'), ('Canetão', 'Canetão')]),
        }

    def __init__(self, *args, **kwargs):
        predio_queryset = kwargs.pop('predio_queryset', None)  # Aceita um queryset de prédios como argumento
        super(SalaForm, self).__init__(*args, **kwargs)
        if predio_queryset:
            self.fields['predio'].queryset = predio_queryset




class GrupoExtensaoForm(forms.ModelForm):
    class Meta:
        model = GrupoExtensao
        fields = ['telefone', 'nome_representante', 'telefone_representante', 'email_representante']

# Formulário de Registro para Administração Predial
class CriarAdministradorPredialForm(UserCreationForm):
    email = forms.EmailField(required=True)
    predio = forms.ModelChoiceField(queryset=Predio.objects.all(), required=True)
    departamento = forms.CharField(max_length=100)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2', 'predio', 'departamento']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_building_administrator = True  # Define como administrador predial
        if commit:
            user.save()
            AdministracaoPredial.objects.create(
                usuario=user,
                predio=self.cleaned_data['predio'],
                departamento=self.cleaned_data['departamento'],
            )
        return user

# Formulário para Solicitação de Reserva
class SolicitacaoForm(forms.ModelForm):
    class Meta:
        model = Solicitacao
        fields = ['predio', 'salas', 'data', 'horario', 'duracao', 'descricao']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'horario': forms.TimeInput(attrs={'type': 'time'}),
            'duracao': forms.NumberInput(attrs={'min': 1}),
            'salas': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super(SolicitacaoForm, self).__init__(*args, **kwargs)
        self.fields['salas'].queryset = Sala.objects.none()

        if 'predio' in self.data:
            try:
                predio_id = int(self.data.get('predio'))
                self.fields['salas'].queryset = Sala.objects.filter(predio_id=predio_id)
            except (ValueError, TypeError):
                pass  # Valor inválido; queryset permanece vazio.
        elif self.instance.pk:
            self.fields['salas'].queryset = self.instance.predio.salas.all()
            
class PredioForm(forms.ModelForm):
    class Meta:
        model = Predio
        fields = ['nome', 'endereco']

# Formulário para criar Administração Predial
class AdministracaoPredialForm(forms.ModelForm):
    class Meta:
        model = AdministracaoPredial
        fields = ['usuario', 'departamento', 'predio']

# Formulário para criar Grupo de Extensão
class GrupoExtensaoForm(forms.ModelForm):
    class Meta:
        model = GrupoExtensao
        fields = ['usuario', 'telefone', 'nome_representante', 'telefone_representante', 'email_representante']