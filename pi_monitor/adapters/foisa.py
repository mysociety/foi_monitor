
from .base import GenericAdapter, AdapterRegistry
import pandas as pd


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

    def get_year(self, year: int, authority_lookup: dict):
        if year == 9999:
            filename = "all time"
        else:
            filename = year

        df = pd.DataFrame.quick.load_file(self.resources_folder,
                                          "{year}.csv".format(year=filename))

        wdtk_df = pd.DataFrame.quick.load_file(self.resources_folder,
                                               "wdtk_{year}.csv".format(year=filename))

        # wdtk ids have already been mapped to FOISA ids
        wdtk = wdtk_df.quick.to_map("authority_id", "count", default=0)

        fill_na = ["EIR requests", "EIRs - full release",
                   "FOISA requests", "FOISA - full release"]
        for n in fill_na:
            df[n] = df[n].fillna(0)
        df["Public Information Requests"] = df["FOISA requests"] + df["EIR requests"]
        df["Public Information Requests (comparison)"] = df["Public Information Requests"]

        df["Public Information Requests - full release"] = df["FOISA - full release"] + \
            df["EIRs - full release"]

        df["WDTK FOI requests"] = df["authority_id"].map(wdtk)

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
