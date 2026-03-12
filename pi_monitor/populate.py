#!/usr/bin/env python
import os
import urllib.request

from pi_monitor.models import Jurisdiction

CABINET_OFFICE_CSV_URL = (
    "https://assets.publishing.service.gov.uk/media/"
    "68108ef4b0d43971b07f5c84/foi-statistics-annual-2024-published-data.csv"
)
CABINET_OFFICE_CSV_FILENAME = "foi-statistics-annual-2024-published-data.csv"

FOISA_XLSX_URL = (
    "https://www.foi.scot/sites/default/files/2025-07/FOIStatisticsAllYears.xlsx"
)
FOISA_XLSX_FILENAME = "FOIStatisticsAllYears.xlsx"


def _download_if_missing(folder, filename, url):
    """Download a file to the resources folder if it doesn't already exist."""
    path = os.path.join(folder, filename)
    if os.path.exists(path):
        print(f"Data file already present: {path}")
        return
    os.makedirs(folder, exist_ok=True)
    print(f"Downloading {filename} from {url} ...")
    urllib.request.urlretrieve(url, path)
    print(f"Saved to {path}")


def fetch_data_if_missing():
    """Fetch the latest data files for both jurisdictions if not already present."""
    resources = os.path.join(os.getcwd(), "resources")
    _download_if_missing(
        os.path.join(resources, "cabinetfoi"),
        CABINET_OFFICE_CSV_FILENAME,
        CABINET_OFFICE_CSV_URL,
    )
    _download_if_missing(
        os.path.join(resources, "foisa"),
        FOISA_XLSX_FILENAME,
        FOISA_XLSX_URL,
    )


def populate():
    print("running population")
    fetch_data_if_missing()
    Jurisdiction.populate()
