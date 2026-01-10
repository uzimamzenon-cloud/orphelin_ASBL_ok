import os
from pathlib import Path

# --- CHEMINS ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SÉCURITÉ ---
SECRET_KEY = 'django-insecure-cle-de-test-a-changer-en-production'
DEBUG = True  # Laisse True pour débugger, mets False quand tout sera fini
ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1', 'orphelin-asbl.onrender.com']

# --- APPLICATIONS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # Static pro
    'django.contrib.staticfiles',
    
    'messagerie.apps.MessagerieConfig',
    'corsheaders',
]

# --- MIDDLEWARE (L'ordre est très strict !) ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # DOIT être ici
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ⚠️ CORRECTION : Ici on met le nom EXACT de ton dossier (configuration)
ROOT_URLCONF = 'configuration.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Ton dossier HTML
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

# ⚠️ CORRECTION : Ici aussi
WSGI_APPLICATION = 'configuration.wsgi.application'

# --- BASE DE DONNÉES ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- FICHIERS STATIQUES (Images, CSS, JS) ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Version moderne WhiteNoise pour Django
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --- SÉCURITÉ ---
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = ['https://orphelin-asbl.onrender.com', 'http://127.0.0.1:8000']

# --- CONFIGURATION EMAIL (GMAIL) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'uzimamzenon@gmail.com'
# Ce code de 16 lettres doit être dans ton onglet "Environment" sur Render
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'dktj wksi qcpk lewn') 
DEFAULT_FROM_EMAIL = f"Orphelin Priorité ASBL <{EMAIL_HOST_USER}>"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'