import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _build_os_message(ordem):
    tecnico = ordem.funcionario.usuario.get_full_name() or ordem.funcionario.usuario.username

    subject = "Nova OS atribuida"
    body = (
        f"Ola {tecnico},\n\n"
        "Uma nova ordem de servico foi atribuida ao seu usuario.\n"
        "Entre no sistema para visualizar os detalhes.\n\n"
        "UpSuporte"
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
