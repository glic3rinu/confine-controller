import base64

from django.contrib.auth import authenticate, login


def logged_or_basicauth(method):
    """ Enables basic auth autentication in django-private-files conditions """
    def wrapper(request, obj):
        if request.user.is_anonymous() and 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2:
                # NOTE: We are only support basic authentication for now.
                #
                if auth[0].lower() == "basic":
                    uname, passwd = base64.b64decode(auth[1]).split(':')
                    user = authenticate(username=uname, password=passwd)
                    if user is not None:
                        if user.is_active:
                            login(request, user)
                            request.user = user
        return method(request, obj)
    return wrapper
