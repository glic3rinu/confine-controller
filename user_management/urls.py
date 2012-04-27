from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout

from user_management import views

password_reset_dict = {
    'template_name': 'registration/password_reset_form.html',
    'email_template_name': 'registration/password_reset.txt'
    }

urlpatterns = patterns('django.contrib.auth.views',
                       (r'^recover_account/$', 'password_reset', password_reset_dict, 'auth_password_reset'),
                       (r'^recover_account/complete/$', 'password_reset_done', {'template_name':'registration/password_reset_done.html'}, 'auth_password_reset_done'),
                       (r'^change_password/$', 'password_change', {'template_name':'registration/password_change_form.html'}, 'auth_password_change'),
                       (r'^change_password/complete/$', 'password_change_done', {'template_name':'registration/password_change_done.html'}, 'auth_change_done'),
                       (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm'),
                       (r'^reset/complete/$', 'password_reset_complete'),
                       
                       )

urlpatterns += patterns('',
                        # Login
                        url(r'^login/$', login, name='login'),
                        url(r'^logged_in/$', views.logged_in),
                        url(r'^logout/$', views.custom_logout, name='logout'),
                        url(r'^register/$', views.register_user, name='register'),
                        url(r'^profile/$', views.user_profile, name='user_profile'),
                        url(r'^delete_user/$', views.user_delete_request, name='user_delete_request'),
                        url(r'^change_user_password/$', views.change_user_password, name='change_user_password'),
                        )
