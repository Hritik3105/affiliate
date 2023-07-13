"""
Django settings for Affilate_Marketing project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import pymysql
 pymysql.version_info = (1, 4, 6, 'final', 0)
pymysql.install_as_MySQLdb()
from decouple import config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-5w&&1euej3vf@2r-s9p&+te=-4kjgkmx3wu!+t*0hv4qo$y8h3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = []
ALLOWED_HOSTS = ["13.50.106.134","myrefera.com","api.myrefera.com","admin.myrefera.com"]


# Application definition

INSTALLED_APPS = [
    'django_crontab',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'rest_framework.authtoken',
    'active_link',
    'AdminApp',
    'InfluencerApp',
    'CampaignApp',
    'ShopifyApp',
    'StoreApp',
]


CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOWED_ORIGINS = [
    'https://myrefera.com',
    'https://api.myrefera.com',
    'http://localhost:3000',
    'https://admin.myrefera.com',
    
]
CORS_ORIGIN_WHITELIST = [
    'https://myrefera.com',
    'https://api.myrefera.com',
    'http://localhost:3000',
    'https://admin.myrefera.com',
]


AUTH_USER_MODEL = 'AdminApp.user'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Affilate_Marketing.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
               
            ],
        },
    },
]

WSGI_APPLICATION = 'Affilate_Marketing.wsgi.application'


CRONJOBS = [
    ('*/1 * * * *', 'CampaignApp.cron.update_campaign_status')
]



# CRONJOBS = [
#     ('0 0 * * *', 'CampaignApp.cron.update_campaign_status')
# ]
# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'marketing_db',
#         'USER':'root',
#         "HOST":"localhost",
#         'PASSWORD':"",
#         "PORT":"3306"
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME':config("NAME"),
        'USER':config("USER"),
        "HOST":config("HOST"),
        'PASSWORD':config("PASSWORD"),
        "PORT":config("PORT")
    }
}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
}



# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static/'),
]
# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field


LOGIN_URL="/isadmin/login1/"



EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST_USER ="testing21032023@gmail.com"
EMAIL_HOST ="smtp.gmail.com"
EMAIL_PORT = 587 
EMAIL_USE_TLS = True 
EMAIL_HOST_PASSWORD = "ozureuoxxvhlqgag"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

base_url="https://marketplacee-app.myshopify.com/admin/api/2023-01/products.json"
headers = {"X-Shopify-Access-Token": "54205eb781a282b00bfa15f2de968559e27efa71"}


SHOPIFY_API_KEY = config("SHOPIFY_API_KEY")
SHOPIFY_API_SECRET = config("SHOPIFY_API_SECRET")
SHOPIFY_PRODUCT=config("shopify_products")
app_name=config("app_name")
redirect_url=config("redirect_uri")
shopify_scopes=config("scopes")
MODASH_HEADER=config("modash_header")
API_VERSION=config("api_version")

CSRF_TRUSTED_ORIGINS=['https://api.myrefera.com','https://admin.myrefera.com']


MEDIA_URL= 'image/'
MEDIA_ROOT = os.path.join(BASE_DIR,'static/image/')

STRIPE_API_KEY=config("STRIPE_API_KEY")
STRIPE_PUBLISHABLE_KEY=config("STRIPE_PUBLISHABLE_KEY")


STRIPE_PRICE_ID_BASIC =config("STRIPE_PRICE_ID_BASIC")
STRIPE_PRICE_ID_PREMIUM =config("STRIPE_PRICE_ID_PREMIUM")
STRIPE_PRICE_ID_ADVANCED= config("STRIPE_PRICE_ID_ADVANCED")