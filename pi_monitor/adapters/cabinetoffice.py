
from .base import GenericAdapter, AdapterRegistry
import numpy as np
import pandas as pd


def zero_if_none(v):
    """
    return 0 if none
    """
    if v:
        if v != "-":
            return int(v)
        else:
            return 0
    else:
        return 0


@AdapterRegistry.register
class CabinetAdapter(GenericAdapter):
    """
    adapter to get Cabinet Office style input
    """
    start_year = 2010
    end_year = 2019
    authority_name_column = "Government body"
    name = "Cabinet Office FOI"
    desc = "UK central government figures (collected and released by Cabinet Office)"
    filename = "foi-statistics-q4-2019-and-annual-published-data2.csv"
    slug = "cabinetfoi"
    public_types = ["FOI"]
    private_types = []
    avaliable_types = public_types + private_types
    data_source = "Cabinet Office FOI statistics"
    geo_label = "UK goverment"

    def get_year(self, year: int, authority_lookup: dict):

        df = pd.DataFrame.quick.load_file(self.resources_folder, self.filename)
        df = df.rename(
            columns={'Total "resolvable" requests': "Total resolvable requests"})

        # Drop all the 'Quarters'
        df["year"] = pd.to_numeric(df["Quarter"], errors="coerce")
        df = df.dropna(subset=["year"])

        # reduce to just the year if not all time
        if year != 9999:
            df = df[df["year"] == year]

        authorities = self.get_authorities()

        # allow multiple alt names to be stored in a row
        alt = authorities.copy()
        alt = alt.dropna(subset=["alt_name"])
        alt["alt_name"] = alt["alt_name"].apply(lambda x: x.split("|"))
        alt = alt.explode("alt_name")

        alt_name_lookup = alt.quick.to_map("alt_name", "Government body")
        sector_lookup = authorities.quick.to_map("Government body", "sector")
        id_lookup = authorities.quick.to_map("wdtk_id", "Government body")


        # replace alternate names with newer forms

        def default_self(x):
            return alt_name_lookup.get(x, x)

        #convert to floats
        for col in df.columns[2:]:
            df.loc[df[col] == "-", col] = 0
            df.loc[df[col] == " ", col] = 0
            df[col] = pd.to_numeric(df[col])

        df["Government body"] = df["Government body"].apply(default_self)
        df["Sector"] = df["Government body"].map(sector_lookup)

        # merge in the wdtk counts
        wdtk_df = pd.DataFrame.quick.load_file(
            self.resources_folder, "wdtk_year_count.csv")
        wdtk_df = wdtk_df.rename(columns={"count": "WhatDoTheyKnow requests"})
        wdtk_df["Government body"] = wdtk_df["public_body_id"].apply(
            id_lookup.get)
        df = pd.merge(df, wdtk_df, left_on=["year", "Government body"], right_on=[
                      "year", "Government body"])


        df["All requests"] = df["Total requests received"]
        df["Public Information Requests - Granted in full"] = df["Initial Outcome Granted in full"]
        df["Public Information Requests"] = df["Total requests received"]

        df["20-day deadline met"] = pd.to_numeric(
            df["20-day deadline met"], errors="coerce")
        df["Permitted extension to 20-day deadline"] = pd.to_numeric(
            df["Permitted extension to 20-day deadline"], errors="coerce")
        df["On time (including extentions)"] = df["20-day deadline met"] + \
            df["Permitted extension to 20-day deadline"]

        df["WhatDoTheyKnow requests (without Home Office)"] = df["WhatDoTheyKnow requests"]
        df.loc[df["Government body"] == "Home Office",
               ["WhatDoTheyKnow requests (without Home Office)"]] = 0

        if year == 9999:
            pt = df.pivot_table(index=["Government body"], aggfunc=np.sum)
            pt["Government body"] = pt.index
            pt["Sector"] = pt["Government body"].map(sector_lookup)
            df = pt

        return df
