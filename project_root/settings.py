

import os
from pathlib import Path
from decouple import config
from dotenv import load_dotenv 
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-$5h3i2#$qg#58b1)j00cluqvel2&rp_e^fp**(8f&xyl)!$l71'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
  
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # app 
   'all_club',
    'myapp' ,
    'owner.apps.OwnerConfig',
    'subscriptions',
    
    # framework 
    'rest_framework',
]




CSRF_TRUSTED_ORIGINS = [
    "https://tripersonal-homelessly-felecia.ngrok-free.app",
 
]



MIDDLEWARE = [
        
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]





# Twilio API configuration
INFOBIP_API_KEY = config("INFOBIP_API_KEY")
INFOBIP_BASE_URL = config("INFOBIP_BASE_URL")



# settings.py (add these)
import os

STRIPE_API_KEY = config("STRIPE_API_KEY")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")
GOOGLE_API_KEY = config("GOOGLE_API_KEY")
OPENAI_API_KEY = config("OPENAI_API_KEY")

# settings.py
GEOAPIFY_API_KEY = config("GEOAPIFY_API_KEY")
print("GEOAPIFY_API_KEY:", GEOAPIFY_API_KEY)


STRIPE_PRICE_IDS = {
    "starter_monthly": "price_1SKuaoCk78tT87fWg4orhRlP",
    "starter_yearly":  "price_XXXXXXXXXXXX_yearly",
    "pro_monthly":     "price_1SKucpCk78tT87fWI95Yy8q8",
    "pro_yearly":      "price_YYYYYYYYYYYY_yearly",
   
}


STRIPE_COUPONS = {
    "FOMO50": "coupon_XXXXXXXXX"
}

FRONTEND_URL = "http://127.0.0.1:4040/stripe/"


AUTH_USER_MODEL = 'owner.User'

AUTHENTICATION_BACKENDS = [
    'owner.backends.EmailBackend', 
]





ROOT_URLCONF = 'project_root.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
     
}


# Email Configuration from .env file
EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)  
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')



CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "https://tripersonal-homelessly-felecia.ngrok-free.app"
]



# settings.py (add)




# Celery settings (example)
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Dhaka"

CELERY_BEAT_SCHEDULE = {
    "sync-nightclubs-every-day": {
        "task": "nightlife.tasks.fetch_all_city_nightclubs",
        "schedule": 60 * 60 * 24,  # once per day
    }
}



from datetime import timedelta



SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=7),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),     
    "ROTATE_REFRESH_TOKENS": True,                 
    "BLACKLIST_AFTER_ROTATION": True,                
    
 
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),

}


WSGI_APPLICATION = 'project_root.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


TEMP_MEDIA_ROOT = os.path.join(BASE_DIR, 'temp_media')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/


MEDIA_URL = '/media/'
STATIC_URL = 'static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')





TEMP_MEDIA_ROOT = os.path.join(MEDIA_ROOT, 'tmp')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# nightclub@gmail.com
# 123