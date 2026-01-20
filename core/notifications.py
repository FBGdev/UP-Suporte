import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _build_os_message(ordem):
    aparelho = ordem.aparelho
    tecnico = ordem.funcionario.usuario.get_full_name() or ordem.funcionario.usuario.username
    agendamento = "Nao agendado"
    if ordem.data_agendada and ordem.hora_agendada:
        agendamento = f"{ordem.data_agendada} as {ordem.hora_agendada}"

    subject = f"OS #{ordem.id} atribuida a voce"
    body = (
        f"Ola {tecnico},\n\n"
        f"Voce foi designado para a OS #{ordem.id}.\n"
        f"Aparelho: {aparelho.nome} ({aparelho.marca} {aparelho.modelo})\n"
        f"Cliente: {aparelho.cliente}\n"
        f"Agendamento: {agendamento}\n"
        f"Prioridade: {ordem.prioridade}\n\n"
        "Acesse o sistema para ver os detalhes."
    )
    return subject, body


def notify_os_assigned(ordem):
    subject, body = _build_os_message(ordem)

    user = ordem.funcionario.usuario
    if user.email:
        try:
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception:  # noqa: BLE001 - avoid blocking the OS assignment
            logger.exception("Falha ao enviar email de OS atribuida para %s", user.email)
    else:
        logger.info("Email nao cadastrado para usuario %s", user.username)

    telefone = ordem.funcionario.telefone
    if telefone and getattr(settings, "ENABLE_WHATSAPP_NOTIFICATIONS", False):
        logger.info("WhatsApp: %s\n%s", telefone, body)
    else:
        logger.info("WhatsApp desativado ou telefone nao cadastrado para OS #%s", ordem.id)
