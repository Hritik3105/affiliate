# Generated by Django 4.2.1 on 2023-07-24 11:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('CampaignApp', '0011_transferdetails_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentdetails',
            name='admin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='adminpayment', to=settings.AUTH_USER_MODEL),
        ),
    ]