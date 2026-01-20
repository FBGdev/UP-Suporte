from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone


class Funcionario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.usuario.get_full_name() or self.usuario.username


class Aparelho(models.Model):
    TIPO_CHOICES = [
        ("NOTEBOOK", "Notebook"),
        ("DESKTOP", "Desktop"),
        ("IMPRESSORA", "Impressora"),
        ("MONITOR", "Monitor"),
        ("OUTRO", "Outro"),
    ]

    nome = models.CharField(max_length=150)
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    numero_serie = models.CharField(max_length=100, unique=True)
    cliente = models.CharField(max_length=150)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.tipo}) - {self.cliente}"


class OrdemServico(models.Model):
    STATUS_CHOICES = [
        ("ABERTO", "Aberto"),
        ("AGENDADO", "Agendado"),
        ("EM_ANDAMENTO", "Em andamento"),
        ("ACEITA", "Aceita"),
        ("REJEITADA", "Rejeitada"),
        ("CONCLUIDO", "Concluído"),
        ("CANCELADO", "Cancelado"),
    ]

    PRIORIDADE_CHOICES = [
        ("BAIXA", "Baixa"),
        ("MEDIA", "Média"),
        ("ALTA", "Alta"),
    ]

    aparelho = models.ForeignKey(Aparelho, on_delete=models.CASCADE, related_name="ordens")
    funcionario = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, null=True, blank=True)

    problema_relatado = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ABERTO")

    data_agendada = models.DateField(null=True, blank=True)
    hora_agendada = models.TimeField(null=True, blank=True)

    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default="MEDIA")

    laudo_tecnico = models.TextField(blank=True)  # só preenche quando finaliza

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    data_limite_sla = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"OS #{self.id} - {self.aparelho.nome}"

    def get_sla_deadline(self):
        if self.data_limite_sla:
            return self.data_limite_sla
        horas = settings.SLA_HORAS.get(self.prioridade, 48)
        return self.data_criacao + timezone.timedelta(hours=horas)

    def is_atrasada(self):
        if self.status in {"CONCLUIDO", "CANCELADO"}:
            return False
        return timezone.now() > self.get_sla_deadline()

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)
        if creating and not self.data_limite_sla and self.data_criacao:
            horas = settings.SLA_HORAS.get(self.prioridade, 48)
            self.data_limite_sla = self.data_criacao + timezone.timedelta(hours=horas)
            super().save(update_fields=["data_limite_sla"])


class OrdemServicoHistorico(models.Model):
    ordem_servico = models.ForeignKey(OrdemServico, on_delete=models.CASCADE, related_name="historico")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    campo = models.CharField(max_length=100)
    valor_anterior = models.TextField(blank=True, null=True)
    valor_novo = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OS #{self.ordem_servico.id} - {self.campo}"

    class Meta:
        ordering = ["-criado_em"]


class OrdemServicoComentario(models.Model):
    ordem_servico = models.ForeignKey(OrdemServico, on_delete=models.CASCADE, related_name="comentarios")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OS #{self.ordem_servico.id} - Comentario"

    class Meta:
        ordering = ["-criado_em"]


class RegistroManutencao(models.Model):
    TIPO_SERVICO = [
        ("MANUTENCAO", "Manutenção"),
        ("TROCA", "Troca de Peça"),
    ]

    ordem_servico = models.ForeignKey(OrdemServico, on_delete=models.CASCADE, related_name="registros")
    funcionario = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, null=True, blank=True)

    tipo_servico = models.CharField(max_length=20, choices=TIPO_SERVICO)
    descricao = models.TextField()
    peca_trocada = models.CharField(max_length=150, blank=True, null=True)
    foto_1 = models.ImageField(upload_to="manutencoes/", blank=True, null=True)
    foto_2 = models.ImageField(upload_to="manutencoes/", blank=True, null=True)
    foto_3 = models.ImageField(upload_to="manutencoes/", blank=True, null=True)

    data_execucao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_servico} - OS #{self.ordem_servico.id}"
