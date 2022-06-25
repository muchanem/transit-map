import geopandas
import pandas as pd
import numpy as np

# grab relevant data/columns and create a few new ones
tracts_data = pd.read_csv("census_data/ACSDT5Y2020.B08301_data_with_overlays_2022-05-31T225204.csv", skiprows=[1])
tracts_data = tracts_data[["GEO_ID", "B08301_001E", "B08301_003E", "B08301_010E", "B08301_021E", "B08301_004E"]]
tracts_data = tracts_data.rename(columns={"B08301_001E": "total", "B08301_003E": "alone", "B08301_004E": "carpool", "B08301_010E": "transit", "B08301_021E": "wfh"})
tracts_data["other"] = tracts_data["total"] - (tracts_data[tracts_data.columns[2:]].sum(axis=1))
tracts_data["not_alone"] = tracts_data["total"] -tracts_data["alone"]
tracts_geo = geopandas.read_file("census_shapefiles/cb_2021_us_tract_500k.shp")

# centroids are not guaranteed to be within shape boundaries, and this is faster anyway
points = tracts_geo["geometry"].representative_point()

# I'm going to use some software with built in mapping (probably plotly), so I only need lat+long, not full shapes
df = pd.DataFrame({
    "lon": points.x,
    "lat": points.y,
    "GEO_ID": tracts_geo["AFFGEOID"]
})

# merge tracts data and locations
df = df.merge(tracts_data,on="GEO_ID")

# create percentage columns for color gneration
df["p_transit"] = df["transit"]/df["not_alone"]
df["p_carpool"] = df["carpool"]/df["not_alone"]
df["p_wfh"] = df["wfh"]/df["not_alone"]

# round off values to avoid float -> int conversion issues
df.loc[:,["p_transit","p_carpool", "p_wfh"]] = df[["p_transit","p_carpool", "p_wfh"]].replace(np.inf, 1.0)
df.loc[:,["p_transit","p_carpool", "p_wfh"]] = df[["p_transit","p_carpool", "p_wfh"]].replace([np.nan,-np.inf], 0.0)

# this is incredibly dumb. pandas does not have the option to set formaters when casting between types, so i have this hamfisted code
df["color"] = "#" + np.round(255*(1-df["p_transit"])).astype(int).apply("{:02x}".format) \
    + np.round(255*(1-df["p_carpool"])).astype(int).apply("{:02x}".format) \
    + np.round(255*(1-df["p_wfh"])).astype(int).apply("{:02x}".format)

print(df)