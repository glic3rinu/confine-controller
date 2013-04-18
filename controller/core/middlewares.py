from controller.settings import DISABLE_LOGIN_CSRF_FROM


class DisableLoginCSRF(object):
    """ 
    Hack to disable csrf on the login page in order to allow login
    integration with other sites
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        if (view_func.func_name == 'index' and
            view_func.__module__ == 'django.contrib.admin.sites' and
            request.META.get('HTTP_ORIGIN', '') in DISABLE_LOGIN_CSRF_FROM):
                setattr(request, '_dont_enforce_csrf_checks', True)
