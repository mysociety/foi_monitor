from django.conf import settings
from django.conf.urls.static import static
from django.http.response import HttpResponse
from django.urls import include, path

import debug_toolbar

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


def holder_frontpage(request):
    """
    quick holding page to make the default url nicer
    """
    template = 'Did you mean <a href="/sites/{0}/">/sites/{0}/'
    return HttpResponse(template.format(settings.SITE_SLUG))


urlpatterns += [
    path("", holder_frontpage),
    path("__debug__/", include(debug_toolbar.urls)),
    path(
        f"sites/{settings.SITE_SLUG}/",
        include(f"{settings.CORE_APP_NAME}.urls"),
    ),
]
