from .settings import *  # noqa: F403

print("using bake settings")

DEBUG = False
HTML_MINIFY = not DEBUG
SITE_ROOT = "https://research.mysociety.org/sites"
IS_LIVE = True
STORAGES = {
    "staticfiles": {
        "BACKEND": "pipeline.storage.PipelineStorage",
    },
}

DISABLE_APPS = ["django.contrib.admin", "debug_toolbar"]

INSTALLED_APPS = [x for x in INSTALLED_APPS if x not in DISABLE_APPS]  # noqa: F405



MIDDLEWARE = (
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    #'django.contrib.sessions.middleware.SessionMiddleware',
    "django.middleware.common.CommonMiddleware",
    #'django.middleware.csrf.CsrfViewMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "htmlmin.middleware.HtmlMinifyMiddleware",
    "htmlmin.middleware.MarkRequestMiddleware",
)

INTERNAL_IPS = []

DISTILL_DIR = BAKE_LOCATION  # noqa: F405
