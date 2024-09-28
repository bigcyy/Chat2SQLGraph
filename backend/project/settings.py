from .const import CONFIG

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'rest_framework',
    'user',
    'common',
    'setting',
    'chat'
]

JWT_TOKEN_EXPIRE_TIME = 3600 * 2  # 2小时
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
