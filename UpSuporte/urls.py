from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from core import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    
    path('login/', views.login_view, name='login'),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='login'),
        name='logout'
    ),

    
    path('devfb/', admin.site.urls),

    
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),


    
    path('aparelho/novo/', views.novo_aparelho, name='novo_aparelho'),
    path('aparelho/editar/<int:id>/', views.editar_aparelho, name='editar_aparelho'),

    
    path('os/nova/<int:aparelho_id>/', views.nova_os, name='nova_os'),
    path('os/<int:id>/', views.detalhe_os, name='detalhe_os'),
    path('os/<int:id>/decidir/', views.decidir_os, name='decidir_os'),
    path('os/<int:id>/comentario/', views.adicionar_comentario_os, name='adicionar_comentario_os'),

    
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

    
    path(
        'os/<int:os_id>/manutencao/',
        views.registrar_manutencao_os,
        name='registrar_manutencao_os'
    ),

    
    path('minhas-os/', views.minhas_os, name='minhas_os'),
]

handler400 = "core.views.custom_400"
handler403 = "core.views.custom_403"
handler404 = "core.views.custom_404"
handler500 = "core.views.custom_500"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
