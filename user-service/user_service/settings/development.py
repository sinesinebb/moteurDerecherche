from .base import *

DEBUG = True
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'fallback-dev-key')
