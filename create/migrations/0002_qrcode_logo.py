# Generated by Django 5.1.4 on 2025-02-15 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('create', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='qrcode',
            name='logo',
            field=models.ImageField(null=True, upload_to='img/logos'),
        ),
    ]
