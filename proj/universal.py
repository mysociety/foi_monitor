from django.conf import settings  # import the settings file

SITE_NAME = ""

MAIN_MENU = []


def universal_context(request):
    """
    returns helpful universal context to the views
    """

    return {'IS_LIVE': settings.IS_LIVE,
            'settings': settings,
            'request': request,
            'current_path': settings.SITE_ROOT + request.get_full_path(),
            'main_menu': MAIN_MENU,
            'site_name': SITE_NAME,
            'SITE_ROOT': settings.SITE_ROOT}
