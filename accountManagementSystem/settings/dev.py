from .general import *

SECRET_KEY = 'django-insecure-p$v=ys_ar9yny3vf273sj3tg&m!&#vvdak-gmlciegw6$nxq+h'
DEBUG = True
ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        # 'NAME': 'account_db',
        # 'USER': 'postgres',
        # 'PASSWORD': 'Solomon11',
        # 'HOST': 'localhost',
        # 'PORT': 5432
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 2525
DEFAULT_FROM_EMAIL = 'info@jagudabank.com'
