import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import plotly.graph_objects as go
from urllib.request import urlopen
import json

def collectAndClean():
    '''
    Returns counties data (from Internet), cleans ranks data (from Excel file), and cleans schools data (from csv file).
    '''
    
    # load county data for geojson to work
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)

    # read in deep disadvantage data and configure fips
    ranks = pd.read_excel("raw_data/Index of Deep Disadvantage - Updated.xlsx", dtype={'fips': str})
    ranks.dropna(subset="fips", inplace = True)                # remove cities
    ranks["fips"] = ranks["fips"].apply(lambda x: x.zfill(5))  # format fips so they can be matched with county geojson info

    # read in school data
    schools = pd.read_csv("raw_data/CSV_10312024-789.csv")

    # will likely rename more columns as more measures are added
    schools.rename(columns={'institution name': 'name',
                            'HD2023.Longitude location of institution': 'lon',
                            'HD2023.Latitude location of institution': 'lat'},
                   inplace=True)

    # tutorial from https://datascience.quantecon.org/tools/maps.html
    schools["coordinates"] = list(zip(schools.lon, schools.lat))
    schools["coordinates"] = schools["coordinates"].apply(Point)
    schools = gpd.GeoDataFrame(schools, geometry="coordinates")

    return(counties, ranks, schools)


def createMap(counties: dict, ranks: pd.core.frame.DataFrame, schools: gpd.geodataframe.GeoDataFrame):
    '''
    Creates and saves basic plotly map based on county data, rank data, and school data.
    This function will also include more inputs once more metrics are implemented.
    '''

    # create default formatting
    MAP_FORMAT = {'width': 800,
                  'height': 400,
                  'margin': {'r':0 ,'t': 30, 'l': 0, 'b': 0},
                  'dragmode': False,
                  'mapbox_style': 'open-street-map',
                  'title': 'U.S. Colleges on Deep Disadvantage Ranked Counties'
                 }

    # create empty figure
    fig = go.Figure(layout=MAP_FORMAT)

    # create first trace - choropleth
    trace = go.Choroplethmapbox(geojson=counties,
                                locations=ranks.fips,
                                z=ranks.rank1,        # color based on ranking of deep disadvantage for each county
                                colorscale="deep_r",
                                zmin=1,
                                zmax=3618,            # total number of counties (plus cities - I may recalculate rankings for cities removed)
                                marker_line_width=0,
                                text = ranks.name)    # tooltip info

    # add trace to figure
    fig.add_trace(trace)

    # create second trace - scatterplot
    trace2 = go.Scattermapbox(lon = schools['lon'],
                             lat = schools['lat'],
                             text = schools['name'],  # tooltip text
                             marker_size=5,
                             marker_color="darkorange")

    # add trace to figure
    fig.add_trace(trace2)

    # center the figure on the continental US
    fig.update_mapboxes(center={'lat': 39, 'lon': -97},
                        zoom=3
                       )
    # save figure
    fig.write_html("figures/basic_map.html")
    
    return fig

if __name__ == "__main__":
    counties, ranks, schools = collectAndClean()
    basic_fig = createMap(counties, ranks, schools)
