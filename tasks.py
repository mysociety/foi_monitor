
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
try:
    from conf.ssh_creds import *  # move ssh creds into config
except:
    #server hosting static files
    MYSOC_SERVER = ""
    #key filename
    SSH_FILENAME = ""
    #if used, passphrase (use environ)
    SSH_PASSPHRASE = ""
    #destination (minus app name) on the server
    DESTINATION_ROOT = ""

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proj.settings")

django.setup()

app_name = settings.SITE_SLUG

destination_path = DESTINATION_ROOT + app_name
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


@task
def uploadzip(c):

    c = Connection(MYSOC_SERVER,
                   user=SSH_USER,
                   port=22,
                   connect_kwargs={"key_filename": SSH_FILENAME,
                                   "passphrase": SSH_PASSPHRASE})
    c.open()
    path, filename = os.path.split(bake_zip)

    sudo_password = ""
    while not sudo_password:
        sudo_password = getpass("sudo password: ")
    print("uploading {0}".format(filename))
    c.put(bake_zip, filename)
    #c.sudo('rm -rf {0}'.format(destination_path))
    c.sudo('unzip -o {0} -d {1}'.format(filename, destination_path),
           password=sudo_password)
    c.close()
