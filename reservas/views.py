from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import RegistroUsuarioForm, CriarAdministradorPredialForm, SolicitacaoForm, GrupoExtensaoForm,PredioForm,SalaForm

from django.contrib.auth.decorators import user_passes_test
from .models import Predio, Sala, Solicitacao, Usuario

def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'reservas/registro_usuario.html', {'form': form})

def is_superuser(user):
    return user.is_superuser

@login_required
def selecionar_predio(request):
    """
    Superusuário escolhe um prédio para gerenciar suas salas.
    """
    if request.user.is_superuser:
        predios = Predio.objects.all()
        return render(request, 'reservas/selecionar_predio.html', {'predios': predios})
    else:
        return redirect('gerenciar_salas')


@login_required
def gerenciar_salas(request, predio_id=None):
    """
    Gerencia as salas vinculadas a um prédio:
    - Permite excluir salas existentes.
    - Redireciona para a página de criação de salas.
    """
    if request.user.is_building_administrator:
        # Administrador predial gerencia as salas do próprio prédio
        predio = request.user.administracaopredial.predio
    elif request.user.is_superuser and predio_id:
        # Superusuário gerencia as salas de qualquer prédio
        predio = get_object_or_404(Predio, id=predio_id)
    else:
        return redirect('selecionar_predio')  # Caso nenhum prédio seja especificado

    salas = Sala.objects.filter(predio=predio)

    # Excluir sala
    if request.method == 'POST' and 'excluir_sala' in request.POST:
        sala_id = request.POST.get('sala_id')
        sala = get_object_or_404(Sala, id=sala_id, predio=predio)
        sala.delete()
        return redirect('gerenciar_salas', predio_id=predio.id)

    return render(request, 'reservas/gerenciar_salas.html', {'salas': salas, 'predio': predio})


@login_required
def criar_sala(request, predio_id):
    """
    Cria uma nova sala para o prédio especificado.
    """
    predio = get_object_or_404(Predio, id=predio_id)

    if not (request.user.is_superuser or (request.user.is_building_administrator and predio == request.user.administracaopredial.predio)):
        return redirect('home')  # Redireciona se o usuário não tiver permissão

    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            nova_sala = form.save(commit=False)
            nova_sala.predio = predio  # Define o prédio automaticamente
            nova_sala.save()
            return redirect('gerenciar_salas', predio_id=predio.id)
    else:
        form = SalaForm()

    return render(request, 'reservas/criar_sala.html', {'form': form, 'predio': predio})

@login_required
def editar_sala(request, sala_id=None):
    """
    Cria ou edita uma sala vinculada a um prédio.
    """
    sala = get_object_or_404(Sala, id=sala_id) if sala_id else None

    if request.user.is_superuser:
        predio_queryset = Predio.objects.all()  # Superusuário pode ver todos os prédios
    elif request.user.is_building_administrator:
        predio_queryset = Predio.objects.filter(id=request.user.administracaopredial.predio.id)  # Apenas o prédio do administrador
    else:
        return redirect('home')

    if request.method == 'POST':
        form = SalaForm(request.POST, instance=sala, predio_queryset=predio_queryset)
        if form.is_valid():
            form.save()
            return redirect('gerenciar_salas', predio_id=form.cleaned_data['predio'].id)
    else:
        form = SalaForm(instance=sala, predio_queryset=predio_queryset)

    return render(request, 'reservas/editar_sala.html', {'form': form, 'sala': sala})

@user_passes_test(is_superuser)
def criar_administrador_predial(request):
    if request.method == 'POST':
        form = CriarAdministradorPredialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_administradores_prediais')
    else:
        form = CriarAdministradorPredialForm()
    return render(request, 'reservas/criar_administrador_predial.html', {'form': form})

@user_passes_test(is_superuser)
def lista_administradores_prediais(request):
    administradores = Usuario.objects.filter(is_building_administrator=True)
    return render(request, 'reservas/lista_administradores_prediais.html', {'administradores': administradores})

@login_required
@login_required
def solicitar_reserva(request):
    """
    Qualquer usuário autenticado pode solicitar reservas.
    """
    if request.method == 'POST':
        form = SolicitacaoForm(request.POST)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.solicitante = request.user  # Associa a solicitação ao usuário autenticado
            solicitacao.save()
            form.save_m2m()  # Salva as relações ManyToMany (salas)
            return redirect('minhas_reservas')
    else:
        form = SolicitacaoForm()

    return render(request, 'reservas/solicitar_reserva.html', {'form': form})


def load_salas(request):
    predio_id = request.GET.get('predio_id')
    salas = Sala.objects.filter(predio_id=predio_id).values('id', 'nome')
    return JsonResponse(list(salas), safe=False)

@login_required
def avaliar_solicitacoes(request):
    if request.user.is_building_administrator:
        solicitacoes = Solicitacao.objects.filter(predio=request.user.administracaopredial.predio, status='Em análise')
        if request.method == 'POST':
            solicitacao_id = request.POST.get('solicitacao_id')
            acao = request.POST.get('acao')
            justificativa = request.POST.get('justificativa')
            solicitacao = get_object_or_404(Solicitacao, id=solicitacao_id)
            solicitacao.status = 'Aprovada' if acao == 'aprovar' else 'Rejeitada'
            solicitacao.justificativa = justificativa
            solicitacao.save()
            return redirect('avaliar_solicitacoes')
        return render(request, 'reservas/avaliar_solicitacoes.html', {'solicitacoes': solicitacoes})
    else:
        return redirect('home')

@login_required
def minhas_reservas(request):
    """
    Lista todas as reservas feitas pelo usuário autenticado.
    """
    solicitacoes = Solicitacao.objects.filter(solicitante=request.user).order_by('-data', '-horario')
    return render(request, 'reservas/minhas_reservas.html', {'solicitacoes': solicitacoes})


@user_passes_test(is_superuser)
def criar_predio(request):
    if request.method == 'POST':
        form = PredioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_predios')  # Redireciona para a lista de prédios após criar
    else:
        form = PredioForm()
    return render(request, 'reservas/criar_predio.html', {'form': form})

@user_passes_test(is_superuser)
def lista_predios(request):
    predios = Predio.objects.all()
    return render(request, 'reservas/lista_predios.html', {'predios': predios})

@login_required
def alterar_perfil(request):
    if request.user.is_grupo_extensao:
        grupo = request.user.grupoextensao
        if request.method == 'POST':
            form = GrupoExtensaoForm(request.POST, instance=grupo)
            if form.is_valid():
                form.save()
                return redirect('meu_perfil')
        else:
            form = GrupoExtensaoForm(instance=grupo)
        return render(request, 'reservas/alterar_perfil.html', {'form': form})
    else:
        return redirect('home')



@login_required
def editar_sala(request, sala_id):
    if request.user.is_administracao_predial:
        sala = get_object_or_404(Sala, id=sala_id, predio=request.user.administracaopredial.predio)
        if request.method == 'POST':
            form = SalaForm(request.POST, instance=sala)
            if form.is_valid():
                form.save()
                return redirect('gerenciar_salas')
        else:
            form = SalaForm(instance=sala)
        return render(request, 'reservas/editar_sala.html', {'form': form})
    else:
        return redirect('home')

def home(request):
    return render(request, 'reservas/home.html')
