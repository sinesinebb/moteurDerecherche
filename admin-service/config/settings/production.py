from .base import *

DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']  # doit être défini
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Sécurité renforcée
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
