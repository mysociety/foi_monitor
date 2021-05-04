import importlib
import os
from collections import OrderedDict
from itertools import groupby

import numpy as np
import pandas as pd
from research_common.charts import Table, query_to_df
from django.conf import settings
from django.db import models
from django.db.models import Count, Max, Min, Sum
from django.urls import reverse
from django.utils.html import conditional_escape, escape
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django_sourdough.models import FlexiBulkModel
from numpy import histogram

from .adapters import AdapterRegistry

for a in settings.PI_ADAPTERS:
    importlib.import_module(a)


def fix_percentage(v): return round(v * 100, 2)


def intcomma(x): return "{:,}".format(x)


def get_link(
    x, y): return '<a href="{1}">{0}</a>'.format(conditional_escape(x), y)


def zero_if_none(v):
    """
    return 0 if none
    """
    if v:
        if pd.isnull(v):
            return 0
        if v == "-":
            return 0
        if v == "--":
            return 0
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return 0
            # if "," in v:
            #    v = v.replace(",", "")
            return int(v)
        if isinstance(v, int):
            return v
        if isinstance(v, float):
            return int(v)
        else:
            return 0
    else:
        return 0


class Jurisdiction(FlexiBulkModel):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    desc = models.CharField(max_length=255, default="")

    def get_special(self, special):
        prop = self.properties.get(special)
        return prop

    @classmethod
    def populate(cls):
        cls.objects.all().delete()
        for slug, adapter in AdapterRegistry.registry.items():
            new = cls(name=adapter.name,
                      slug=adapter.slug,
                      desc=adapter.desc)
            new.save()
            new.populate_jurisdiction()

    @property
    def resources_folder(self):
        return os.path.join(os.getcwd(), "resources", self.slug)

    def adapter(self):
        adapter_class = AdapterRegistry.get(self.slug)
        return adapter_class(self.resources_folder)

    def data_source(self):
        """
        label for when charts are copied
        """
        return self.adapter().data_source

    def geo_label(self):
        """
        label for when charts are copied
        """
        return self.adapter().geo_label

    def year_range(self):
        adapter = self.adapter()
        return range(adapter.start_year, adapter.end_year+1)

    def populate_jurisdiction(self):
        self.populate_properties()
        self.populate_authorities()
        self.populate_years()

    def populate_years(self):
        Year.objects.filter(jurisdiction=self).delete()
        for y in self.year_range():
            Year(jurisdiction=self,
                 number=y,
                 display=str(y),
                 slug=str(y)).queue()
        Year(jurisdiction=self,
             number="9999",
             display="All time",
             slug="alltime").queue()
        Year.save_queue()
        for y in self.years.all():
            y.load_year()

    def populate_properties(self):

        adapter = self.adapter()
        df = adapter.get_properties()

        self.properties.all().delete()

        name_to_id = df.quick.to_map("value", "id")

        local_to_global = {}
        children_ids = []
        has_children = []
        to_create = []

        existing = Property.objects.all().order_by('-id')

        if existing.exists():
            latest_id = existing[0].id
        else:
            latest_id = 0

        df = df.replace({np.nan: None})
        for index, r in df.iterrows():
            latest_id += 1
            c = Property(id=latest_id,
                         local_id=int(r["id"]),
                         name=r["value"].strip(),
                         slug=d_slugify(r["value"].strip()),
                         description=r["description"],
                         dynamic=r["combo_of"],
                         special=r["special"],
                         jurisdiction=self
                         )

            local_to_global[int(r["id"])] = latest_id
            if pd.notnull(r["child_of"]):
                local_id = name_to_id[r["child_of"]]
                global_id = local_to_global[local_id]
                c.child_of_id = global_id
                children_ids.append(c.child_of_id)

            to_create.append(c)

        has_children = [x for x in to_create if x.id in children_ids]
        to_create = [x for x in to_create if x.id not in children_ids]

        Property.objects.bulk_create(has_children)
        Property.objects.bulk_create(to_create)

    def sectors(self):
        return self.authorities.filter(is_sector=True).order_by('name')

    def bodies(self):
        return self.authorities.filter(is_sector=False,
                                       is_overall=False).order_by('name')

    def ordered_bodies(self):
        return self.authorities.filter(is_sector=False,
                                       is_overall=False).order_by('sector__name', 'name')

    def populate_authorities(self):
        adapter = self.adapter()
        df = adapter.get_authorities()

        self.authorities.all().delete()

        all_auths = Authority(jurisdiction=self,
                              name="All Authorities",
                              slug=slugify("All Authorities"),
                              is_overall=True
                              )

        all_auths.save()

        def num_to_boolean(v):
            if v:
                return True
            return False

        for index, r in df.iterrows():
            if pd.isnull(r["sector"]):
                Authority(jurisdiction=self,
                          name=r[adapter.authority_name_column],
                          slug=slugify(r[adapter.authority_name_column]),
                          local_id=r["authority_id"],
                          sector=all_auths,
                          is_sector=True,
                          render_full=num_to_boolean(r["render_full"])).queue()

        sectors = Authority.save_queue()
        sectors = {x.name: x.id for x in sectors}

        for index, r in df.iterrows():
            if pd.notnull(r["sector"]):
                Authority(jurisdiction=self,
                          name=r[adapter.authority_name_column],
                          slug=slugify(r[adapter.authority_name_column]),
                          local_id=r["authority_id"],
                          sector_id=sectors[r["sector"]],
                          is_sector=False,
                          render_full=num_to_boolean(r["render_full"])).queue()
        Authority.save_queue()


class Year(FlexiBulkModel):
    """
    Stores a set of annual statistics for an FOI jurisdiction
    """
    jurisdiction = models.ForeignKey(
        Jurisdiction, related_name="years", on_delete=models.CASCADE)
    number = models.IntegerField(default=0)
    display = models.CharField(max_length=20)
    slug = models.CharField(max_length=20, default="")
    file_name = models.CharField(max_length=20)

    def load_year(self):
        """
        load all values in for the year
        """

        adapter = self.jurisdiction.adapter()

        authorities = self.jurisdiction.authorities.all()
        authority_lookup = {x.name: x.id for x in authorities}

        df = adapter.get_year(self.number, authority_lookup)

        self.values.all().delete()

        normal_properties = self.jurisdiction.properties.filter(dynamic=None)
        combo_properties = self.jurisdiction.properties.exclude(dynamic=None)

        # load the ordinary values where it's just a number
        for index, r in df.iterrows():
            # don't load blank rows
            if pd.isnull(r[adapter.overall_total_column]):
                continue
            authority_name = r[adapter.authority_name_column]
            authority_id = authority_lookup.get(authority_name, None)
            if authority_id:  # skip those that only appeared once with no values
                for n in normal_properties:
                    v = zero_if_none(r[n.name])
                    if v == '':
                        v = 0
                    # if n.special:
                    #    print (n.special,r[n.name], v)
                    Value(authority_id=authority_id,
                          property=n,
                          year=self,
                          value=v
                          ).queue()

        # generate sectors totals for sector counts and overall
        print("generating sector values")
        sectors = list(self.jurisdiction.authorities.filter(is_sector=True))
        all_time = self.jurisdiction.authorities.get(is_overall=True)

        sector_lookup = {x.name: x.sector.name for x in self.jurisdiction.bodies(
        ).prefetch_related('sector')}

        df["sector"] = df[adapter.authority_name_column].map(sector_lookup)
        for s in sectors + [all_time]:
            if s.is_overall:
                reduced = df
            else:
                reduced = df[df["sector"] == s.name]
            for n in normal_properties:
                v = pd.to_numeric(reduced[n.name], errors='coerce').sum()
                if s.is_overall:
                    print(n.name, v)
                Value(
                    authority_id=s.id,
                    property=n,
                    year=self,
                    value=v
                ).queue()

        ordinary_values = Value.save_queue(safe_creation_rate=10000)

        print("calculating dynamic values")
        # calculate the dynamic values made from combinations of others
        def authority_key(x): return x.authority_id
        ordinary_values.sort(key=authority_key)
        for authority_id, values in groupby(ordinary_values,
                                            key=authority_key):
            value_lookup = {x.property_id: int(x.value) for x in values}
            for c in combo_properties:
                v = c.generate_value(value_lookup)
                v.authority_id = authority_id
                v.year = self
                v.queue()

        Value.save_queue()

        # calculate percentage values for children
        properties = list(self.jurisdiction.properties.all())
        to_update = []
        all_values = list(Value.objects.filter(
            year=self).order_by('authority'))
        for authority_id, values in groupby(all_values, key=authority_key):

            values = list(values)
            value_lookup = {x.property_id: x for x in values}
            for p in properties:
                if p.child_of_id:
                    base = value_lookup[p.id]
                    parent = value_lookup[p.child_of_id]
                    if parent.value:
                        base.percentage_value = base.value / parent.value
                    else:
                        base.percentage_value = 0
                    to_update.append(base)

        Value.objects.bulk_update(to_update, ['percentage_value'])


class Authority(FlexiBulkModel):
    jurisdiction = models.ForeignKey(
        Jurisdiction, related_name="authorities", on_delete=models.CASCADE)
    local_id = models.IntegerField(default=0)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    sector = models.ForeignKey("self", related_name="children",
                               null=True, blank=True,
                               on_delete=models.CASCADE)
    is_sector = models.BooleanField(default=False)
    is_overall = models.BooleanField(default=False)
    render_full = models.BooleanField(default=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stats = None

    def valid_years(self):
        return self.jurisdiction.years.filter(values__authority=self).distinct()

    def get_stats(self, year):
        """
        get all stats for this authority and year
        """
        v = Value.objects.filter(year=year, authority=self)
        v = v.order_by('property_id').prefetch_related('property')
        return v

    def prepare_stats(self, year):
        stat_items = self.get_stats(year)
        stats = {x.property.slug: x for x in stat_items}
        stats = {x.property.special: x for x in stat_items}
        self.stats = stats
        return stats

    def prepare_stats_as_tree(self, year):
        """
        Structure so there's easy comparison of percentage value
        """
        j = self.jurisdiction

        lp = list(j.properties.all().order_by('local_id'))
        child_props = list(set([x.child_of_id for x in lp if x.child_of_id]))
        props_with_children = [x for x in lp if x.id in child_props]
        slug_to_prop = {x.slug: x for x in lp}

        def get_property_link(property_slug):
            prop = slug_to_prop[property_slug]
            url = reverse('pi.property', args=(prop.jurisdiction.slug,
                                               prop.slug, year.slug))
            return get_link(escape(prop.name), url)

        def get_linked_value(row):
            property_slug = row["Property"]

            value = intcomma(int(row["Value"]))
            if not self.render_full:
                return value
            prop = slug_to_prop[property_slug]
            url = reverse('pi.bodystat', args=(prop.jurisdiction.slug, self.slug,
                                               prop.slug))
            return get_link(value, url)

        # authority stats

        sectors = [self.id]
        if self.sector_id:
            sectors.append(self.sector_id)

        stats = Value.objects.filter(year=year, authority__in=sectors)
        stats = stats.order_by('-value')
        stats = stats.prefetch_related(
            'authority', "property")

        header = {
            "authority_id": "authority_id",
            "property__slug": "Property",
            "property__child_of_id": "parent_group",
            "value": "Value",
            "percentage_value": "%"
        }

        main_df = query_to_df(stats, header)

        df = main_df[main_df["authority_id"] == self.id]
        df = df.drop(columns=["authority_id"])

        # parent_stats

        if self.sector_id:
            if self.sector.is_overall:
                sector_label = "Overall %"
            else:
                sector_label = "Sector %"

            parent_df = main_df[main_df["authority_id"] == self.sector_id]
            parent_df = parent_df.drop(
                columns=["authority_id", "Value", "parent_group"])
            parent_df = parent_df.rename(columns={"%": sector_label})

            df = df.merge(parent_df, on=["Property"])

        for p in props_with_children:
            reduced_df = df[(df["Property"] == p.slug) |
                            (df["parent_group"] == p.id)]
            reduced_df = reduced_df.drop('parent_group', axis='columns')
            reduced_df.loc[df["Property"] == p.slug, '%'] = 1
            if self.sector:
                reduced_df.loc[df["Property"] == p.slug, sector_label] = 1
            title = ""
            p.table = Table(name=title)
            p.table.df = reduced_df

            p.table.format["Property"] = get_property_link
            p.table.format_on_row["Value"] = get_linked_value
            p.table.format["%"] = fix_percentage
            if self.sector:
                p.table.format[sector_label] = fix_percentage

        return props_with_children


def d_slugify(v):
    return slugify(v).replace("-", "_")


class Property(FlexiBulkModel):
    jurisdiction = models.ForeignKey(
        Jurisdiction, related_name="properties", on_delete=models.CASCADE)
    local_id = models.IntegerField(default=0)
    name = models.CharField(max_length=255, null=True, blank=True)
    slug = models.CharField(max_length=255, null=True, blank=True, default="")
    description = models.CharField(max_length=255, null=True, blank=True)
    child_of = models.ForeignKey("self", related_name="children",
                                 on_delete=models.CASCADE,
                                 null=True, blank=True)
    dynamic = models.CharField(max_length=255, null=True, blank=True)
    special = models.CharField(max_length=255, null=True, blank=True)
    priority = models.IntegerField(default=0)

    def generate_value(self, value_lookup: dict):
        v = 0
        if self.dynamic == "*children*":
            child_ids = self.children.all().values_list('id', flat=True)
            for c in child_ids:
                v += value_lookup.get(c, 0)
        return Value(property=self, value=v)


class Value(FlexiBulkModel):
    authority = models.ForeignKey(Authority, related_name="values",
                                  on_delete=models.CASCADE)
    property = models.ForeignKey(Property, related_name="values",
                                 on_delete=models.CASCADE)
    year = models.ForeignKey(Year, related_name="values",
                             on_delete=models.CASCADE)
    value = models.FloatField(default=0)
    percentage_value = models.FloatField(default=0)

    def display_percent(self):
        return round(self.percentage_value, 2) * 100

    def parent_value(self):
        """
        get equiv value for one higher up
        """
        if self.authority.sector_id:
            parent_authority = self.authority.sector_id
            v = Value.objects.get(property_id=self.property_id,
                                  year_id=self.year_id,
                                  authority_id=parent_authority)
            return v
