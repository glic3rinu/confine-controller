from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    ssh_key = models.TextField("SSH Key")
