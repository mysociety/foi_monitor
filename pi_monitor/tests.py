"""
Tests for all pi_monitor views against the real populated database.

These tests verify that every view returns HTTP 200, renders the expected
template, and contains key context data. They use the real database with
source data from Cabinet Office and FOISA.
"""

from django.test import Client
from django.urls import reverse

import pytest

from pi_monitor.models import Jurisdiction, Property

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def foisa():
    return Jurisdiction.objects.get(slug="foisa")


@pytest.fixture
def cabinet():
    return Jurisdiction.objects.get(slug="cabinetfoi")


# ---- OverviewView ----


class TestOverviewView:
    def test_returns_200(self, client):
        url = reverse("pi:overview")
        response = client.get(url)
        assert response.status_code == 200

    def test_uses_correct_template(self, client):
        url = reverse("pi:overview")
        response = client.get(url)
        assert "pi_monitor/overview.html" in [t.name for t in response.templates]

    def test_context_contains_jurisdictions(self, client):
        url = reverse("pi:overview")
        response = client.get(url)
        jurisdictions = response.context["jurisdictions"]
        assert jurisdictions.count() == 2
        slugs = list(jurisdictions.values_list("slug", flat=True))
        assert "foisa" in slugs
        assert "cabinetfoi" in slugs


# ---- HomeView ----


class TestHomeView:
    def test_returns_200_foisa(self, client, foisa):
        url = reverse("pi:home", args=(foisa.slug,))
        response = client.get(url)
        assert response.status_code == 200

    def test_returns_200_cabinet(self, client, cabinet):
        url = reverse("pi:home", args=(cabinet.slug,))
        response = client.get(url)
        assert response.status_code == 200

    def test_uses_correct_template(self, client, foisa):
        url = reverse("pi:home", args=(foisa.slug,))
        response = client.get(url)
        assert "pi_monitor/home.html" in [t.name for t in response.templates]

    def test_context_has_jurisdiction(self, client, foisa):
        url = reverse("pi:home", args=(foisa.slug,))
        response = client.get(url)
        assert response.context["jurisdiction"] == foisa

    def test_context_has_charts(self, client, foisa):
        url = reverse("pi:home", args=(foisa.slug,))
        response = client.get(url)
        assert "all_time_chart" in response.context
        assert "over_time_chart" in response.context
        assert "type_distribution_chart" in response.context

    def test_context_has_years(self, client, foisa):
        url = reverse("pi:home", args=(foisa.slug,))
        response = client.get(url)
        assert len(response.context["years"]) > 0


# ---- PropertyView ----


class TestPropertyView:
    def test_returns_200_with_year(self, client, foisa):
        prop = foisa.properties.first()
        year = foisa.years.exclude(slug="alltime").first()
        url = reverse("pi:property", args=(foisa.slug, prop.slug, year.slug))
        response = client.get(url)
        assert response.status_code == 200

    def test_returns_200_alltime(self, client, foisa):
        prop = foisa.properties.first()
        url = reverse("pi:property", args=(foisa.slug, prop.slug, "alltime"))
        response = client.get(url)
        assert response.status_code == 200

    def test_returns_200_cabinet(self, client, cabinet):
        prop = cabinet.properties.first()
        year = cabinet.years.exclude(slug="alltime").first()
        url = reverse("pi:property", args=(cabinet.slug, prop.slug, year.slug))
        response = client.get(url)
        assert response.status_code == 200

    def test_uses_correct_template(self, client, foisa):
        prop = foisa.properties.first()
        year = foisa.years.exclude(slug="alltime").first()
        url = reverse("pi:property", args=(foisa.slug, prop.slug, year.slug))
        response = client.get(url)
        assert "pi_monitor/property.html" in [t.name for t in response.templates]

    def test_context_has_property_and_year(self, client, foisa):
        prop = foisa.properties.first()
        year = foisa.years.exclude(slug="alltime").first()
        url = reverse("pi:property", args=(foisa.slug, prop.slug, year.slug))
        response = client.get(url)
        assert response.context["property"].slug == prop.slug
        assert response.context["year"].slug == year.slug

    def test_property_with_child_of_has_percent_chart(self, client, foisa):
        """Properties that are children of another should have a percentage chart."""
        prop = Property.objects.filter(
            jurisdiction=foisa, child_of__isnull=False
        ).first()
        year = foisa.years.exclude(slug="alltime").first()
        url = reverse("pi:property", args=(foisa.slug, prop.slug, year.slug))
        response = client.get(url)
        assert "time_chart_percent" in response.context

    def test_context_has_tables(self, client, foisa):
        prop = foisa.properties.first()
        year = foisa.years.exclude(slug="alltime").first()
        url = reverse("pi:property", args=(foisa.slug, prop.slug, year.slug))
        response = client.get(url)
        assert "sector_table" in response.context
        assert "authority_table" in response.context


# ---- YearView ----


class TestYearView:
    def test_returns_200(self, client, foisa):
        year = foisa.years.exclude(slug="alltime").first()
        url = reverse("pi:year", args=(foisa.slug, year.slug))
        response = client.get(url)
        assert response.status_code == 200

    def test_returns_200_alltime(self, client, foisa):
        url = reverse("pi:year", args=(foisa.slug, "alltime"))
        response = client.get(url)
        assert response.status_code == 200

    def test_returns_200_cabinet(self, client, cabinet):
        year = cabinet.years.exclude(slug="alltime").first()
        url = reverse("pi:year", args=(cabinet.slug, year.slug))
        response = client.get(url)
        assert response.status_code == 200

    def test_uses_correct_template(self, client, foisa):
        year = foisa.years.exclude(slug="alltime").first()
        url = reverse("pi:year", args=(foisa.slug, year.slug))
        response = client.get(url)
        assert "pi_monitor/year.html" in [t.name for t in response.templates]

    def test_context_has_stats(self, client, foisa):
        year = foisa.years.exclude(slug="alltime").first()
        url = reverse("pi:year", args=(foisa.slug, year.slug))
        response = client.get(url)
        ctx = response.context
        assert "average" in ctx
        assert "median" in ctx
        assert "max" in ctx
        assert "relevant_auths" in ctx

    def test_context_has_tables_and_chart(self, client, foisa):
        year = foisa.years.exclude(slug="alltime").first()
        url = reverse("pi:year", args=(foisa.slug, year.slug))
        response = client.get(url)
        assert "sector_chart" in response.context
        assert "sector_table" in response.context
        assert "bodies_table" in response.context


# ---- BodyView ----


class TestBodyView:
    def test_returns_200_sector(self, client, foisa):
        sector = foisa.sectors().first()
        year = foisa.years.exclude(slug="alltime").first()
        url = reverse("pi:body", args=(foisa.slug, sector.slug, year.slug))
        response = client.get(url)
        assert response.status_code == 200

    def test_returns_200_body(self, client, cabinet):
        body = cabinet.bodies().first()
        year = cabinet.years.exclude(slug="alltime").first()
        url = reverse("pi:body", args=(cabinet.slug, body.slug, year.slug))
        response = client.get(url)
        assert response.status_code == 200

    def test_uses_correct_template(self, client, foisa):
        sector = foisa.sectors().first()
        year = foisa.years.exclude(slug="alltime").first()
        url = reverse("pi:body", args=(foisa.slug, sector.slug, year.slug))
        response = client.get(url)
        assert "pi_monitor/body.html" in [t.name for t in response.templates]

    def test_context_has_authority_and_chart(self, client, foisa):
        sector = foisa.sectors().first()
        year = foisa.years.exclude(slug="alltime").first()
        url = reverse("pi:body", args=(foisa.slug, sector.slug, year.slug))
        response = client.get(url)
        assert response.context["authority"] == sector
        assert "chart" in response.context

    def test_context_has_stats_tree(self, client, foisa):
        sector = foisa.sectors().first()
        year = foisa.years.exclude(slug="alltime").first()
        url = reverse("pi:body", args=(foisa.slug, sector.slug, year.slug))
        response = client.get(url)
        assert "stats_tree" in response.context


# ---- BodyStatisticView ----


class TestBodyStatisticView:
    def test_returns_200(self, client, foisa):
        body = (
            foisa.authorities.filter(render_full=True).exclude(is_overall=True).first()
        )
        prop = foisa.properties.first()
        url = reverse("pi:bodystat", args=(foisa.slug, body.slug, prop.slug))
        response = client.get(url)
        assert response.status_code == 200

    def test_returns_200_cabinet(self, client, cabinet):
        body = (
            cabinet.authorities.filter(render_full=True)
            .exclude(is_overall=True)
            .first()
        )
        prop = cabinet.properties.first()
        url = reverse("pi:bodystat", args=(cabinet.slug, body.slug, prop.slug))
        response = client.get(url)
        assert response.status_code == 200

    def test_uses_correct_template(self, client, foisa):
        body = (
            foisa.authorities.filter(render_full=True).exclude(is_overall=True).first()
        )
        prop = foisa.properties.first()
        url = reverse("pi:bodystat", args=(foisa.slug, body.slug, prop.slug))
        response = client.get(url)
        assert "pi_monitor/bodystat.html" in [t.name for t in response.templates]

    def test_context_has_time_chart(self, client, foisa):
        body = (
            foisa.authorities.filter(render_full=True).exclude(is_overall=True).first()
        )
        prop = foisa.properties.first()
        url = reverse("pi:bodystat", args=(foisa.slug, body.slug, prop.slug))
        response = client.get(url)
        assert "time_chart" in response.context

    def test_property_with_child_of_has_percent_charts(self, client, foisa):
        body = (
            foisa.authorities.filter(render_full=True).exclude(is_overall=True).first()
        )
        prop = Property.objects.filter(
            jurisdiction=foisa, child_of__isnull=False
        ).first()
        url = reverse("pi:bodystat", args=(foisa.slug, body.slug, prop.slug))
        response = client.get(url)
        assert "time_chart_percent" in response.context

    def test_context_has_year_table(self, client, foisa):
        body = (
            foisa.authorities.filter(render_full=True).exclude(is_overall=True).first()
        )
        prop = foisa.properties.first()
        url = reverse("pi:bodystat", args=(foisa.slug, body.slug, prop.slug))
        response = client.get(url)
        assert "year_table" in response.context


# ---- URL resolution ----


class TestURLResolution:
    """Verify all URL patterns resolve correctly."""

    def test_overview_url(self):
        assert reverse("pi:overview") == "/sites/foi-monitor/"

    def test_home_url(self):
        url = reverse("pi:home", args=("foisa",))
        assert url == "/sites/foi-monitor/foisa/"

    def test_property_url(self):
        url = reverse("pi:property", args=("foisa", "all_requests", "2020"))
        assert url == "/sites/foi-monitor/foisa/property/all_requests/2020/"

    def test_year_url(self):
        url = reverse("pi:year", args=("foisa", "2020"))
        assert url == "/sites/foi-monitor/foisa/years/2020/"

    def test_body_url(self):
        url = reverse("pi:body", args=("foisa", "local-government", "2020"))
        assert url == "/sites/foi-monitor/foisa/body/local-government/2020/"

    def test_bodystat_url(self):
        url = reverse("pi:bodystat", args=("foisa", "local-government", "all_requests"))
        assert (
            url
            == "/sites/foi-monitor/foisa/body/local-government/property/all_requests/"
        )


# ---- Data integrity ----


class TestDataIntegrity:
    """Basic checks that the populated database has expected data."""

    def test_two_jurisdictions_exist(self):
        assert Jurisdiction.objects.count() == 2

    def test_foisa_has_years(self, foisa):
        assert foisa.years.count() > 0

    def test_cabinet_has_years(self, cabinet):
        assert cabinet.years.count() > 0

    def test_foisa_has_authorities(self, foisa):
        assert foisa.authorities.count() > 0

    def test_foisa_has_properties(self, foisa):
        assert foisa.properties.count() > 0

    def test_values_exist(self):
        from pi_monitor.models import Value

        assert Value.objects.count() > 0

    def test_foisa_has_sectors(self, foisa):
        assert foisa.sectors().count() > 0

    def test_cabinet_has_sectors(self, cabinet):
        assert cabinet.sectors().count() > 0

    def test_each_jurisdiction_has_overall_authority(self):
        for j in Jurisdiction.objects.all():
            assert j.authorities.filter(is_overall=True).count() == 1
