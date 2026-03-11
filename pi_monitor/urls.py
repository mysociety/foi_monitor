from django.urls import path

from . import views

app_name = "pi"

urlpatterns = [
    path("", views.OverviewView.as_view(), name="overview"),
    path(
        "<slug:jurisdiction_slug>/property/<slug:property_slug>/<slug:year_slug>/",
        views.PropertyView.as_view(),
        name="property",
    ),
    path(
        "<slug:jurisdiction_slug>/body/<slug:body_slug>/property/<slug:property_slug>/",
        views.BodyStatisticView.as_view(),
        name="bodystat",
    ),
    path(
        "<slug:jurisdiction_slug>/body/<slug:body_slug>/<slug:year_slug>/",
        views.BodyView.as_view(),
        name="body",
    ),
    path(
        "<slug:jurisdiction_slug>/years/<slug:year_slug>/",
        views.YearView.as_view(),
        name="year",
    ),
    path("<slug:jurisdiction_slug>/", views.HomeView.as_view(), name="home"),
]
