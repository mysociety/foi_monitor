"""
reformat wdtk data to match scottish ids
"""

from useful_inkleby.files import QuickGrid
from collections import Counter

resources_folder = r"C:\Users\alexj\Dropbox\mysociety\research_sites\resources\foisa"

def get_wdtk_to_scottish_id():
    qg = QuickGrid().open([resources_folder, "authorities.csv"])
    
    lookup = {}
    
    for r in qg:
        osic = int(r["authority_id"])
        
        for x in range(1,12):
            col = "wdtk_id_{0}".format(x)
            if r[col]:
                lookup[int(r[col])] = osic
            
    return lookup

def create_wdtk_count(year=2013):
    qg = QuickGrid().open([resources_folder, "info_request.csv"])
    lookup = get_wdtk_to_scottish_id()
    
    qg.generate_col("foisa", lambda x: lookup.get(int(x["public_body_id"]),None) )
    
    ids = []
    for r in qg:
        if year != 'alltime' and r["date_part"] != str(year):
            continue
        if r["foisa"]:
            ids.append(r["foisa"])

    c = Counter(ids)
    
    final = QuickGrid(header=["authority_id","year","count"])
    
    for k, v in c.items():
        final.add([k,year, v])
        
    final.save([resources_folder,"wdtk_{0}.csv".format(year)])

def create_counts():
    
    years = list(range(2013, 2020)) + ["alltime"] 
    for y in years:
        create_wdtk_count(y)
    
    
if __name__ == "__main__":
    create_counts()