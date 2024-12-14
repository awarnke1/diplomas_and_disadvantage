import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import plotly.graph_objects as go
from urllib.request import urlopen
import json
pd.options.mode.chained_assignment = None

from src.util import create_title, subset_schools, county_settings

def collect_and_clean():
    """
    Returns counties data (from Internet), cleans ranks data (from Excel file), and cleans schools data (from csv file).
    """
    
    # load county data for geojson to work
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)
    counties1 = gpd.read_file("https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json")

    # read in deep disadvantage data and configure fips
    ranks = pd.read_excel("raw_data/Index of Deep Disadvantage - Updated.xlsx", dtype={'fips': str})
    ranks.dropna(subset="fips", inplace = True)                # remove cities
    ranks["fips"] = ranks["fips"].apply(lambda x: x.zfill(5))  # format fips so they can be matched with county geojson info
    ranks = ranks.sort_values(by = "rank1")
    ranks = ranks.reset_index(drop=True).reset_index()
    ranks["level_0"] = ranks["level_0"] + 1

    ranks['name'] = ranks['name'].apply(lambda x: x.replace('city', 'City'))
    

    # read in school data
    schools = pd.read_csv("raw_data/CSV_10312024-789.csv")

    # will likely rename more columns as more measures are added
    schools.rename(columns={'institution name': 'name',
                            'HD2023.Longitude location of institution': 'lon',
                            'HD2023.Latitude location of institution': 'lat'},
                   inplace=True)
    
    schools["below_bachelors"] = schools["DRVC2023.Number of students receiving an Associate's degree"] + schools["DRVC2023.Number of students receiving certificates of less than 12 weeks"] + schools["DRVC2023.Number of students receiving certificates of at least 12 weeks, but less than 1 year"] + schools["DRVC2023.Number of students receiving a certificate of 1 but less than 4 years"]
    schools["bachelors_above"] = schools["DRVC2023.Number of students receiving a Bachelor's degree"] + schools["DRVC2023.Number of students receiving a Master's degree"] + schools["DRVC2023.Number of students receiving a Doctor's degree"]
    schools["below_bachelors"] = schools["below_bachelors"].fillna(0)
    schools["bachelors_above"] = schools["bachelors_above"].fillna(0)
    schools["ratio"] = schools["below_bachelors"] / (schools["below_bachelors"] + schools["bachelors_above"])
    schools["community_college"] = schools.apply(lambda x: 1 if x["ratio"] > 0.9 and x["HD2023.Control of institution"] == "Public" else 0, axis=1)

    # tutorial from https://datascience.quantecon.org/tools/maps.html
    schools["coordinates"] = list(zip(schools.lon, schools.lat))
    schools["coordinates"] = schools["coordinates"].apply(Point)
    schools = gpd.GeoDataFrame(schools, geometry="coordinates")

    county_list = []
    for point in schools["coordinates"]:
        in_county = counties1[counties1.geometry.contains(point)]["id"]
        try:
            county_list.append(in_county.iloc[0])
        except:
            county_list.append("0")
    schools["fips"] = county_list
    schools = schools.merge(ranks, how = "inner", on="fips")    #7 schools get booted off
    return(counties, ranks, schools)

def create_map(subset: str,
              metric: str, 
              county_tooltip: bool,
              school_tooltip: bool,
              counties: dict,
              ranks: pd.core.frame.DataFrame,
              schools: gpd.geodataframe.GeoDataFrame):
    """
    Creates and saves basic plotly map based on county data, rank data, and school data.
    This function will also include more inputs once more metrics are implemented.
    """

    schools = subset_schools(subset, schools)

    ranks, schools, color = county_settings(metric, ranks, schools)

    ranks["textbox"] = ranks["name"] + "<br>" + metric + ": " + ranks["metric_of_interest"].astype(str)
    schools["textbox"] = schools["name_x"] + "<br>County: " + schools["name_y"] + "<br>County " + metric + ": " + schools["metric_of_interest"].astype(str)
    
    if county_tooltip:
        hoverinfo_1 = "text"
    else:
        hoverinfo_1 = "skip"
    
    if school_tooltip:
        hoverinfo_2 = "text"
    else:
        hoverinfo_2 = "skip"


    # create default formatting
    MAP_FORMAT = {'width': 800,
                  'height': 400,
                  'margin': {'r':0 ,'t': 30, 'l': 0, 'b': 0},
                  'dragmode': False,
                  'mapbox_style': 'open-street-map',
                  'title': create_title(subset, metric)
                 }

    # create empty figure
    fig = go.Figure(layout=MAP_FORMAT)

    # create first trace - choropleth
    trace = go.Choroplethmapbox(geojson=counties,
                                locations=ranks.fips,
                                z=ranks.metric_of_interest,        # color based on ranking of deep disadvantage for each county
                                colorscale=color,
                                zmin=min(ranks.metric_of_interest),
                                zmax=max(ranks.metric_of_interest),
                                marker_line_width=0,
                                hoverinfo=hoverinfo_1,
                                text = ranks.textbox)   # tooltip info

    # add trace to figure
    fig.add_trace(trace)

    # create second trace - scatterplot
    trace2 = go.Scattermapbox(lon = schools['lon'],
                             lat = schools['lat'],
                             hoverinfo=hoverinfo_2,
                             text = schools['textbox'],  # tooltip text
                             marker_size=5,
                             marker_color="darkorange")

    # add trace to figure
    fig.add_trace(trace2)

    # center the figure on the continental US
    fig.update_mapboxes(center={'lat': 39, 'lon': -97},
                        zoom=3
                       )
    # save figure
    #fig.write_html("figures/basic_map.html")
    
    return(fig)
