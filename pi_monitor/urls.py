from django_distill import distill_path

from . import views
from .models import Jurisdiction

app_name = "pi"


def distill_overview():
    return [{}]


def distill_home():
    for j in Jurisdiction.objects.all():
        yield {"jurisdiction_slug": j.slug}


def distill_property():
    for j in Jurisdiction.objects.all():
        for p in j.properties.all():
            for y in j.years.all():
                yield {
                    "jurisdiction_slug": j.slug,
                    "property_slug": p.slug,
                    "year_slug": y.slug,
                }


def distill_bodystat():
    for j in Jurisdiction.objects.all():
        for a in j.authorities.filter(render_full=True):
            for p in j.properties.all():
                yield {
                    "jurisdiction_slug": j.slug,
                    "body_slug": a.slug,
                    "property_slug": p.slug,
                }


def distill_body():
    for j in Jurisdiction.objects.all():
        for a in j.authorities.all():
            for y in a.valid_years():
                yield {
                    "jurisdiction_slug": j.slug,
                    "body_slug": a.slug,
                    "year_slug": y.slug,
                }


def distill_year():
    for j in Jurisdiction.objects.all():
        for y in j.years.all():
            yield {
                "jurisdiction_slug": j.slug,
                "year_slug": y.slug,
            }


urlpatterns = [
    distill_path(
        "",
        views.OverviewView.as_view(),
        name="overview",
        distill_func=distill_overview,
    ),
    distill_path(
        "<slug:jurisdiction_slug>/property/<slug:property_slug>/<slug:year_slug>/",
        views.PropertyView.as_view(),
        name="property",
        distill_func=distill_property,
    ),
    distill_path(
        "<slug:jurisdiction_slug>/body/<slug:body_slug>/property/<slug:property_slug>/",
        views.BodyStatisticView.as_view(),
        name="bodystat",
        distill_func=distill_bodystat,
    ),
    distill_path(
        "<slug:jurisdiction_slug>/body/<slug:body_slug>/<slug:year_slug>/",
        views.BodyView.as_view(),
        name="body",
        distill_func=distill_body,
    ),
    distill_path(
        "<slug:jurisdiction_slug>/years/<slug:year_slug>/",
        views.YearView.as_view(),
        name="year",
        distill_func=distill_year,
    ),
    distill_path(
        "<slug:jurisdiction_slug>/",
        views.HomeView.as_view(),
        name="home",
        distill_func=distill_home,
    ),
]
