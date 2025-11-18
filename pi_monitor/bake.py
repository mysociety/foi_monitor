import os
from dirsync import sync

from django.conf import settings

from django_sourdough.views import BaseBakeManager


class BakeManager(BaseBakeManager):
    """
    add support for copying media files
    """

    def copy_media_files(self):
        dir_loc = os.path.join(settings.BAKE_LOCATION, "media")
        print("syncing media")
        if os.path.isdir(dir_loc) is False:
            os.makedirs(dir_loc)
        sync(settings.MEDIA_ROOT, dir_loc, "sync", ctime=True)

    def amend_settings(self, **kwargs):
        super(BakeManager, self).amend_settings(**kwargs)
        settings.IS_LIVE = True
        settings.EXPORT_CHARTS = True

    # def bake_app(self):
    #    self.app_urls.bake(only_absent=True) #
    #    #self.copy_media_files()
