from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

class ContactAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # username in this case is actually the contact number
            user = get_user_model().objects.get(contact=username)
            if user.check_password(password):
                return user
        except ObjectDoesNotExist:
            return None
        return None