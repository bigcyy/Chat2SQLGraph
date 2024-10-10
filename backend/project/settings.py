import os
from .const import CONFIG
from django.core.management.utils import get_random_secret_key


DEBUG = True
CORS_ALLOW_ALL_ORIGINS = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'rest_framework',
    'user',
    'common',
    'setting',
    'chat',
    'django.contrib.staticfiles',  # required for serving swagger ui's css/js files
    'drf_yasg',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

STATIC_URL = '/static/'

# 使用环境变量或生成一个随机的 SECRET_KEY
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', get_random_secret_key())

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

JWT_TOKEN_EXPIRE_TIME = 3600 * 12  # 12小时
JWT_SECRET = '123456'
JWT_ALGORITHM = 'HS256'

DATABASES = {
    "default": CONFIG.get_db_settings(),
}

ROOT_URLCONF = 'project.urls'

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'EXCEPTION_HANDLER': 'common.handler.exception_handler.handle_exception',
    'DEFAULT_AUTHENTICATION_CLASSES': ['common.auth.authenticate.AnonymousAuthentication']
}


#  缓存配置
CACHES = {
    "default": {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 60 * 30,
        'OPTIONS': {
            'MAX_ENTRIES': 150,
            'CULL_FREQUENCY': 5,
        }
    }
}

# swagger 配置
SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'DEFAULT_MODEL_RENDERING': 'example'
}
