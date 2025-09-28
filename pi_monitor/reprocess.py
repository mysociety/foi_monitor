"""
reformat wdtk data to match scottish ids
"""

import pandas as pd
from collections import Counter
import os

resources_folder = r"C:\Users\alexj\Dropbox\mysociety\research_sites\resources\foisa"

def get_wdtk_to_scottish_id():
    path = os.path.join(resources_folder, "authorities.csv")
    df = pd.read_csv(path)
    
    lookup = {}
    
    for index, row in df.iterrows():
        osic = int(row["authority_id"])
        
        for x in range(1,12):
            col = "wdtk_id_{0}".format(x)
            if col in row and pd.notna(row[col]) and str(row[col]).strip():
                try:
                    lookup[int(row[col])] = osic
                except (ValueError, TypeError):
                    pass  # Skip invalid values
            
    return lookup

def create_wdtk_count(year=2013):
    path = os.path.join(resources_folder, "info_request.csv")
    df = pd.read_csv(path)
    lookup = get_wdtk_to_scottish_id()
    
    # Convert public_body_id to numeric, handling errors
    df["public_body_id"] = pd.to_numeric(df["public_body_id"], errors='coerce')
    
    df["foisa"] = df["public_body_id"].apply(lambda x: lookup.get(int(x), None) if pd.notna(x) else None)
    
    ids = []
    for index, row in df.iterrows():
        if year != 'alltime' and str(row["date_part"]) != str(year):
            continue
        if pd.notna(row["foisa"]):
            ids.append(row["foisa"])

    c = Counter(ids)
    
    # Create new DataFrame with results
    result_data = []
    for k, v in c.items():
        result_data.append([k, year, v])
    
    final = pd.DataFrame(result_data, columns=["authority_id", "year", "count"])
    
    output_path = os.path.join(resources_folder, "wdtk_{0}.csv".format(year))
    final.to_csv(output_path, index=False)

def create_counts():
    
    years = list(range(2013, 2020)) + ["alltime"] 
    for y in years:
        create_wdtk_count(y)
    
    
if __name__ == "__main__":
    create_counts()