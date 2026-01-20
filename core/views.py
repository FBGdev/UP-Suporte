from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

from .decorators import gestor_required
from .forms import (
    AparelhoForm,
    CadastroUsuarioForm,
    OrdemServicoForm,
    RegistroManutencaoForm,
)
from .models import Aparelho, Funcionario, OrdemServico, RegistroManutencao
from .notifications import notify_os_assigned



def _get_funcionario(user):
    try:
        return user.funcionario
    except Funcionario.DoesNotExist:
        return None


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            is_tecnico = user.groups.filter(name="Tecnico").exists()
            is_gestor = user.groups.filter(name="Gestor").exists()

            if not (is_tecnico or is_gestor):
                form.add_error(None, "Acesso permitido apenas para técnicos ou gestores.")
            else:
                login(request, user)
                return redirect("home")

    return render(request, "login.html", {"form": form})


@login_required
def home(request):
    funcionario = _get_funcionario(request.user)
    is_gestor = request.user.groups.filter(name="Gestor").exists()
    is_tecnico = request.user.groups.filter(name="Tecnico").exists()

    if is_tecnico and funcionario:
        aparelhos = Aparelho.objects.none()
        ordens = (
            OrdemServico.objects.filter(funcionario=funcionario)
            .select_related("aparelho", "funcionario")
        )
    else:
        aparelhos = Aparelho.objects.all()
        ordens = OrdemServico.objects.select_related("aparelho", "funcionario")

    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    prioridade = request.GET.get("prioridade", "").strip()
    tecnico_id = request.GET.get("tecnico", "").strip()

    if q:
        query = (
            Q(aparelho__nome__icontains=q)
            | Q(aparelho__marca__icontains=q)
            | Q(aparelho__modelo__icontains=q)
            | Q(aparelho__cliente__icontains=q)
            | Q(problema_relatado__icontains=q)
        )
        if q.isdigit():
            query |= Q(id=int(q))
        ordens = ordens.filter(query)

    if status:
        ordens = ordens.filter(status=status)

    if prioridade:
        ordens = ordens.filter(prioridade=prioridade)

    if is_gestor and tecnico_id:
        ordens = ordens.filter(funcionario_id=tecnico_id)

    ordens = ordens.order_by("-data_criacao")

    return render(
        request,
        "home.html",
        {
            "aparelhos": aparelhos,
            "ordens": ordens,
            "funcionario": funcionario,
            "is_gestor": is_gestor,
            "is_tecnico": is_tecnico,
            "status_choices": OrdemServico.STATUS_CHOICES,
            "prioridade_choices": OrdemServico.PRIORIDADE_CHOICES,
            "tecnicos": Funcionario.objects.all() if is_gestor else Funcionario.objects.none(),
            "filters": {
                "q": q,
                "status": status,
                "prioridade": prioridade,
                "tecnico": tecnico_id,
            },
        },
    )


@gestor_required
def novo_aparelho(request):
    if request.method == "POST":
        form = AparelhoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = AparelhoForm()

    return render(
        request,
        "cadastrar_aparelho.html",
        {"form": form, "editando": False},
    )


@gestor_required
def editar_aparelho(request, id):
    aparelho = get_object_or_404(Aparelho, id=id)

    if request.method == "POST":
        form = AparelhoForm(request.POST, instance=aparelho)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = AparelhoForm(instance=aparelho)

    return render(
        request,
        "cadastrar_aparelho.html",
        {"form": form, "editando": True},
    )


@login_required
def nova_os(request, aparelho_id):
    aparelho = get_object_or_404(Aparelho, id=aparelho_id)

    if request.method == "POST":
        form = OrdemServicoForm(request.POST)
        if form.is_valid():
            os = form.save(commit=False)
            os.aparelho = aparelho
            os.save()
            return redirect("home")
    else:
        form = OrdemServicoForm()

    return render(request, "nova_os.html", {
        "form": form,
        "aparelho": aparelho
    })


@ensure_csrf_cookie
@gestor_required
def designar_funcionario(request, os_id):
    ordem = get_object_or_404(OrdemServico, id=os_id)
    funcionarios = Funcionario.objects.all()

    if request.method == "POST":
        ordem.funcionario_id = request.POST.get("funcionario")
        ordem.data_agendada = request.POST.get("data_agendada")
        ordem.hora_agendada = request.POST.get("hora_agendada")
        ordem.status = "AGENDADO"
        ordem.save()
        if ordem.funcionario:
            notify_os_assigned(ordem)
        return redirect("home")

    return render(request, "designar_funcionario.html", {
        "ordem": ordem,
        "funcionarios": funcionarios
    })

@login_required
def detalhe_os(request, id):
    os_obj = get_object_or_404(OrdemServico, id=id)
    is_gestor = request.user.groups.filter(name="Gestor").exists()
    funcionario = _get_funcionario(request.user)
    return render(
        request,
        "detalhe_os.html",
        {"os": os_obj, "is_gestor": is_gestor, "funcionario": funcionario},
    )


@login_required
def decidir_os(request, id):
    os_obj = get_object_or_404(OrdemServico, id=id)
    funcionario = _get_funcionario(request.user)
    is_tecnico = request.user.groups.filter(name="Tecnico").exists()

    if not is_tecnico or not funcionario or os_obj.funcionario_id != funcionario.id:
        return redirect("home")

    if request.method == "POST":
        acao = request.POST.get("acao")
        if acao == "aceitar":
            os_obj.status = "ACEITA"
        elif acao == "rejeitar":
            os_obj.status = "REJEITADA"
        os_obj.save()
        return redirect("home")

    return redirect("home")

@login_required
def registrar_manutencao_os(request, os_id):
    ordem = get_object_or_404(OrdemServico, id=os_id)
    funcionario = ordem.funcionario

    if request.method == "POST":
        form = RegistroManutencaoForm(request.POST, request.FILES)
        if form.is_valid():
            manut = form.save(commit=False)
            manut.ordem_servico = ordem
            manut.funcionario = funcionario
            manut.save()

            ordem.status = "EM_ANDAMENTO"
            ordem.save()

            return redirect("detalhe_os", id=ordem.id)
    else:
        form = RegistroManutencaoForm()

    return render(
        request,
        "registrar_manutencao.html",
        {"form": form, "ordem": ordem, "funcionario": funcionario},
    )


@gestor_required
def finalizar_os(request, id):
    os = get_object_or_404(OrdemServico, id=id)

    if request.method == "POST":
        laudo = request.POST.get("laudo", "").strip()

        if not laudo:
            return render(
                request,
                "finalizar_os.html",
                {"os": os, "erro": "O laudo técnico é obrigatório para finalizar a OS."},
            )

        os.laudo_tecnico = laudo
        os.status = "CONCLUIDO"
        os.data_conclusao = timezone.now()
        os.save()

        return redirect("detalhe_os", id=os.id)

    return render(request, "finalizar_os.html", {"os": os})

def cadastrar_usuario(request):
    if request.method == "POST":
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["senha"])
            user.save()

            Funcionario.objects.create(
                usuario=user,
                cargo=form.cleaned_data["cargo"],
                telefone=form.cleaned_data.get("telefone", "")
            )

            login(request, user)
            return redirect("home")
    else:
        form = CadastroUsuarioForm()

    return render(request, "cadastro.html", {"form": form})


@login_required
def minhas_os(request):
    funcionario = _get_funcionario(request.user)
    if funcionario:
        ordens = (
            OrdemServico.objects.filter(funcionario=funcionario)
            .select_related("aparelho", "funcionario")
            .order_by("-data_criacao")
        )
    else:
        ordens = OrdemServico.objects.none()

    return render(
        request,
        "minhas_os.html",
        {"ordens": ordens, "funcionario": funcionario},
    )
