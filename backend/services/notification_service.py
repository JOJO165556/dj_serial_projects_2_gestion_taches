import logging
import threading
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


def _send_email_async(email):
    """Fonction exécutée en arrière-plan pour envoyer l'email sans bloquer l'utilisateur."""
    try:
        email.send(fail_silently=False)
    except Exception as exc:
        logger.error("Erreur lors de l'envoi asynchrone de l'email : %s", exc)


def send_project_invitation_email(invitation, invited_by, custom_message=""):
    if not invitation.user.email:
        return False

    invite_url = f"{settings.FRONTEND_URL}/invite/{invitation.token}"
    subject = f"Invitation a rejoindre le projet {invitation.project.name}"

    message_lines = [
        f"Bonjour {invitation.user.username},",
        "",
        f"{invited_by.username} vous invite a rejoindre le projet '{invitation.project.name}' sur {settings.APP_NAME}.",
    ]

    if custom_message:
        message_lines.extend(
            [
                "",
                "Message de l'invitation :",
                custom_message.strip(),
            ]
        )

    message_lines.extend(
        [
            "",
            "Lien d'invitation :",
            invite_url,
            "",
            "Si vous n'attendiez pas cet email, vous pouvez simplement l'ignorer.",
        ]
    )

    text_body = "\n".join(message_lines)
    html_body = (
        f"<p>Bonjour {invitation.user.username},</p>"
        f"<p><strong>{invited_by.username}</strong> vous invite a rejoindre le projet "
        f"<strong>{invitation.project.name}</strong> sur {settings.APP_NAME}.</p>"
    )

    if custom_message:
        html_body += (
            "<p><strong>Message de l'invitation :</strong><br>"
            f"{custom_message.strip()}</p>"
        )

    html_body += (
        f'<p><a href="{invite_url}">Ouvrir l\'invitation</a></p>'
        "<p>Si vous n'attendiez pas cet email, vous pouvez simplement l'ignorer.</p>"
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[invitation.user.email],
    )
    email.attach_alternative(html_body, "text/html")
    
    # Envoi asynchrone via Thread
    thread = threading.Thread(target=_send_email_async, args=(email,))
    thread.start()
    return True


def send_magic_link_email(user, magic_url):
    if not user.email:
        return False

    subject = f"Votre lien de connexion {settings.APP_NAME}"
    text_body = "\n".join(
        [
            f"Bonjour {user.username},",
            "",
            "Voici votre lien de connexion :",
            magic_url,
            "",
            "Ce lien expire rapidement pour des raisons de securite.",
            "Si vous n'etes pas a l'origine de cette demande, ignorez cet email.",
        ]
    )
    html_body = (
        f"<p>Bonjour {user.username},</p>"
        f'<p><a href="{magic_url}">Se connecter</a></p>'
        "<p>Ce lien expire rapidement pour des raisons de securite.</p>"
        "<p>Si vous n'etes pas a l'origine de cette demande, ignorez cet email.</p>"
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html_body, "text/html")
    
    # Envoi asynchrone via Thread
    thread = threading.Thread(target=_send_email_async, args=(email,))
    thread.start()
    return True
