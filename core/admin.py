from django.contrib import admin
from .models import Aparelho, Funcionario, OrdemServico, RegistroManutencao


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "cargo", "telefone")
    search_fields = ("usuario__username", "usuario__first_name", "usuario__last_name", "cargo")


@admin.register(Aparelho)
class AparelhoAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "tipo", "marca", "modelo", "numero_serie", "cliente", "data_cadastro")
    search_fields = ("nome", "marca", "modelo", "numero_serie", "cliente")
    list_filter = ("tipo", "marca")
    ordering = ("-data_cadastro",)


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ("id", "aparelho", "status", "prioridade", "funcionario", "data_agendada", "hora_agendada", "data_criacao")
    search_fields = ("aparelho__nome", "aparelho__cliente", "problema_relatado", "funcionario__usuario__username")
    list_filter = ("status", "prioridade", "data_agendada")
    ordering = ("-data_criacao",)


@admin.register(RegistroManutencao)
class RegistroManutencaoAdmin(admin.ModelAdmin):
    list_display = ("id", "ordem_servico", "funcionario", "tipo_servico", "peca_trocada", "data_execucao")
    search_fields = ("ordem_servico__id", "descricao", "funcionario__usuario__username")
    list_filter = ("tipo_servico", "data_execucao")
    ordering = ("-data_execucao",)
