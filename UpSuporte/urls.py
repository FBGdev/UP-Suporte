from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from core import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 🔐 Autenticação
    path('login/', views.login_view, name='login'),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='login'),
        name='logout'
    ),

    # 🛠️ Admin
    path('admin/', admin.site.urls),

    # 🏠 Dashboard
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),


    # 📦 Aparelhos
    path('aparelho/novo/', views.novo_aparelho, name='novo_aparelho'),
    path('aparelho/editar/<int:id>/', views.editar_aparelho, name='editar_aparelho'),

    # 🧾 Ordem de Serviço (OS)
    path('os/nova/<int:aparelho_id>/', views.nova_os, name='nova_os'),
    path('os/<int:id>/', views.detalhe_os, name='detalhe_os'),
    path('os/<int:id>/decidir/', views.decidir_os, name='decidir_os'),
    path('os/<int:id>/comentario/', views.adicionar_comentario_os, name='adicionar_comentario_os'),

    # 👷 Gestão da OS (gestor)
    path(
        'os/<int:os_id>/designar/',
        views.designar_funcionario,
        name='designar_funcionario'
    ),
    path(
        'os/<int:id>/finalizar/',
        views.finalizar_os,
        name='finalizar_os'
    ),

    # 🛠️ Manutenção (técnico)
    path(
        'os/<int:os_id>/manutencao/',
        views.registrar_manutencao_os,
        name='registrar_manutencao_os'
    ),

    # 📋 Minhas OS (técnico)
    path('minhas-os/', views.minhas_os, name='minhas_os'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
