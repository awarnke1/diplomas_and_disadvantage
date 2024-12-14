import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import plotly.graph_objects as go
from urllib.request import urlopen
import json
pd.options.mode.chained_assignment = None

try:
    # works if run by app.py
    from src.util import create_title, subset_schools, county_settings
except:
    # works if run as standalone program
    from util import create_title, subset_schools, county_settings

# function used at the beginning of the app.py file
def collect_and_clean(ranks_location: str,
                      schools_location: str
                      ) -> list:
    """
    Returns list with counties data (from Internet), clean ranks data (from Excel file), and clean schools data (from csv file).
    Ranks_location is the file location of the ranks data (i.e. "raw_data/Index of Deep Disadvantage - Updated.xlsx")
    Schools_lcation is the file location of the schools data (i.e. "raw_data/CSV_10312024-789.csv")
    """
    
    # load county data for graphing
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)
    
    # load county data as geopandas dataframe to match each school with its county
    counties_gpd = gpd.read_file("https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json")


    # read in deep disadvantage data and configure fips
    ranks = pd.read_excel(ranks_location, dtype={"fips": str})
    ranks.dropna(subset="fips", inplace = True)                # remove cities
    ranks["fips"] = ranks["fips"].apply(lambda x: x.zfill(5))  # format fips so they can be matched with county geojson info

    # redo ranks with only counties (rank1 variable includes top 500 cities, which I removed above)
    ranks = ranks.sort_values(by = "rank1")                 # sort by original rankings
    ranks = ranks.reset_index(drop=True).reset_index()      # reset index so that index is the new ranking, called level_0      
    ranks["level_0"] = ranks["level_0"] + 1                 # index starts at 0, so add 1 so that ranking now starts at 1

    # fix counties with 'city' in the name so that 'city' is capitalized to be consistent with all other county names
    ranks["name"] = ranks["name"].apply(lambda x: x.replace("city", "City"))
    

    # read in school data
    schools = pd.read_csv(schools_location)

    # rename columns that will be used in mapping
    schools.rename(columns={"institution name": "name",
                            "HD2023.Longitude location of institution": "lon",
                            "HD2023.Latitude location of institution": "lat"},
                   inplace=True)
    
    # calculate degree ratios to be able to define community colleges
    # calculate number of associate's degrees and certificates
    schools["below_bachelors"] = schools["DRVC2023.Number of students receiving an Associate's degree"] + schools["DRVC2023.Number of students receiving certificates of less than 12 weeks"] + schools["DRVC2023.Number of students receiving certificates of at least 12 weeks, but less than 1 year"] + schools["DRVC2023.Number of students receiving a certificate of 1 but less than 4 years"]
    # calculate number of bachelor's, master's, and doctoral degrees
    schools["bachelors_above"] = schools["DRVC2023.Number of students receiving a Bachelor's degree"] + schools["DRVC2023.Number of students receiving a Master's degree"] + schools["DRVC2023.Number of students receiving a Doctor's degree"]
    # fill in N/As in both columns with 0 so that ratio works
    schools["below_bachelors"] = schools["below_bachelors"].fillna(0)
    schools["bachelors_above"] = schools["bachelors_above"].fillna(0)
    # calculate ratio of degrees that are associate's degrees and certificates
    schools["ratio"] = schools["below_bachelors"] / (schools["below_bachelors"] + schools["bachelors_above"])
    # community colleges defined as public institutions with over 90% of degrees being associate's degrees and certificates
    schools["community_college"] = schools.apply(lambda x: 1 if x["ratio"] > 0.9 and x["HD2023.Control of institution"] == "Public" else 0, axis=1)

    # prep schools dataframe for mapping by defining the school's point in a geopandas dataframe
    # tutorial from https://datascience.quantecon.org/tools/maps.html
    schools["coordinates"] = list(zip(schools.lon, schools.lat))
    schools["coordinates"] = schools["coordinates"].apply(Point)
    schools = gpd.GeoDataFrame(schools, geometry="coordinates")

    # create empty list to hold all of the counties
    county_list = []
    # loop through each school's point
    for point in schools["coordinates"]:
        # match with the counties geopandas dataframe to determine which county the point is in
        in_county = counties_gpd[counties_gpd.geometry.contains(point)]["id"]
        # if a county is found, the fips code is added to the county list, otherwise a 0 is added to the list
        try:
            county_list.append(in_county.iloc[0])
        except:
            county_list.append("0")
    schools["fips"] = county_list                               # add list of fips as a new column in schools
    schools = schools.merge(ranks, how = "inner", on="fips")    # merge with ranks list so that county name and data is present for each school; there are only 7 schools with no fips information found
    return [counties, ranks, schools] 

# function used in the display_map function in app.py
# rerun every time a setting is changed by the user
def create_map(subset: str,
              metric: str, 
              county_tooltip: bool,
              school_tooltip: bool,
              counties: dict,
              ranks: pd.core.frame.DataFrame,
              schools: gpd.geodataframe.GeoDataFrame
              ) -> go.Figure:
    """
    Creates and saves basic plotly map based on county data, rank data, and school data.
    This function will also include more inputs once more metrics are implemented.
    """

    # run subset_schools function in util.py to get filtered geopandas dataframe
    schools = subset_schools(subset, schools)

    # run county_settings function in util.py to get modified ranks and schools, as well as the appropriate colorscale
    ranks, schools, color = county_settings(metric, ranks, schools)

    # set the tooltip text to include the desired metric for counties and schools
    ranks["textbox"] = ranks["name"] + "<br>" + metric + ": " + ranks["metric_of_interest"].astype(str)
    schools["textbox"] = schools["name_x"] + "<br>County: " + schools["name_y"] + "<br>County " + metric + ": " + schools["metric_of_interest"].astype(str)
    
    # checks if county tooltip option is selected and toggles it on ("text") or off ("skip")
    if county_tooltip:
        hoverinfo_county = "text"
    else:
        hoverinfo_county = "skip"
    
    # checks if school tooltip option is selected and toggles it on ("text") or off ("skip")
    if school_tooltip:
        hoverinfo_school = "text"
    else:
        hoverinfo_school = "skip"


    # create default formatting
    MAP_FORMAT = {"width": 800,
                  "height": 400,
                  "margin": {"r":0 ,"t": 30, "l": 0, "b": 0},
                  "dragmode": False,
                  "mapbox_style": "open-street-map",
                  # run create_map function in util.py to get title customized with metric and subset selected by user
                  "title": create_title(subset, metric)
                 }

    # create empty figure
    fig = go.Figure(layout=MAP_FORMAT)

    # create first trace - choropleth
    trace = go.Choroplethmapbox(geojson=counties,
                                locations=ranks.fips,
                                z=ranks.metric_of_interest,        # color based on chosen metric
                                colorscale=color,                  # colorscale based on chosen metric
                                zmin=min(ranks.metric_of_interest),
                                zmax=max(ranks.metric_of_interest),
                                marker_line_width=0,
                                hoverinfo=hoverinfo_county,             # set above based on user-selected option
                                text = ranks.textbox)                   # tooltip info (ignored if hover_info_county = "skip")

    # add trace to figure
    fig.add_trace(trace)

    # create second trace - scatterplot
    trace2 = go.Scattermapbox(lon = schools["lon"],
                             lat = schools["lat"],
                             hoverinfo=hoverinfo_school,        # set above based on user-selected option
                             text = schools["textbox"],         # tooltip info (ignored if hover_info_school = "skip")
                             marker_size=5,
                             marker_color="darkorange")

    # add trace to figure
    fig.add_trace(trace2)

    # center the figure on the continental US
    fig.update_mapboxes(center={"lat": 39, "lon": -97},
                        zoom=3
                       )
    
    return(fig)

if __name__ == "__main__":
    counties, ranks, schools = collect_and_clean("../raw_data/Index of Deep Disadvantage - Updated.xlsx", "../raw_data/CSV_10312024-789.csv")
    fig = create_map("All", "Rank", True, True, counties, ranks, schools)
    fig.write_html("../figures/basic_map.html")
