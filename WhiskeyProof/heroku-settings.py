from .settings import *
import dj_database_url


DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ["*"]

DATABASES['default'] = dj_database_url.config()

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

# make sure to include any directories that might be outside of the app/static directories.
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, '../global/'),
# )


