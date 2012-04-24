from django.contrib import admin
from django.contrib.auth.models import User
from models import UserProfile
from confine_utils.admin import insert_inline

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 0


insert_inline(User, UserProfileInline)
