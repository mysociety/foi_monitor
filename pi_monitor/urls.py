from django.urls import re_path

from . import views

app_name = "pi"

urlpatterns = [
    re_path(r"^$", views.OverviewView.as_view(), name="overview"),
    re_path(r"^(?P<jurisdiction_slug>.*)/property/(?P<property_slug>.*)/(?P<year_slug>.*)/$", views.PropertyView.as_view(), name="property"),
    re_path(r"^(?P<jurisdiction_slug>.*)/body/(?P<body_slug>.*)/property/(?P<property_slug>.*)/$", views.BodyStatisticView.as_view(), name="bodystat"),
    re_path(r"^(?P<jurisdiction_slug>.*)/body/(?P<body_slug>.*)/(?P<year_slug>.*)/$", views.BodyView.as_view(), name="body"),
    re_path(r"^(?P<jurisdiction_slug>.*)/years/(?P<year_slug>.*)/$", views.YearView.as_view(), name="year"),
    re_path(r"^(?P<jurisdiction_slug>.*)/$", views.HomeView.as_view(), name="home"),
]
