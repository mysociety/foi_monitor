
from django.conf import settings
from django.core.management import execute_from_command_line
import os
import sys
import shutil
import django

from invoke import task, Exit
from invoke.context import Context
from pathlib import Path
from fabric import Connection
from getpass import getpass

try:
    os.environ.pop("DJANGO_SETTINGS_MODULE")
except Exception:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proj.settings")

django.setup()

app_name = settings.SITE_SLUG

bake_dir = settings.BAKE_LOCATION + "/sites/" + app_name + "/"
bake_zip = settings.BAKE_LOCATION + "/sites/" + app_name + ".zip"


def do_django_command(*args):
    ll = ["manage.py"] + [x for x in args if x]
    execute_from_command_line(ll)


@task
def makemigrations(c):
    do_django_command("makemigrations")


@task
def migrate(c):
    do_django_command("migrate")


@task
def populate(c):
    do_django_command("populate")


@task
def bake(c):
    do_django_command("bake")


@task
def collectstatic(c):
    do_django_command("collectstatic", "--noinput")


@task
def bakezip(c):
    print("creating {0}".format(bake_zip))
    shutil.make_archive(bake_zip[:-4], 'zip', bake_dir)


@task
def broadcast(c):
    do_django_command("runserver", "0.0.0.0:8000")