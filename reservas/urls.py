from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.registro_usuario, name='registro_usuario'),
    path('login/', auth_views.LoginView.as_view(template_name='reservas/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('alterar_perfil/', views.alterar_perfil, name='alterar_perfil'),
    path('solicitar_reserva/', views.selecionar_predio_para_reserva, name='selecionar_predio_para_reserva'),
    path('solicitar_reserva/<int:predio_id>/', views.solicitar_reserva, name='solicitar_reserva'),
    path('minhas_reservas/', views.minhas_reservas, name='minhas_reservas'),
    path('avaliar_solicitacoes/', views.avaliar_solicitacoes, name='avaliar_solicitacoes'),
    path('administradores_prediais/criar/', views.criar_administrador_predial, name='criar_administrador_predial'),
    path('administradores_prediais/', views.lista_administradores_prediais, name='lista_administradores_prediais'),
    path('predios/criar/', views.criar_predio, name='criar_predio'),
    path('predios/', views.lista_predios, name='lista_predios'),
    path('salas/gerenciar/<int:predio_id>/', views.gerenciar_salas, name='gerenciar_salas'),
    path('salas/novo/<int:predio_id>/', views.criar_sala, name='criar_sala'),
    path('salas/editar/<int:sala_id>/', views.editar_sala, name='editar_sala'),
    path('api/get_reservas/', views.get_reservas, name='get_reservas'),
    path('selecionar-predio/', views.selecionar_predio, name='selecionar_predio'),
]
