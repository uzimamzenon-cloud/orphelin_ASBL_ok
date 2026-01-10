import os
from pathlib import Path

# Construit les chemins à l'intérieur du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SÉCURITÉ ---
SECRET_KEY = 'django-insecure-cle-de-test-a-changer-en-production'

# Détection de Render pour le mode DEBUG
IS_IN_PRODUCTION = 'RENDER' in os.environ
DEBUG = not IS_IN_PRODUCTION  # True sur ton PC, False sur Render

# On autorise ton PC et l'adresse de ton site
ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1', '.onrender.com', 'orphelin-asbl.onrender.com']

# --- APPLICATIONS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Tes applications
    'messagerie.apps.MessagerieConfig',
    'corsheaders',
]

# --- MIDDLEWARE (L'ordre est crucial pour WhiteNoise et CORS) ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # DOIT être ici pour les images/CSS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # Indispensable avant CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'Config.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # On dit à Django de chercher le dossier 'templates' à la racine
        'DIRS': [BASE_DIR / 'templates'], 
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

WSGI_APPLICATION = 'config.wsgi.application'

# --- BASE DE DONNÉES (SQLite) ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- FICHIERS STATIQUES (CSS, JS, IMAGES) ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# On dit à Django que nos fichiers sont dans le dossier 'static' à la racine
STATICFILES_DIRS = STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Configuration WhiteNoise pour servir les fichiers efficacement
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --- CONFIGURATION CORS (Pour que le JS puisse parler au Backend) ---
CORS_ALLOW_ALL_ORIGINS = True 

# Sécurité pour le déploiement
if IS_IN_PRODUCTION:
    CSRF_TRUSTED_ORIGINS = ['https://orphelin-asbl.onrender.com']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'