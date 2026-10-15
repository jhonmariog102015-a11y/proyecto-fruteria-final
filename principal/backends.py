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
    ingresando tanto su nombre de usuario como su correo electrónico.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if not username or not password:
            return None

        try:
            # Búsqueda insensible a mayúsculas por username o email
            user = UserModel.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).first()

            if user and user.check_password(password) and self.user_can_authenticate(user):
                return user
        except Exception:
            return None
        return None
