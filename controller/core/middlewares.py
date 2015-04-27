from controller.settings import DISABLE_LOGIN_CSRF_FROM


class DisableLoginCSRF(object):
    """ 
    Hack to disable csrf on the login page in order to allow login
    integration with other sites
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        if (view_func.func_name == 'index' and
            view_func.__module__ == 'django.contrib.admin.sites'): # and
            # Don't check Origin header until is supported by most of
            # the browsers (in april, 2015 only Chromium)
            # https://stackoverflow.com/a/8087233/1538221
            #request.META.get('HTTP_ORIGIN', '') in DISABLE_LOGIN_CSRF_FROM):
                setattr(request, '_dont_enforce_csrf_checks', True)
