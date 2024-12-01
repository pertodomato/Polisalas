from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import (
    RegistroUsuarioForm,
    CriarAdministradorPredialForm,
    SolicitacaoForm,
    PredioForm,
    SalaForm,
)
from .models import Predio, Sala, Solicitacao, Usuario
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta

def home(request):
    return render(request, 'reservas/home.html')

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

@login_required
def alterar_perfil(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Seu perfil foi atualizado com sucesso.")
            return redirect('alterar_perfil')
    else:
        form = RegistroUsuarioForm(instance=request.user)
    return render(request, 'reservas/alterar_perfil.html', {'form': form})

def is_superuser(user):
    return user.is_superuser

@csrf_exempt
@login_required
def get_reservas(request):
    sala_id = request.GET.get('sala')
    data = request.GET.get('data')
    solicitacoes = Solicitacao.objects.filter(status='Aprovada')

    if sala_id:
        solicitacoes = solicitacoes.filter(salas__id=sala_id)
    if data:
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        solicitacoes = solicitacoes.filter(data=data_obj)

    events = []

    for solicitacao in solicitacoes:
        events.append({
            'title': f"Reservado",
            'start': datetime.combine(solicitacao.data, solicitacao.horario).isoformat(),
            'end': (datetime.combine(solicitacao.data, solicitacao.horario) + timedelta(hours=solicitacao.duracao)).isoformat(),
            'color': 'red',
            'allDay': False,
        })

    return JsonResponse(events, safe=False)

@login_required
def selecionar_predio_para_reserva(request):
    predios = Predio.objects.all()
    return render(request, 'reservas/selecionar_predio_para_reserva.html', {'predios': predios})

@login_required
def solicitar_reserva(request, predio_id):
    predio = get_object_or_404(Predio, id=predio_id)
    salas = Sala.objects.filter(predio=predio)
    selected_salas = []

    if request.method == 'POST':
        form = SolicitacaoForm(request.POST, predio=predio)
        selected_salas = request.POST.getlist('salas')
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.solicitante = request.user
            solicitacao.predio = predio
            solicitacao.status = 'Em análise'

            # Validação para verificar conflitos de horários
            salas_selecionadas = form.cleaned_data['salas']
            data = form.cleaned_data['data']
            horario = form.cleaned_data['horario']
            duracao = form.cleaned_data['duracao']
            horario_inicio = datetime.combine(data, horario)
            horario_fim = horario_inicio + timedelta(hours=duracao)

            conflitos = []
            for sala in salas_selecionadas:
                conflitos_sala = Solicitacao.objects.filter(
                    salas=sala,
                    data=data,
                    status='Aprovada'
                ).exclude(
                    pk=solicitacao.pk  # Exclui a própria solicitação em caso de edição
                ).filter(
                    horario__lt=horario_fim.time(),
                    horario__gte=horario_inicio.time()
                )
                if conflitos_sala.exists():
                    conflitos.append(f"Sala {sala.nome} já está reservada no horário especificado.")

            if conflitos:
                # Adiciona os erros ao formulário e exibe mensagens
                form.add_error('salas', "Conflito detectado nas salas selecionadas.")
                for conflito in conflitos:
                    messages.error(request, conflito)
            else:
                solicitacao.save()
                form.save_m2m()
                messages.success(request, "Sua solicitação foi enviada para análise.")
                return redirect('minhas_reservas')
        else:
            messages.error(request, "Erro ao enviar a solicitação. Verifique os dados e tente novamente.")
    else:
        form = SolicitacaoForm(predio=predio)
        if form.initial.get('salas'):
            selected_salas = form.initial['salas']
        else:
            selected_salas = []

    context = {
        'form': form,
        'predio': predio,
        'salas': salas,
        'selected_salas': selected_salas,
    }

    return render(request, 'reservas/solicitar_reserva.html', context)


@login_required
def minhas_reservas(request):
    """
    Lista todas as reservas feitas pelo usuário autenticado.
    """
    solicitacoes = Solicitacao.objects.filter(solicitante=request.user).order_by('-data', '-horario')

    
    for solicitacao in solicitacoes:
        duracao_horas = solicitacao.duracao
        horas = int(duracao_horas)
        minutos = int((duracao_horas - horas) * 60)
        if minutos > 0:
            solicitacao.duracao_formatada = f"{horas}h {minutos}min"
        else:
            solicitacao.duracao_formatada = f"{horas}h"

    return render(request, 'reservas/minhas_reservas.html', {'solicitacoes': solicitacoes})


@login_required
def avaliar_solicitacoes(request):
    if request.user.is_building_administrator:
        predio = request.user.administracaopredial.predio
        
        # Categoriza as solicitações por status
        solicitacoes_em_analise = Solicitacao.objects.filter(predio=predio, status='Em análise')
        solicitacoes_aprovadas = Solicitacao.objects.filter(predio=predio, status='Aprovada')
        solicitacoes_rejeitadas = Solicitacao.objects.filter(predio=predio, status='Rejeitada')
        
        if request.method == 'POST':
            solicitacao_id = request.POST.get('solicitacao_id')
            acao = request.POST.get('acao')
            justificativa = request.POST.get('justificativa')
            solicitacao = get_object_or_404(Solicitacao, id=solicitacao_id)

            # Atualiza o status da solicitação com base na ação
            if acao == 'aprovar':
                solicitacao.status = 'Aprovada'
            elif acao == 'rejeitar':
                solicitacao.status = 'Rejeitada'
            
            solicitacao.justificativa = justificativa
            solicitacao.save()
            
            # Redireciona para atualizar a página
            return redirect('avaliar_solicitacoes')

        return render(request, 'reservas/avaliar_solicitacoes.html', {
            'solicitacoes_em_analise': solicitacoes_em_analise,
            'solicitacoes_aprovadas': solicitacoes_aprovadas,
            'solicitacoes_rejeitadas': solicitacoes_rejeitadas,
        })
    else:
        return redirect('home')


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
def selecionar_predio(request):
    predios = Predio.objects.all()  # Obtém todos os prédios
    return render(request, 'reservas/selecionar_predio.html', {'predios': predios})

@login_required
def gerenciar_salas(request, predio_id=None):
    if request.user.is_building_administrator:
        predio = request.user.administracaopredial.predio
    elif request.user.is_superuser and predio_id:
        predio = get_object_or_404(Predio, id=predio_id)
    else:
        return redirect('selecionar_predio')  # Use 'selecionar_predio' if appropriate

    salas = Sala.objects.filter(predio=predio)

    if request.method == 'POST' and 'excluir_sala' in request.POST:
        sala_id = request.POST.get('sala_id')
        sala = get_object_or_404(Sala, id=sala_id, predio=predio)
        sala.delete()
        return redirect('gerenciar_salas', predio_id=predio.id)

    return render(request, 'reservas/gerenciar_salas.html', {'salas': salas, 'predio': predio})

@login_required
def criar_sala(request, predio_id):
    predio = get_object_or_404(Predio, id=predio_id)

    if not (request.user.is_superuser or (request.user.is_building_administrator and predio == request.user.administracaopredial.predio)):
        return redirect('home')

    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            nova_sala = form.save(commit=False)
            nova_sala.predio = predio
            nova_sala.save()
            return redirect('gerenciar_salas', predio_id=predio.id)
    else:
        form = SalaForm()

    return render(request, 'reservas/criar_sala.html', {'form': form, 'predio': predio})

@login_required
def editar_sala(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id)

    if request.user.is_superuser:
        predio = sala.predio
    elif request.user.is_building_administrator and sala.predio == request.user.administracaopredial.predio:
        predio = sala.predio
    else:
        return redirect('home')

    if request.method == 'POST':
        form = SalaForm(request.POST, instance=sala)
        if form.is_valid():
            form.save()
            return redirect('gerenciar_salas', predio_id=predio.id)
    else:
        form = SalaForm(instance=sala)

    return render(request, 'reservas/editar_sala.html', {'form': form, 'sala': sala})

@user_passes_test(is_superuser)
def criar_predio(request):
    if request.method == 'POST':
        form = PredioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_predios')
    else:
        form = PredioForm()
    return render(request, 'reservas/criar_predio.html', {'form': form})

@user_passes_test(is_superuser)
def lista_predios(request):
    predios = Predio.objects.all()
    return render(request, 'reservas/lista_predios.html', {'predios': predios})
from django.shortcuts import render

def fale_conosco(request):
    return render(request, 'reservas/fale_conosco.html')
