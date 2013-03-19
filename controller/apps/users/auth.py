from django.contrib.auth import get_user_model


class EmailBackend(object):
    def authenticate(self, username=None, password=None):
        """ Authenticate a user based on email address as the user name. """
        User = get_user_model()
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            UserModel = get_user_model()
            return UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
