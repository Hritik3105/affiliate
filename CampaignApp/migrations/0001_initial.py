# Generated by Django 4.1.7 on 2023-06-21 12:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campaign_name', models.CharField(default='', max_length=255)),
                ('influencer_visit', models.CharField(blank=True, max_length=255, null=True)),
                ('offer', models.CharField(max_length=255, null=True)),
                ('influencer_name', models.CharField(default='', max_length=255)),
                ('date', models.DateField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.IntegerField(choices=[('1', 'Marketplace'), ('2', 'Influencer')], default=0)),
                ('description', models.TextField(default='')),
                ('campaign_status', models.IntegerField(choices=[('0', 'Inactive'), ('1', 'Active')], default=0)),
                ('draft_status', models.BooleanField(default=0)),
                ('influencer_fee', models.FloatField(blank=True, null=True)),
                ('campaign_exp', models.BooleanField(default=True)),
                ('end_date', models.DateField(null=True)),
                ('influencerid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='influencer', to=settings.AUTH_USER_MODEL)),
                ('vendorid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ModashInfluencer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default='', max_length=255)),
                ('follower', models.BigIntegerField()),
                ('image', models.ImageField(blank=True, default='', max_length=500, upload_to='')),
                ('engagements', models.BigIntegerField(null=True)),
                ('engagement_rate', models.FloatField()),
                ('fullname', models.CharField(default='', max_length=255)),
                ('isverified', models.BooleanField(null=True)),
                ('influencerid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='VendorStripeDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('publishable_key', models.CharField(blank=True, max_length=255)),
                ('secret_key', models.CharField(blank=True, max_length=255)),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='VendorCampaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campaign_status', models.IntegerField(default=0)),
                ('campaignid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='CampaignApp.campaign')),
                ('influencerid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='CampaignApp.modashinfluencer')),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RequestSent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('influencee', models.CharField(max_length=200, null=True)),
                ('status', models.BooleanField(default=0)),
                ('campaignid', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='CampaignApp.campaign')),
                ('vendorid', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Productdetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.CharField(default='', max_length=255)),
                ('vendorid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Product_information',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=255, null=True)),
                ('product_id', models.BigIntegerField(null=True)),
                ('coupon_name', models.TextField(blank=True, null=True)),
                ('amount', models.TextField(blank=True)),
                ('campaignid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='CampaignApp.campaign')),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(blank=True, null=True)),
                ('amountpaid', models.FloatField(blank=True, null=True)),
                ('sales', models.FloatField(blank=True, null=True)),
                ('influencerfee', models.FloatField(blank=True, null=True)),
                ('offer', models.CharField(blank=True, max_length=200, null=True)),
                ('campaign', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='CampaignApp.campaign')),
                ('influencer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='CampaignApp.modashinfluencer')),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('send_notification', models.IntegerField(default=0)),
                ('message', models.TextField(default='')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('campaignid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='CampaignApp.campaign')),
                ('influencerid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='CampaignApp.modashinfluencer')),
                ('vendor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Campaign_accept',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campaign_status', models.IntegerField(default=0)),
                ('modashinfluencer', models.IntegerField(blank=True, null=True)),
                ('campaignid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='CampaignApp.campaign')),
                ('influencerid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='influencer_accept', to=settings.AUTH_USER_MODEL)),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]