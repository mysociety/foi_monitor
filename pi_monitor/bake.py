"""
Static site generation support (legacy).

This file provides support for static site generation using the old django-sourdough
baking functionality. This is kept for backward compatibility but is not needed for
running this as a standard Django application.

If you need static site generation, you may need to:
1. Re-add django-sourdough as a dependency
2. Update this file to work with the new view structure
"""
import os
from dirsync import sync

from django.conf import settings


# Note: BaseBakeManager is from django-sourdough which has been removed
# If you need baking functionality, you'll need to implement it differently
# or re-add django-sourdough as a dependency

class BakeManager:
    """
    Legacy bake manager for static site generation.
    
    This is no longer functional without django-sourdough.
    Kept for reference only.
    """

    def copy_media_files(self):
        """Copy media files to bake location."""
        if not hasattr(settings, 'BAKE_LOCATION'):
            raise ValueError("BAKE_LOCATION not configured in settings")
        
        dir_loc = os.path.join(settings.BAKE_LOCATION, "media")
        print("syncing media")
        if os.path.isdir(dir_loc) is False:
            os.makedirs(dir_loc)
        sync(settings.MEDIA_ROOT, dir_loc, "sync", ctime=True)

    def amend_settings(self, **kwargs):
        """Amend settings for baking."""
        settings.IS_LIVE = True
        settings.EXPORT_CHARTS = True

