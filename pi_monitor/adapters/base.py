
import os
import markdown
import pandas as pd
from collections import defaultdict


def load_file(*args, **kwargs):
    """
    Load a file (CSV or Excel) based on file extension
    """
    lower_case_columns = kwargs.pop("lower_case_columns", False)
    path = os.path.join(*args)
    print("Opening : {path}".format(path=path))
    ext = os.path.splitext(path)[1]
    if ext in [".xlsx", '.xls']:
        df = pd.read_excel(path, **kwargs)
    else:  # Default to CSV
        df = pd.read_csv(path, **kwargs)
    if lower_case_columns:
        df.columns = [x.lower().strip() for x in df.columns]
    return df


def dataframe_to_map(df, col1name, col2name, default=None):
    """
    Create a dictionary mapping from two columns of a DataFrame
    """
    if default is not None:
        di = defaultdict(lambda: default)
        mapping = pd.Series(df[col2name].values, index=df[col1name]).to_dict()
        di.update(mapping)
        return di
    else:
        return pd.Series(df[col2name].values, index=df[col1name]).to_dict()


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
        return load_file(self.resources_folder, self.authorites_desc_file)

    def get_properties(self):
        return load_file(self.resources_folder, self.property_desc_file)

    def get_year(self, year: int, authority_lookup: dict):
        """
        return a pandas DataFrame with information for authorities in the year.
        """
        print(year)
        print(authority_lookup)
        return None
