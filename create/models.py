
import os
from django.db import models
from django.contrib.auth.models import User

def user_directory_path(instance, filename):
    return os.path.join(instance.user.username, filename)  




class Qrcode(models.Model):
    name = models.CharField(max_length=255)
    link = models.URLField()
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Conexão com a conta
    created_at = models.DateTimeField(auto_now_add=True)
    logo = models.ImageField(upload_to='img/logos', null=True)
    free = models.BooleanField(default=False)
    standard= models.BooleanField(default=False)
    pro = models.BooleanField(default=False)
    

   


    def __str__(self):
        return f"{self.name} - {self.user.username}"


class QrcodeLimit(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Criamos campos de limite de código QR que podem conter apenas números positivos
    limit_standard = models.PositiveBigIntegerField(default=10)
    limit_pro = models.PositiveBigIntegerField(default=20)