# -*- coding: utf-8 -*-

import altair as alt
import numpy as np
import pandas as pd
from research_common.charts import (
    AltairChart,
    Table,
    query_to_df,
    group_to_other,
    theme,
)
from research_common.views import AnchorChartsMixIn
from django.conf import settings
from django.db.models import Q
from django.urls import reverse
from django.utils.html import conditional_escape

from .base_views import StandardLogicalView
from .models import (
    Authority,
    Jurisdiction,
    Property,
    Value,
    Year,
    fix_percentage,
    get_link,
    intcomma,
)


class GenericSocial(object):
    share_image = "http://research.mysociety.org/static/img/mysociety-circles-social.e9fe1879ff6d.png"
    twitter_share_image = "http://research.mysociety.org/static/img/mysociety-circles-social.e9fe1879ff6d.png"
    share_site_name = "mySociety Research"
    share_twitter = "@mysociety"


class LocalView(AnchorChartsMixIn, GenericSocial, StandardLogicalView):
    chart_storage_slug = "foi-monitor"

    def extra_params(self, context):
        params = super().extra_params(context)
        if hasattr(settings, "SITE_ROOT"):
            params["SITE_ROOT"] = settings.SITE_ROOT
        extra = {
            "social_settings": self.social_settings(params),
            "page_title": self._page_title(params),
        }
        params.update(extra)
        return params


class OverviewView(LocalView):
    template_name = "pi_monitor/overview.html"
    share_title = "Public Information Statistics"
    page_title = "Public Information Statistics"
    share_description = "Explore FOI information for different jurisdictions"

    def logic(self):
        self.jurisdictions = Jurisdiction.objects.all().order_by("name")


class HomeView(LocalView):
    template_name = "pi_monitor/home.html"
    share_title = "{{jurisdiction.name}} Statistics"
    page_title = "{{jurisdiction.name}} Statistics"
    share_description = (
        "Explore public information statistics for {{jurisdiction.name}}"
    )

    def bake_args(self):
        for j in Jurisdiction.objects.all():
            yield (j.slug,)

    def logic(self):
        self.jurisdiction = Jurisdiction.objects.get(slug=self.jurisdiction_slug)
        self.desc = self.jurisdiction.adapter().get_description()
        self.years = list(self.jurisdiction.years.order_by("number"))
        self.current_year = self.years[-1].number
        self.all_time_chart = self.get_all_time_chart(self.jurisdiction)
        self.over_time_chart = self.get_over_time_chart(self.jurisdiction)
        self.type_distribution_chart = self.get_type_distribution_chart(
            self.jurisdiction
        )

    def get_over_time_chart(self, jurisdiction):
        """
        gets the all time number of requests split by sector and year
        """

        title = "Change over time by sector ({0})".format(jurisdiction.geo_label())

        year_values = Value.objects.filter(
            authority__in=jurisdiction.sectors(), property__special="PI_ALL"
        )
        year_values = year_values.exclude(year__number=9999)

        chart = AltairChart(name=title, title=title, chart_type="line")

        chart.header["authority__name"] = "Sector"
        chart.header["year__number"] = "Year"
        chart.header["value"] = "Public information requests"

        df = chart.apply_query(year_values)

        df = group_to_other(
            df,
            "Public information requests",
            "Year",
            "Sector",
            cut_off=3,
            other_label="Other sectors",
        )
        chart.df = df

        pir = df["Public information requests"]
        df["percentage"] = pir / pir.sum()

        chart.set_options(
            y="Public information requests",
            x=alt.X("Year", title=""),
            tooltip=[
                "Sector",
                "Year",
                alt.Tooltip("Public information requests", title="PIRs", format=","),
                alt.Tooltip("percentage", format=",.2%"),
            ],
            color=alt.Color("Sector", sort="-y"),
        )

        years = df["Year"].unique()
        years.sort()

        chart.options["x"].axis = alt.Axis(format="d", values=years)

        return chart

    def get_all_time_chart(self, jurisdiction):
        """
        gets the all time number of requests split by sector
        """

        title = "Public information requests by sector ({0})".format(
            jurisdiction.geo_label()
        )

        year_values = Value.objects.filter(
            authority__in=jurisdiction.sectors(),
            property__special="PI_ALL",
            year__number=9999,
        )

        chart = AltairChart(name=title, title=title, chart_type="bar")

        header = {
            "authority__name": "Sector",
            "year__number": "Year",
            "value": "Public information requests",
        }

        chart.header = header
        df = chart.apply_query(year_values)

        year_totals = (
            df.groupby(["Year"]).sum().to_dict()["Public information requests"]
        )

        def func(r):
            return r["Public information requests"] / year_totals[r["Year"]]

        df["Percentage in year"] = df.apply(func, axis="columns")

        chart.set_options(
            y=alt.Y("Sector", sort="-x", title=""),
            x="Public information requests",
            tooltip=[
                "Sector",
                alt.Tooltip("Public information requests", title="PIRs", format=","),
                alt.Tooltip("Percentage in year", format="%"),
            ],
        )

        chart.set_text_options(
            text=alt.Text("Public information requests", format=".2s"),
            align="left",
            baseline="middle",
            dx=3,
        )

        chart.data_source = "Data source: " + jurisdiction.data_source()

        chart.options["x"].axis = alt.Axis(format="s")

        return chart

    def get_type_distribution_chart(self, jurisdiction):
        avaliable_types = jurisdiction.adapter().avaliable_types

        title = ", ".join(avaliable_types) + " volumes ({0})".format(
            jurisdiction.geo_label()
        )

        special_labels = ["{type}_ALL".format(type=x.upper()) for x in avaliable_types]

        query = Value.objects.filter(
            authority__jurisdiction=jurisdiction,
            authority__is_overall=True,
            property__special__in=special_labels,
        )

        query = query.exclude(year__number=9999)

        chart = AltairChart(name=title, title=title, chart_type="line")

        chart.data_source = "Data source: " + jurisdiction.data_source()
        chart.header = {
            "property__name": "Request type",
            "year__number": "Year",
            "value": "Information requests",
        }

        df = chart.apply_query(query)

        year_totals = df.groupby(["Year"]).sum().to_dict()["Information requests"]

        def func(r):
            return r["Information requests"] / year_totals[r["Year"]]

        df["Percentage in year"] = df.apply(func, axis="columns")

        chart.set_options(
            x=alt.X("Year", title=""),
            y="Information requests",
            color=alt.Color("Request type", sort="-y"),
            tooltip=[
                "Request type",
                "Year",
                alt.Tooltip("Information requests", format=","),
                alt.Tooltip("Percentage in year", format=",.2%"),
            ],
        )

        years = df["Year"].unique()
        years.sort()

        chart.options["x"].axis = alt.Axis(format="d", values=years)

        chart.custom_settings = lambda x: x.configure_point(size=50)

        return chart


def zero_if_not(v):
    if v is None:
        return 0
    return v


class PropertyView(LocalView):
    template_name = "pi_monitor/property.html"
    share_title = "{{property.name}} Statistics"
    page_title = "{{property.name}} Statistics"
    share_description = "{{jurisdiction.name}} - Statistics for {{jurisdiction.name}}"

    def bake_args(self):
        for j in Jurisdiction.objects.all():
            for a in j.properties.all():
                for y in j.years.all():
                    yield (
                        j.slug,
                        a.slug,
                        y.slug,
                    )

    def logic(self):
        self.jurisdiction = Jurisdiction.objects.get(slug=self.jurisdiction_slug)

        self.property = Property.objects.get(
            jurisdiction=self.jurisdiction, slug=self.property_slug
        )
        self.years = self.jurisdiction.years.filter(
            values__property=self.property
        ).distinct()
        self.year = Year.objects.get(
            jurisdiction=self.jurisdiction, slug=self.year_slug
        )
        if self.year_slug == "alltime":
            self.time_chart = self.property_over_time(self.property)
            if self.property.child_of_id:
                self.time_chart_percent = self.property_over_time(
                    self.property, percentage=True
                )
        else:
            self.time_chart = self.property_over_time(self.property, year=self.year)
            if self.property.child_of_id:
                self.time_chart_percent = self.property_over_time(
                    self.property, percentage=True, year=self.year
                )
            # add new bar chart based on property and year

        self.sector_table = self.public_bodies_table(
            self.property, self.year, "Sector", self.jurisdiction.sectors()
        )

        self.authority_table = self.public_bodies_table(
            self.property, self.year, "Authority", self.jurisdiction.bodies()
        )

    def public_bodies_table(self, property, year, name, authority_query):
        table = Table(name="counts by " + property.name)

        value_query = Value.objects.filter(
            year=year, property=property, authority__in=authority_query
        )

        value_query = value_query.order_by("-value")

        render_full = self.jurisdiction.authorities.filter(
            render_full=True
        ).values_list("slug", flat=True)

        def authority_link(authority):
            authority_url = reverse(
                "pi.body",
                args=(self.year.jurisdiction.slug, authority.slug, self.year.slug),
            )
            return get_link(authority.name, authority_url)

        def get_linked_value(row):
            body_slug = row[name]
            value = intcomma(int(row["Count"]))
            if body_slug not in render_full:
                return value
            else:
                url = reverse(
                    "pi.bodystat",
                    args=(self.jurisdiction.slug, body_slug, self.property.slug),
                )
                return get_link(value, url)

        auth_links = {
            x.slug: authority_link(x) for x in self.jurisdiction.authorities.all()
        }

        table.header["authority__slug"] = name
        if name == "Authority":
            table.header["authority__sector__slug"] = "Sector"
        table.header["value"] = "Count"
        if self.property.child_of:
            col_name = "Percentage of " + self.property.child_of.name
            table.header["percentage_value"] = col_name
            table.format[col_name] = fix_percentage

        table.format[name] = auth_links.get
        table.format["Sector"] = auth_links.get

        table.format_on_row["Count"] = get_linked_value

        table.apply_query(value_query)
        return table

    def property_over_time(self, item_property, percentage=False, year=None):
        """
        table to show counts or percentages over time

        if year is set, do bar charts.
        If not set - do a comparative line chart of all years.

        """

        title = item_property.name
        y_lab = "Requests by sector"
        if percentage:
            y_lab = f"As % of {item_property.child_of.name.lower()}"

        if year:
            chart_type = "bar"
        else:
            chart_type = "line"
        chart = AltairChart(name=title, title=title, chart_type=chart_type)

        safe_name = conditional_escape(item_property.name)

        chart.header["year__number"] = "Year"
        if percentage:
            chart.header["percentage_value"] = safe_name
            property_tooltip = alt.Tooltip(safe_name, format="%")
            agg_func = "mean"
            simple_color = theme.all_colours["colour_dark_blue"]
        else:
            chart.header["value"] = safe_name
            property_tooltip = alt.Tooltip(safe_name)
            agg_func = "sum"
            simple_color = theme.all_colours["colour_blue"]

        chart.header["authority__name"] = "Sector"

        sectors = Authority.objects.filter(
            Q(is_sector=True) | Q(is_overall=True),
            jurisdiction=self.jurisdiction,
        )

        year_values = Value.objects.filter(
            authority__in=sectors, property=item_property
        ).order_by("year__number")

        year_values = year_values.exclude(year__number=9999)

        if year:
            year_values = year_values.filter(year=year)

        df = chart.apply_query(year_values)

        # do bar charts by sector for each year.
        if year:
            yy = alt.Y("Sector", axis=alt.Axis(labelAngle=0), title=y_lab, sort="-x")
            xx = alt.X(safe_name, title="")
            chart.set_options(
                x=xx,
                y=yy,
                tooltip=["Sector", property_tooltip, "Year"],
                color=alt.value(simple_color),
            )
            if percentage:
                chart.options["x"].axis = alt.Axis(format=".0%")
                chart.options["x"].scale = alt.Scale(domain=(0, 1))
        else:
            # for overall chart, reduce to highest values
            df = group_to_other(
                df,
                safe_name,
                "Year",
                "Sector",
                cut_off=3,
                agg_func=agg_func,
                other_label="Other sectors",
            )
            chart.df = df
            years = df["Year"].unique()
            years.sort()
            x_axis = alt.Axis(format="d", values=years)
            chart.set_options(
                x=alt.X("Year", axis=x_axis),
                y=alt.Y(safe_name, title=y_lab),
                tooltip=["Sector", property_tooltip, "Year"],
                color="Sector",
            )
            if percentage:
                chart.options["y"].axis = alt.Axis(format=".0%")
                chart.options["y"].scale = alt.Scale(domain=(0, 1))

        chart.custom_settings = lambda x: x.configure_point(size=50)

        return chart


class YearView(LocalView):
    template_name = "pi_monitor/year.html"
    share_title = "{{jurisdiction.name}} Statistics - {{year.number}}"
    page_title = "{{jurisdiction.name}} Statistics - {{year.number}}"
    share_description = "Information request statistics"

    def bake_args(self):
        for j in Jurisdiction.objects.all():
            for y in j.years.all():
                yield (
                    j.slug,
                    y.slug,
                )

    def logic(self):
        self.jurisdiction = Jurisdiction.objects.get(slug=self.jurisdiction_slug)
        self.years = self.jurisdiction.years.all()
        self.year = self.years.get(slug=self.year_slug)
        self.jurisdiction.adapter()

        relevant_auths = Value.objects.filter(
            year=self.year,
            authority__is_overall=False,
            authority__is_sector=False,
            property__special="PI_ALL",
        )

        relevant_auths = relevant_auths.exclude(value=0)

        values = [x.value for x in relevant_auths]
        values.sort()

        self.average = sum(values) / relevant_auths.count()
        self.median = values[int(len(values) / 2)]
        self.max = values[-1]
        self.relevant_auths = relevant_auths.count()

        self.authority = Authority.objects.get(
            jurisdiction=self.jurisdiction, is_overall=True
        )
        self.authority.prepare_stats(self.year)
        self.stats = self.authority.stats
        self.sectors = self.jurisdiction.sectors()
        self.sector_chart = self.sector_distribution(self.year)
        self.sector_table = self.public_bodies_table(self.year, "Sector", self.sectors)
        self.bodies_table = self.public_bodies_table(
            self.year, "Public Bodies", self.jurisdiction.bodies()
        )

    def public_bodies_table(self, year, name, body_query):
        """
        requests and successs made to public bodies ('body_query')
        in 'year'
        name expects either 'Public Bodies' or 'Sectors'
        """

        # function to adapt link
        def authority_link(authority):
            """
            generate an authority link
            """
            j_slug = self.year.jurisdiction.slug
            year_slug = self.year.slug
            authority_url = reverse("pi.body", args=(j_slug, authority.slug, year_slug))
            return get_link(authority.name, authority_url)

        valid_auths = self.jurisdiction.authorities.all()
        auth_links = {x.slug: authority_link(x) for x in valid_auths}

        title = "FOI counts for " + year.display + " " + name
        table = Table(name=title)

        # What are the public information types
        pts = self.jurisdiction.adapter().public_types
        public_types = ["{type}_ALL".format(type=x.upper()) for x in pts]
        public_types_full = ["{type}_FULL".format(type=x.upper()) for x in pts]

        needed_values = ["PI_ALL"] + public_types + ["PI_FULL"] + public_types_full

        # map special values to local values
        properties = Property.objects.filter(
            jurisdiction=self.jurisdiction, special__in=needed_values
        )
        properties = {x.special: x.name for x in properties}

        # create basic table of authorities and sectors
        table.header["slug"] = name
        if name == "Public Bodies":
            table.header["sector__slug"] = "Sector"
        df = table.apply_query(body_query)

        # get values and convert to pivot_table
        values = Value.objects.filter(
            property__special__in=needed_values, year=year, authority__in=body_query
        )
        values = query_to_df(
            values,
            {
                "property__name": "property",
                "authority__slug": "authority",
                "value": "value",
            },
        )
        pivot = pd.pivot_table(
            values, values="value", index="authority", columns=["property"]
        )

        # reorder columns to correct order
        pivot = pivot[[properties[x] for x in needed_values]]
        # join with authority and sector slugs
        df = df.set_index(name)
        df = df.join(pivot)
        df.reset_index(inplace=True)

        # sort by total public information requests
        df = df.sort_values(properties["PI_ALL"], ascending=False)

        table.format[name] = auth_links.get
        table.format["Sector"] = auth_links.get
        for n in needed_values:
            full = properties[n]
            if "ALL" in n:
                table.format[full] = lambda x: intcomma(int(x))
            else:
                # convert to percentage against all for that type
                all_slug = n.split("_")[0] + "_ALL"
                all_full = properties[all_slug]
                all_requests = df[all_full]
                df[full] = df[full] / all_requests
                table.format[full] = fix_percentage

        # replace infinities and drop NAs
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(0)
        table.df = df
        return table

    def sector_distribution(self, year):
        title = "Public information requests by sector"
        chart = AltairChart(name=title, title=title, chart_type="bar")

        sectors = year.jurisdiction.sectors()

        chart.header["authority__name"] = "Sector"
        chart.header["value"] = "Public information requests"

        year_values = Value.objects.filter(
            year=year, authority__in=sectors, property__special="PI_ALL"
        )
        df = chart.apply_query(year_values)
        pir = df["Public information requests"]
        df["Percentage"] = pir / pir.sum()

        chart.set_options(
            x="Public information requests",
            y=alt.Y("Sector", sort="-x"),
            tooltip=[
                "Sector",
                alt.Tooltip("Public information requests", format=","),
                alt.Tooltip("Percentage", format=",.2%"),
            ],
        )

        chart.set_text_options(
            text=alt.Text("Public information requests", format=".2s"),
            align="left",
            baseline="middle",
            dx=3,
        )

        chart.custom_settings = lambda x: x.configure_point(size=50)

        return chart


class BodyStatisticView(LocalView):
    """
    change over time and index comparisions for a specific
    body on a specific statistic
    """

    template_name = "pi_monitor/bodystat.html"
    share_title = "{{authority.name}} -- {{property.name}}"
    page_title = "{{authority.name}} -- {{property.name}}"
    share_description = "{{jurisdiction.name}} - Information request statistics"

    def _get_bake_path(self, *args):
        args = args[:-1]  # remove the helper vars
        return super()._get_bake_path(*args)

    def bake_args(self, options=None):
        for j in Jurisdiction.objects.all():
            for a in j.authorities.filter(render_full=True):
                print("fetching {0}".format(a.slug))
                bake_df = self.get_dataframe(a)
                for p in j.properties.all():
                    bake_variables = {
                        "jurisdiction": j,
                        "authority": a,
                        "property": p,
                        "bake_df": bake_df,
                    }

                    yield (j.slug, a.slug, p.slug, bake_variables)

    def load_from_bake(self):
        if self.bake_variables:
            for k, v in self.bake_variables.items():
                setattr(self, k, v)

    def get_dataframe(self, authority, property=None):
        sectors = [authority.id]
        if authority.sector_id:
            sectors.append(authority.sector_id)

        year_values = Value.objects.filter(
            Q(authority_id__in=sectors) | Q(authority__is_overall=True)
        ).order_by("year__number")
        if property:
            year_values = year_values.filter(property=property)
        year_values = year_values.exclude(year__number=9999).prefetch_related(
            "year", "authority"
        )

        header = {
            "year__number": "Year",
            "percentage_value": "percentage_value",
            "value": "value",
            "authority__name": "Authority",
            "property_id": "property_id",
        }

        main_df = query_to_df(year_values, header)

        return main_df

    def logic(self):
        # Get bake_variables from kwargs if provided
        self.bake_variables = getattr(self, 'bake_variables', {})
        
        if not self.bake_variables:
            self.jurisdiction = Jurisdiction.objects.get(slug=self.jurisdiction_slug)
            self.authority = Authority.objects.get(
                slug=self.body_slug, jurisdiction=self.jurisdiction
            )
            self.property = Property.objects.filter(
                slug=self.property_slug, jurisdiction=self.jurisdiction
            ).select_related("child_of")
            self.property = self.property[0]
            main_df = self.get_dataframe(self.authority, self.property)
        else:
            self.load_from_bake()
            bake_df = self.bake_df
            main_df = bake_df[bake_df["property_id"] == self.property.id]

        # get query to power charts

        self.time_chart = self.property_over_time(self.property, main_df)
        self.time_chart_indexed = self.property_over_time(
            self.property, main_df, reindex_on_earliest=True
        )
        if self.property.child_of_id:
            self.time_chart_percent = self.property_over_time(
                self.property, main_df, percentage=True
            )
            self.time_chart_percent_indexed = self.property_over_time(
                self.property, main_df, percentage=True, reindex_on_earliest=True
            )
        self.year_table = self.get_table(main_df)

    def get_table(self, main_df):
        """
        table of property over time
        """

        title = "Over time - {body} - {prop}".format(
            body=self.authority.name, prop=self.property.name
        )
        table = Table(name=title)

        df = main_df[main_df["Authority"] == self.authority.name]

        df = df.drop(columns=["Authority", "property_id"])

        df = df.reindex(columns=["Year", "value", "percentage_value"])

        df = df.rename(columns={"value": "Value"})

        if self.property.child_of_id:
            df = df.rename(
                columns={"percentage_value": "% of " + self.property.child_of.name}
            )
        else:
            df = df.drop(columns=["percentage_value"])

        table.df = df

        def format_year(year):
            url = reverse(
                "pi.body",
                args=(self.jurisdiction.slug, self.authority.slug, str(int(year))),
            )
            return get_link(int(year), url)

        table.format["Year"] = format_year
        table.format["Value"] = lambda x: intcomma(int(x))
        if self.property.child_of:
            table.format["% of " + self.property.child_of.name] = fix_percentage

        return table

    def property_over_time(
        self, item_property, main_df, percentage=False, reindex_on_earliest=False
    ):
        """
        table to show counts or percentages over time
        """

        safe_name = conditional_escape(item_property.name)

        safe_name = safe_name + " chart over time"
        if percentage:
            safe_name += " percentage"
        if reindex_on_earliest:
            safe_name += " reindexed"

        title = "Change over time"

        chart = AltairChart(name=safe_name, title=title, chart_type="line")

        df = main_df.copy()

        if percentage:
            df[safe_name] = df["percentage_value"]
        else:
            df[safe_name] = df["value"]

        chart.df = df

        years = df["Year"].unique()
        years.sort()

        # make correct subtitle/label for this chart
        if percentage:
            y_lab = f"As % of {item_property.child_of.name}"
            if reindex_on_earliest:
                y_lab = f"As % of {item_property.child_of.name} ({years[0]} indexed)"
        else:
            y_lab = f"Requests: {item_property.name.lower()}"
            if reindex_on_earliest:
                y_lab = f"Requests: {item_property.name.lower()} ({years[0]} indexed)"

        ev = df.loc[df["Year"] == years[0], ["Authority", safe_name]]
        ev = ev.rename(columns={safe_name: "Earliest Value"})
        df = df.merge(ev)

        if reindex_on_earliest:
            if len(df["Authority"].unique()) == 1:
                # mostly nonsense to index against self
                return None
            if df[safe_name].min() == 0:
                # similarly doesn't work if reindexing off 0
                return None

            df[safe_name] = (df[safe_name] / df["Earliest Value"]) * 100
            setting_min = df[safe_name].min()
            setting_max = df[safe_name].max()

        df["line_label"] = df["Authority"]
        df.loc[df["Year"] != df["Year"].min(), "line_label"] = ""

        chart.df = df

        chart.set_options(
            x="Year",
            y=alt.Y(safe_name, title=y_lab),
            tooltip=[safe_name, "Year"],
            color="Authority",
        )

        jurisdiction = item_property.jurisdiction.data_source()
        chart.data_source = "Data source: {0}".format(jurisdiction)

        # too fiddly to get working automatically at the moment
        # chart.set_text_options(text="line_label", dx=-10, baseline="middle", align="right")

        chart.options["x"].axis = alt.Axis(format="d", values=years)
        if percentage and not reindex_on_earliest:
            chart.options["y"].axis = alt.Axis(format=".0%")
            chart.options["y"].scale = alt.Scale(domain=(0, 1))
        if reindex_on_earliest:
            if setting_min != np.inf and setting_max != np.inf:
                chart.options["y"].scale = alt.Scale(domain=(setting_min, setting_max))

        chart.custom_settings = lambda x: x.configure_point(size=50)

        return chart


class BodyView(LocalView):
    template_name = "pi_monitor/body.html"
    share_title = "Statistics - {{authority.name}}"
    page_title = "Statistics - {{authority.name}}"
    share_description = "{{jurisdiction.name}} - Information request statistics"

    def bake_args(self):
        for j in Jurisdiction.objects.all():
            for a in j.authorities.all():
                for y in a.valid_years():
                    yield (
                        j.slug,
                        a.slug,
                        y.slug,
                    )

    def logic(self):
        self.jurisdiction = Jurisdiction.objects.get(slug=self.jurisdiction_slug)
        self.authority = Authority.objects.get(
            slug=self.body_slug, jurisdiction=self.jurisdiction
        )
        self.years = self.authority.valid_years()
        self.year = self.years.get(slug=self.year_slug)
        self.chart = self.resolve_chart(self.authority)
        self.stats_tree = self.authority.prepare_stats_as_tree(self.year)
        for s in self.stats_tree:
            self.chart_collection.register(s.table)

    def resolve_chart(self, authority):
        """
        line chart of how much was answered in full for different types
        """

        title = "{0}: requests received and resolved".format(authority.name)

        titlep = "Requests received and resolved"
        y_lab = authority.name

        chart = AltairChart(name=title, title=titlep, chart_type="line")

        properties = ["PI_ALL", "PI_FULL"]

        year_values = Value.objects.filter(
            authority=authority, property__special__in=properties
        )
        year_values = year_values.exclude(year__number=9999)

        chart.header["year__number"] = "Year"
        chart.header["property__name"] = "Series"
        chart.header["value"] = "Requests"
        chart.header["percentage_value"] = "% of Total"
        chart.apply_query(year_values)

        legend_options = alt.Legend(orient="bottom", labelLimit=300)

        chart.set_options(
            y=alt.Y("Requests", title=y_lab),
            x="Year",
            tooltip=[
                "Series",
                "Year",
                alt.Tooltip("Requests", format=","),
                alt.Tooltip("% of Total", format=",.2%"),
            ],
            color=alt.Color("Series", legend=legend_options),
        )

        years = chart.df["Year"].unique()
        years.sort()

        chart.options["x"].axis = alt.Axis(format="d", values=years)

        return chart
