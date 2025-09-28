
import os
import markdown
import pandas as pd
from collections import defaultdict


@pd.api.extensions.register_dataframe_accessor("quick")
class QuickPandasDataFrame:
    """
    extention to store local helper functions
    """
    localEmpty = "localEmpty"

    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def load_file(*args, **kwargs):
        lower_case_columns = False
        if "lower_case_columns" in kwargs:
            lower_case_columns = kwargs["lower_case_columns"]
            del kwargs["lower_case_columns"]
        path = os.path.join(*args)
        print("Opening : {path}".format(path=path))
        ext = os.path.splitext(path)[1]
        if ext in [".xlsx", '.xls']:
            func = pd.read_excel
        if ext == ".csv":
            func = pd.read_csv
        df = func(path, **kwargs)
        if lower_case_columns:
            df.columns = [x.lower().strip() for x in df.columns]
        return df

    def to_map(self, col1name, col2name, default=localEmpty):
        if default != self.__class__.localEmpty:
            di = defaultdict(lambda: default)
        else:
            di = {}
        col1 = self._obj[col1name]
        col2 = self._obj[col2name]
        return pd.Series(col2.values, index=col1).to_dict(into=di)


class AdapterRegistry(object):
    registry = {}

    @classmethod
    def register(cls, new_adapter):
        """
        register an adapter for use by the app
        """
        cls.registry[new_adapter.slug] = new_adapter
        return new_adapter

    @classmethod
    def get(cls, slug):
        return cls.registry[slug]


class GenericAdapter(object):
    """
    Generic object to handle loading from FOI stats files
    Expects at least three files
    one that defines the column headings (or properties)
    one that defines the authority information
    and at least one that specifies the actual information
    (possibly seperated by year)
    """
    property_desc_file = "column_lookup.csv"
    authorites_desc_file = "authorities.csv"

    authority_name_column = "AuthorityName"
    overall_total_column = "Public Information Requests"
    slug = ""
    start_year = 0000
    end_year = 9999
    description_loc = "description.md"
    data_source = ""
    geo_label = ""

    def __init__(self, resources_folder):
        self.resources_folder = resources_folder
        self.data_source = self.__class__.data_source

    def get_description(self):
        """
        get markdown description
        """
        path = os.path.join(self.resources_folder, self.description_loc)
        with open(path, 'r') as f:
            htmlmarkdown = markdown.markdown(f.read())
        return htmlmarkdown

    def get_authorities(self):
        return pd.DataFrame.quick.load_file(self.resources_folder, self.authorites_desc_file)

    def get_properties(self):
        return pd.DataFrame.quick.load_file(self.resources_folder, self.property_desc_file)

    def get_year(self, year: int, authority_lookup: dict):
        """
        return a pandas DataFrame with information for authorities in the year.
        """
        print(year)
        print(authority_lookup)
        return None
