from django.db import models
from django.contrib.auth.models import User


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

    def __str__(self):
        return f"OS #{self.id} - {self.aparelho.nome}"


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
