import numpy as np
import pandas as pd

from .base import AdapterRegistry, GenericAdapter, dataframe_to_map, load_file


def zero_if_none(v):
    """
    return 0 if none
    """
    if v:
        return int(v)
    else:
        return 0


# Mapping from newer XLSX column names (2022-23+) to canonical names
# used in column_lookup.csv and the rest of the codebase.
_NEW_TO_CANONICAL = {
    # Authority name column
    "Public Authority": "AuthorityName",
    "Authority": "AuthorityName",
    # FOISA columns
    "FOISA fees paid": "FOISA - fees paid",
    "FOISA failure to respond": "FOISA - faliure to respond",
    "FOISA refused cost": "FOISA refused - cost",
    "FOISA vexatious": "FOISA - vexatious",
    "FOISA repeated": "FOISA - repeated",
    "FOISA full release": "FOISA - full release",
    "FOISA none released": "FOISA - none released",
    "FOISA some released": "FOISA - some released",
    "FOISA none held": "FOISA - none held",
    "FOISA no confirm/deny": "FOISA - no confirm/deny",
    # EIR columns
    "EIR closed - unclear": "EIR closed - unclear",
    "EIR - fees notice": "EIRs fees notice",
    "EIR - fees paid": "EIRs - fees paid",
    "EIR - Response on time": "EIRs response on time",
    "EIR - response late": "EIRs response late",
    "EIR - failure to respond": "EIRs - failure to respond",
    "EIR - timescale extended": "EIR timescale extended",
    "EIR refused - cost": "EIRs refused - cost",
    "EIR - manifestly unreasonable": "EIRs - manifestly unreasonable",
    "EIR - full release": "EIRs - full release",
    "EIR - none released": "EIRs - none released",
    "EIR - some released": "EIRs - some released",
    "EIR - none held": "EIRs - none held",
    "EIR - no confirm/deny": "EIRs - no confirm/deny",
    # Review columns
    "FOISA reviews": "FOISA reviews",
    "FOISA reviews - late response": "FOISA review - late response",
    "FOISA reviews - failure to respond": "FOISA review - failure to respond",
    "FOISA reviews - wholly/partially upheld": "FOISA review - wholly/partially upheld",
    "FOISA review - decision reached": "FOISA review - decision reached",
    "EIR reviews": "EIRs reviews",
    "EIR review - on time": "EIRs review - on time",
    "EIR review - late response": "EIRs review - late response",
    "EIR review - failure to respond": "EIRs review - failure to respond",
    # FOI exemption columns (2023-24+, strip "FOI: " prefix)
    "FOI: Otherwise accessible": "Otherwise accessible",
    "FOI: Publication scheme": "Publication Scheme",
    "FOI: Disclosure prohibited: enactment": "Disclosure prohibited: enactment",
    "FOI: Disclosure prohibited: EU obligation": "Disclosure prohibited: EU obligation",
    "FOI: Disclosure prohibited: contempt of court": "Disclosure prohibited: Contempt of Court",
    "FOI: Future publication: 12 weeks": "Future publication: 12 weeks",
    "FOI: Future publication: programme of research": "Future publication: programme of research",
    "FOI: Substantial prejudice to UK relations": "Substantial prejudice to UK relations",
    "FOI: Formulation/development of government policy": "Formulation/development of government policy",
    "FOI: Ministerial communications": "Ministerial communications",
    "FOI: Advice by Law Officers": "Advice by Law Officers",
    "FOI: Operation of Ministerial private office": "Operation of Ministerial private office",
    "FOI: Substantial prejudice to collective responsibility of Scottish Ministers": "Substantial prejudice to collective responsibility of Scottish Ministers",
    "FOI: Substantial inhibition to free and frank provision of advice": "Substantial inhibition to free and frank provision of advice",
    "FOI: Substantial inhibition to free and frank exchange of views": "Substantial inhibition to free and frank exchange of views",
    "FOI: Substantial prejudice to effective conduct of public affairs": "Substantial prejudice to effective conduct of public affairs",
    "FOI: National security": "National security",
    "FOI: Substantial prejudice to defence": "Substantial prejudice to defence",
    "FOI: Substantial prejudice to international relations": "Substantial prejudice to international relations",
    "FOI: Confidential information obtained from abroad": "Confidential information obtained from abroad",
    "FOI: Trade secret": "Trade secret",
    "FOI: Substantial prejudice to commercial interests": "Substantial prejudice to commercial interests",
    "FOI: Substantial prejudice to the economic interests of the UK": "Substantial prejudice to the economic interests of the UK",
    "FOI: Substantial prejudice to the financial interests of a UK administration": "Substantial prejudice to the financial interests of a UK administration",
    "FOI: Information held for the purposes of a criminal investigation": "Information held for the purposes of a criminal investigation",
    "FOI: Information held for ongoing Fatal Accident Inquiry": "Information held for ongoing Fatal Accident Inquiry",
    "FOI: Information held regarding cause of death": "Information held regarding cause of death",
    "FOI: Information relating to the obtaining of information from confidential sources": "Information relating to the obtaining of information from confidential sources",
    "FOI: Information held for purposes of civil proceedings arising out of investigations": "Information held for purposes of civil proceedings arising out of investigations",
    "FOI: Substantial prejudice to prevention or detection of crime": "Substantial prejudice to prevention or detection of crime",
    "FOI: Substantial prejudice to apprehension or prosecution of offenders": "Substantial prejudice to apprehension or prosecution of offenders",
    "FOI: Substantial prejudice to administration of justice": "Substantial prejudice to administration of justice",
    "FOI: Substantial prejudice to assessment or collection of tax or duty": "Substantial prejudice to assessment or collection of tax or duty",
    "FOI: Substantial prejudice to operation of immigration controls": "Substantial prejudice to operation of immigration controls",
    "FOI: Substantial prejudice to maintenance of security and good order in prisons": "Substantial prejudice to maintenance of security and good order in prisons",
    "FOI: Substantial prejudice to the exercise by a public authority for any of its functions": "Substantial prejudice to the exercise by a public authority for any of its functions",
    "FOI: Substantial prejudice to civil proceedings brought by an authority": "Substantial prejudice to civil proceedings brought by an authority",
    "FOI: Confidentiality of communications": "Confidentiality of communications",
    "FOI: Actionable breach of confidence": "Actionable breach of confidence",
    "FOI: Court records": "Court records",
    "FOI: Court records: inquiry or arbitration": "Court records: inquiry or arbitration",
    "FOI: Personal data of the applicant": "Personal data of the applicant - FOI",
    "FOI: Third party personal data": "Third party personal data - FOI",
    "FOI: Personal census information": "Personal census information",
    "FOI: Deceased person's health record": "Deceased person's health record",
    "FOI: Endangerment to health or safety": "Endangerment to health or safety",
    "FOI: Environmental information": "Environmental information",
    "FOI: Substantial prejudice to audit function": "Substantial prejudice to audit function",
    "FOI: Communications with the Royal Family and honours": "Communications with the Royal Family and honours",
    # EIR exception columns (2023-24+, strip "EIR: " prefix)
    "EIR: Material in the course of completion": "Material in course of completion",
    "EIR: Internal communications": "Internal Communications",
    "EIR: Substantial prejudice to international relations, public safety, etc.": "Substantial prejudice to international relations public safety etc.",
    "EIR: Substantial prejudice to course of justice": "Substantial prejudice to course of justice etc.",
    "EIR: Substantial prejudice to intellectual property rights": "Substantial prejudice to intellectual property rights",
    "EIR: Substantial prejudice to confidentiality of proceedings": "Substantial prejudice to confidentiality of proceedings",
    "EIR: Substantial prejudice to confidentiality of commercial industrial information": "Substantial prejudice to confidentiality of commercial or industrial information",
    "EIR: Substantial prejudice to the interests of a third party": "Substantial prejudice to the interests of a third party",
    "EIR: Substantial prejudice to the protection of the environment": "Substantial prejudice to the protection of the environment",
    "EIR: Neither confirm nor deny whether environmental information is held": "Neither confirm nor deny whether environmental information held",
    "EIR: Personal data of applicant": "Personal data of the applicant - EIR",
    "EIR: Third party personal data.": "Third party personal data - EIR",
    "EIR: Neither confirm nor deny whether personal data held": "Neither confirm or deny whether personal data held",
    # 2022-23 style (bare exemption names without FOI:/EIR: prefix, with case differences)
    "Publication scheme": "Publication Scheme",
    "Disclosure prohibited: contempt of court": "Disclosure prohibited: Contempt of Court",
    "Material in the course of completion": "Material in course of completion",
    "Internal communications": "Internal Communications",
    "Substantial prejudice to international relations, public safety, etc.": "Substantial prejudice to international relations public safety etc.",
    "Substantial prejudice to course of justice": "Substantial prejudice to course of justice etc.",
    "Substantial prejudice to confidentiality of commercial industrial information": "Substantial prejudice to confidentiality of commercial or industrial information",
    "Neither confirm nor deny whether environmental information is held": "Neither confirm nor deny whether environmental information held",
    "Neither confirm nor deny whether personal data held": "Neither confirm or deny whether personal data held",
    # EIR personal data - 2022-23 style (bare distinct names)
    "Personal data of applicant": "Personal data of the applicant - EIR",
    "Third party personal data.": "Third party personal data - EIR",
}


def _normalise_columns(df):
    """
    Normalise XLSX column names to match canonical column_lookup.csv names.
    Strips whitespace, normalises Unicode characters, then applies the rename
    mapping for newer-format columns. Also handles the duplicate
    'Personal data' / 'Third party' columns from older sheets that use
    .1 suffixes.
    """
    # Strip whitespace and replace curly apostrophes with straight ones
    df.columns = [c.strip().replace("\u2019", "'") for c in df.columns]

    # Apply the new→canonical mapping (safe for all eras - only matches what exists)
    rename = {k: v for k, v in _NEW_TO_CANONICAL.items() if k in df.columns}
    if rename:
        df = df.rename(columns=rename)

    # Handle duplicate column disambiguation for older-style sheets
    # (columns like "Personal data of the applicant" and "Personal data of the
    # applicant.1" need to become FOI/EIR variants)
    nh = []
    done_foi = False
    for h in df.columns:
        header = h.lower().strip().replace(".1", "")
        if header == "personal data of the applicant":
            if done_foi:
                nh.append("Personal data of the applicant - EIR")
            else:
                nh.append("Personal data of the applicant - FOI")
                done_foi = True
        else:
            nh.append(h)
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
            nh.append(h)
    df.columns = nh

    return df


@AdapterRegistry.register
class FoisaAdapter(GenericAdapter):
    """
    adapter to get FOISA style input
    """

    start_year = 2013
    end_year = 2024
    authority_name_column = "AuthorityName"
    name = "Scotland Information Request Statistics"
    desc = "Statistics of FOI, EIR and SAR for public authorities in Scotland (collected by OSIC)"
    slug = "foisa"
    public_types = ["FOI", "EIR"]
    private_types = ["SAR"]
    avaliable_types = public_types + private_types
    data_source = "OSIC FOI Statistics"
    geo_label = "Scotland"
    xlsx_filename = "FOIStatisticsAllYears.xlsx"

    def _sheet_name_for_year(self, year):
        """Map an integer year to the XLSX sheet name (financial year format)."""
        return f"{year}-{(year + 1) % 100:02d} Annual"

    def _read_sheet(self, year):
        """Read a single year's sheet from the XLSX, normalising columns."""
        import os

        path = os.path.join(self.resources_folder, self.xlsx_filename)
        sheet = self._sheet_name_for_year(year)
        df = pd.read_excel(path, sheet_name=sheet)
        df = _normalise_columns(df)

        # Ensure an AuthorityName column exists
        if "AuthorityName" not in df.columns:
            for col in ("Authority", "Public Authority"):
                if col in df.columns:
                    df = df.rename(columns={col: "AuthorityName"})
                    break

        return df

    def get_year(self, year: int, authority_lookup: dict):
        if year == 9999:
            # Aggregate across all years
            frames = []
            for y in range(self.start_year, self.end_year + 1):
                ydf = self._read_sheet(y)
                frames.append(ydf)
            df = pd.concat(frames, ignore_index=True)
            # Sum numeric columns per authority so each authority has one row
            df = df.drop(columns=["Region", "Sector"], errors="ignore")
            df = df.pivot_table(index=["AuthorityName"], aggfunc=np.sum)
            df = df.reset_index()
        else:
            df = self._read_sheet(year)

        fill_na = [
            "EIR requests",
            "EIRs - full release",
            "FOISA requests",
            "FOISA - full release",
        ]
        for n in fill_na:
            if n in df.columns:
                df[n] = df[n].fillna(0)

        df["Public Information Requests"] = df["FOISA requests"] + df["EIR requests"]
        df["Public Information Requests (comparison)"] = df[
            "Public Information Requests"
        ]

        df["Public Information Requests - full release"] = (
            df["FOISA - full release"] + df["EIRs - full release"]
        )

        # Inject authority_id by matching on name from authorities.csv
        auth_df = load_file(self.resources_folder, "authorities.csv")
        name_to_auth_id = dataframe_to_map(auth_df, "AuthorityName", "authority_id")
        df["authority_id"] = df["AuthorityName"].map(name_to_auth_id)

        # get mappings between WDTK and FOISA ids
        wdtk_id_lookup = auth_df

        id_lookup = {}
        for r in range(1, 12):
            col = "wdtk_id_{id}".format(id=r)
            if col not in wdtk_id_lookup.columns:
                continue
            reduced = wdtk_id_lookup[~wdtk_id_lookup[col].isnull()]
            new_ids = dataframe_to_map(reduced, col, "authority_id")
            id_lookup.update(new_ids)

        # merge in the wdtk counts
        wdtk_df = load_file(self.resources_folder, "wdtk_year_count.csv")

        # add all values up for year
        if year == 9999:
            wdtk_df = wdtk_df.pivot_table(
                index=["public_body_id"], values="count", aggfunc=np.sum
            )
            wdtk_df = wdtk_df.reset_index()
        else:
            wdtk_df = wdtk_df[wdtk_df["year"] == year]
            wdtk_df = wdtk_df.drop(columns="year")

        wdtk_df["authority_id"] = wdtk_df["public_body_id"].apply(id_lookup.get)
        wdtk_df = wdtk_df[~wdtk_df["authority_id"].isnull()]
        # fold together different wdtk ids covered by the same foisa id
        wdtk_df = wdtk_df.pivot_table(
            index=["authority_id"], values="count", aggfunc=np.sum
        )
        wdtk_df = wdtk_df.reset_index()
        wdtk_df = wdtk_df.rename(columns={"count": "WDTK FOI requests"})
        # merge in the new column
        df = pd.merge(
            df, wdtk_df, how="left", left_on=["authority_id"], right_on=["authority_id"]
        )

        # Ensure WDTK column exists even if no data was available for this year
        if "WDTK FOI requests" not in df.columns:
            df["WDTK FOI requests"] = 0

        return df
