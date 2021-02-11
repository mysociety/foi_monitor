
import debug_toolbar

from django.conf.urls import include, url
from django.urls import path
from django.http.response import HttpResponse
from django.contrib import admin
from django_sourdough.views import AppUrl, include_view
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


def holder_frontpage(request):
    """
    quick holding page to make the default url nicer
    """
    template = 'Did you mean <a href="/sites/{0}/">/sites/{0}/'
    return HttpResponse(template.format(settings.SITE_SLUG))


urlpatterns += [
    path('', holder_frontpage),
    path('__debug__/', include(debug_toolbar.urls)),
    url(r'^sites/{0}/'.format(settings.SITE_SLUG),
        include_view('{0}.views'.format(settings.CORE_APP_NAME))),
]
