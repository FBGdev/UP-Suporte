import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.urls import reverse

logger = logging.getLogger(__name__)


def _build_os_message(ordem):
    tecnico = ordem.funcionario.usuario.get_full_name() or ordem.funcionario.usuario.username

    subject = "Nova OS atribuida"
    base_url = getattr(settings, "SITE_URL", "http://localhost:8000").rstrip("/")
    approval_url = f"{base_url}{reverse('detalhe_os', args=[ordem.id])}"
    text_body = (
        f"Ola {tecnico},\n\n"
        "Uma nova ordem de servico foi atribuida ao seu usuario.\n"
        f"Acesse para aceitar ou rejeitar: {approval_url}\n\n"
        "UpSuporte"
    )
    html_body = f"""
    <div style="font-family: Arial, sans-serif; color: #0f172a;">
      <h2 style="margin: 0 0 8px;">Nova OS atribuida</h2>
      <p>Ola {tecnico},</p>
      <p>Uma nova ordem de servico foi atribuida ao seu usuario.</p>
      <a
        href="{approval_url}"
        style="display: inline-block; margin-top: 16px; padding: 10px 18px; background: #0f172a; color: #ffffff; text-decoration: none; border-radius: 999px; font-weight: 600;"
      >Acessar UpSuporte</a>
      <p style="margin-top: 24px; font-size: 12px; color: #64748b;">Se nao conseguir clicar, copie e cole: {approval_url}</p>
    </div>
    """
    return subject, text_body, html_body


def notify_os_assigned(ordem):
    subject, text_body, html_body = _build_os_message(ordem)

    user = ordem.funcionario.usuario
    if user.email:
        try:
            timeout = getattr(settings, "EMAIL_TIMEOUT", 5)
            connection = get_connection(timeout=timeout)
            message = EmailMultiAlternatives(
                subject,
                text_body,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                connection=connection,
            )
            message.attach_alternative(html_body, "text/html")
            message.send(fail_silently=False)
        except Exception:  # noqa: BLE001 - avoid blocking the OS assignment
            logger.exception("Falha ao enviar email de OS atribuida para %s", user.email)
    else:
        logger.info("Email nao cadastrado para usuario %s", user.username)

    telefone = ordem.funcionario.telefone
    if telefone and getattr(settings, "ENABLE_WHATSAPP_NOTIFICATIONS", False):
        logger.info("WhatsApp: %s\n%s", telefone, text_body)
    else:
        logger.info("WhatsApp desativado ou telefone nao cadastrado para OS #%s", ordem.id)
