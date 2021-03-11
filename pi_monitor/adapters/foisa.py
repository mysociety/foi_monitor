
from .base import GenericAdapter, AdapterRegistry
import pandas as pd
import numpy as np

def zero_if_none(v):
    """
    return 0 if none
    """
    if v:
        return int(v)
    else:
        return 0


@AdapterRegistry.register
class FoisaAdapter(GenericAdapter):
    """
    adapter to get FOISA style input
    """
    start_year = 2013
    end_year = 2019
    authority_name_column = "AuthorityName"
    name = "Scotland Information Request Statistics"
    desc = "Statistics of FOI, EIR and SAR for public authorities in Scotland (collected by OSIC)"
    slug = "foisa"
    public_types = ["FOI", "EIR"]
    private_types = ["SAR"]
    avaliable_types = public_types + private_types
    data_source = "OSIC FOI Statistics"
    geo_label = "Scotland"

    def get_year(self, year: int, authority_lookup: dict):
        if year == 9999:
            filename = "all time"
        else:
            filename = year

        df = pd.DataFrame.quick.load_file(self.resources_folder,
                                          "{year}.csv".format(year=filename))

        fill_na = ["EIR requests", "EIRs - full release",
                   "FOISA requests", "FOISA - full release"]
        for n in fill_na:
            df[n] = df[n].fillna(0)
        df["Public Information Requests"] = df["FOISA requests"] + df["EIR requests"]
        df["Public Information Requests (comparison)"] = df["Public Information Requests"]

        df["Public Information Requests - full release"] = df["FOISA - full release"] + \
            df["EIRs - full release"]

        # get mappings between WDTK and FOISA ids

        wdtk_id_lookup = pd.DataFrame.quick.load_file(self.resources_folder,
                                                      "authorities.csv")

        id_lookup = {}
        for r in range(1, 12):
            col = "wdtk_id_{id}".format(id=r)
            reduced = wdtk_id_lookup[~wdtk_id_lookup[col].isnull()]
            new_ids = reduced.quick.to_map(col, "authority_id")
            id_lookup.update(new_ids)

        # merge in the wdtk counts
        wdtk_df = pd.DataFrame.quick.load_file(
            self.resources_folder, "wdtk_year_count.csv")
        
        # add all values up for year
        if year == 9999:
            wdtk_df = wdtk_df.pivot_table(
                index=["public_body_id"], values="count", aggfunc=np.sum)
            wdtk_df = wdtk_df.reset_index()
        else:
            wdtk_df = wdtk_df[wdtk_df["year"] == year]
            wdtk_df = wdtk_df.drop(columns="year")
        
        wdtk_df["authority_id"] = wdtk_df["public_body_id"].apply(
            id_lookup.get)
        wdtk_df = wdtk_df[~wdtk_df["authority_id"].isnull()]
        # fold together different wdtk ids covered by the same foisa id
        wdtk_df = wdtk_df.pivot_table(
            index=["authority_id"], values="count", aggfunc=np.sum)
        wdtk_df = wdtk_df.reset_index()
        wdtk_df = wdtk_df.rename(columns={"count": "WDTK FOI requests"})

        # merge in the new column
        df = pd.merge(df, wdtk_df, left_on=[
                      "authority_id"], right_on=["authority_id"])

        # two columns are named the same, this fixes that
        nh = []
        done_foi = False
        for h in df.columns:
            l = h.lower().strip().replace(".1", "")
            if l == "personal data of the applicant":
                if done_foi:
                    nh.append("Personal data of the applicant - EIR")
                else:
                    nh.append("Personal data of the applicant - FOI")
                    done_foi = True
            else:
                nh.append(h.strip())
        df.columns = nh

        done_foi = False
        nh = []
        for h in df.columns:
            if h.lower().strip() == "third party personal data":
                if done_foi:
                    nh.append("Third party personal data - EIR")
                else:
                    nh.append("Third party personal data - FOI")
                    done_foi = True
            else:
                nh.append(h.strip())
        df.columns = nh

        return df
