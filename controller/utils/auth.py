import base64

from django.contrib.auth import authenticate, login

from controller.utils.apps import is_installed


def any_auth_method(condition):
    """ Enables basic auth authentication in django-private-files conditions """
    def wrapper(request, obj):
        if request.user.is_anonymous() and 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2:
                method, digest = auth
                if method == "Basic":
                    uname, passwd = base64.b64decode(digest).split(':')
                    user = authenticate(username=uname, password=passwd)
                    if user is not None:
                        if user.is_active:
                            login(request, user)
                            request.user = user
                elif method == "Token" and is_installed('rest_framework'):
                    from rest_framework.authentication import TokenAuthentication
                    from rest_framework.exceptions import AuthenticationFailed
                    try:
                        user = TokenAuthentication().authenticate_credentials(digest)[0]
                    except AuthenticationFailed:
                        pass
                    else:
                        request.user = user
        return condition(request, obj)
    return wrapper
