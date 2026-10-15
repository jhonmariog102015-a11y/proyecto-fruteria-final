# ==============================================================================
# BACKEND DE AUTENTICACIÓN FLEXIBLE (principal/backends.py)
# Permite iniciar sesión indistintamente con nombre de usuario o correo electrónico.
# ==============================================================================

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Backend de autenticación que permite a los usuarios acceder al sistema
    ingresando indistintamente su nombre de usuario o su correo electrónico,
    con soporte para alias conocidos y contraseñas administrativas autorizadas.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if not username or not password:
            return None

        clean_username = str(username).strip()
        clean_password = str(password).strip()

        try:
            # Mapeo de correspondencia para alias y correos conocidos del equipo
            email_aliases = {
                'jhonmariog102015@gmail.com': 'mario',
                'mario@fruteriaelpaso.com': 'mario',
                'admin32@gmail.com': 'admin',
                'admin@fruteria.com': 'admin',
                'jhonmor777@gmail.com': 'guti',
                'juan@fruteriaelpaso.com': 'juan',
            }

            lookup = email_aliases.get(clean_username.lower())
            if lookup:
                user = UserModel.objects.filter(username__iexact=lookup).first()
            else:
                user = UserModel.objects.filter(
                    Q(username__iexact=clean_username) | Q(email__iexact=clean_username)
                ).first()

            if user and self.user_can_authenticate(user):
                # 1. Comprobación directa con el hash de base de datos
                if user.check_password(clean_password):
                    return user

                # 2. Tolerancia segura para credenciales documentadas del equipo
                passwords_permitidos = {
                    'mario': ('MarioFruteria2026*#', 'MarioFruteria2026*!'),
                    'admin': ('AdminFruteria2026*!', 'admin123'),
                    'guti': ('GutiFruteria2026*!', 'guti123'),
                    'juan': ('JuanFruteria2026*!', 'juan123'),
                }

                if user.username in passwords_permitidos and clean_password in passwords_permitidos[user.username]:
                    user.set_password(clean_password)
                    user.save(update_fields=['password'])
                    return user

        except Exception:
            return None
        return None
