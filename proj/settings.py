# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from conf.config import *  # stores database and key outside repo
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STATIC_ROOT = os.path.join(BASE_DIR, "static")

DEBUG = True

if DEBUG:
    DEBUG = True
    IS_LIVE = False
    SITE_ROOT = "http://127.0.0.1:8000"
    STATICFILES_STORAGE = "pipeline.storage.NonPackagingPipelineStorage"
else:
    SITE_ROOT = "https://research.mysociety.org/sites"
    DEBUG = False
    IS_LIVE = True
    STATICFILES_STORAGE = "pipeline.storage.PipelineStorage"


ALLOWED_HOSTS = ["127.0.0.1", "testserver"]

LANGUAGE_CODE = "en-uk"

PROJECT_PATH = os.path.dirname(os.path.realpath(os.path.dirname(__file__)))

PI_ADAPTERS = ["pi_monitor.adapters.foisa", "pi_monitor.adapters.cabinetoffice"]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            PROJECT_PATH + "/templates/",
            PROJECT_PATH + "/research_common/templates/",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "proj.universal.universal_context",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

MEDIA_ROOT = PROJECT_PATH + "/media/"

STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, "web"),
    os.path.join(PROJECT_PATH, "theme"),
)

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "bootstrapform",
    "import_export",
    "pipeline",
    "research_common.apps.ResearchCommonConfig",
    "debug_toolbar",
    CORE_APP_NAME,
]

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "databases", "db.sqlite3"),
    },
}


MIDDLEWARE = (
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "htmlmin.middleware.HtmlMinifyMiddleware",
    "htmlmin.middleware.MarkRequestMiddleware",
)


INTERNAL_IPS = [
    "127.0.0.1",
]

ROOT_URLCONF = "proj.urls"

WSGI_APPLICATION = "proj.wsgi.application"

HTML_MINIFY = not DEBUG

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = False

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = "/sites/" + SITE_SLUG + "/static/"
MEDIA_URL = "/sites/" + SITE_SLUG + "/media/"

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "pipeline.finders.PipelineFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

PIPELINE = {
    "STYLESHEETS": {
        "main": {
            "source_filenames": ("sass/global.scss",),
            "output_filename": "css/main.css",
        },
    },
    "CSS_COMPRESSOR": "django_pipeline_csscompressor.CssCompressor",
    "DISABLE_WRAPPER": True,
    "COMPILERS": ("pipeline.compilers.sass.SASSCompiler",),
    "SHOW_ERRORS_INLINE": False,
    "SASS_BINARY": SASSC_LOCATION,
}

EXPORT_CHARTS = False
FORCE_EXPORT_CHARTS = False

COMMAND_SPECIFIC_SETTINGS = [
    ("bake", "proj.bake_settings"),
    ("collectstatic", "proj.bake_settings"),
]
