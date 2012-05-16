# -*- coding: utf-8 -*-
from user_management import models
from django.contrib import admin
from django.conf import settings

from user_management import admin_actions


class ResearchGroupAdminModel(admin.ModelAdmin):
    class Meta:
        model = models.ResearchGroup

class RoleAdminModel(admin.ModelAdmin):
    class Meta:
        model = models.Role

class ConfinePermissionAdminModel(admin.ModelAdmin):
    class Meta:
        model = models.ConfinePermission


class ActivationRequestAdminModel(admin.ModelAdmin):
    actions = [admin_actions.activate_user]
    class Meta:
        model = models.ActivationRequest

class DeleteRequestAdminModel(admin.ModelAdmin):
    actions = [admin_actions.delete_user]
    class Meta:
        model = models.DeleteRequest

admin.site.register(models.ActivationRequest, ActivationRequestAdminModel)
admin.site.register(models.DeleteRequest, DeleteRequestAdminModel)
admin.site.register(models.Role, RoleAdminModel)
admin.site.register(models.ResearchGroup, ResearchGroupAdminModel)
admin.site.register(models.ConfinePermission, ConfinePermissionAdminModel)
