from django.conf.global_settings import *  # noqa

SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    'django.contrib.sessions',
    'django.contrib.gis',
    "tests",
    "leaflet_storage",
]
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'testdb',
    }
}
ROOT_URLCONF = 'leaflet_storage.urls'
MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': (),
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages'
            ]
        }
    },
]
LOGIN_URL = '/login/'
SITE_URL = 'http://domain.org'
TEST_RUNNER = 'leaflet_storage.runner.Runner'
LEAFLET_STORAGE_KEEP_VERSIONS = 10
