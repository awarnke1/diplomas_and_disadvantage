import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import plotly.graph_objects as go
from urllib.request import urlopen
import json
pd.options.mode.chained_assignment = None

def collectAndClean():
    '''
    Returns counties data (from Internet), cleans ranks data (from Excel file), and cleans schools data (from csv file).
    '''
    
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
    
    schools["below_bachelors"] = schools["DRVC2023.Number of students receiving an Associate's degree"]+ schools["DRVC2023.Number of students receiving certificates of less than 12 weeks"] + schools["DRVC2023.Number of students receiving certificates of at least 12 weeks, but less than 1 year"] + schools["DRVC2023.Number of students receiving a certificate of 1 but less than 4 years"]
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

def createTitle(subset: str,
                metric: str
                ):
    if subset == "All":
        descript = "U.S. Colleges"
    else:
        descript = subset
    
    if metric == "Rank":
        metric_phrase = "Deep Disadvantage-Ranked Counties"
    elif metric == "Raw Disadvantage":
        metric_phrase = "Counties with Index of Deep Disadvantage"
    elif metric == "Percent Below Poverty Line":
        metric_phrase = "County Percentages of Residents in Poverty"
    elif metric == "Percent Below Deep Poverty Line":
        metric_phrase = "County Percentages of Residents in Deep Poverty"
    elif metric == "Life Expectancy":
        metric_phrase = "County Life Expectancies"
    elif metric == "Low Birth Weight Rate":
        metric_phrase = "County Infant Low Birth Weight Rates"
    elif metric == "Percent White":
        metric_phrase = "County Percentages of Residents who Identify as White"
    elif metric == "Percent Black":
        metric_phrase = "County Percentages of Residents who Identify as Black"
    elif metric == "Percent Native":
        metric_phrase = "County Percentages of Residents who Identify as Native"
    elif metric == "Percent Less Than High School Diploma":
        metric_phrase = "County Percentages of Residents with Less Than High School Diploma"
    elif metric == "Percent College Graduates":
        metric_phrase = "County Percentages of Residents who are College Graduates"
    elif metric == "Unemployment Rate":
        metric_phrase = "County Umemployment Rates"
    elif metric == "Gini Coefficient":
        metric_phrase = "County Gini Coefficients"
    elif metric == "Socioeconomic Mobility":
        metric_phrase = "County Socioeconomic Mobilities"
    elif metric == "Climate Disasters":
        metric_phrase = "County Climate Disasters"
    
    return (descript + " on " + metric_phrase)


def createMap(subset: str,
              metric: str, 
              county_tooltip: bool,
              school_tooltip: bool,
              counties: dict,
              ranks: pd.core.frame.DataFrame,
              schools: gpd.geodataframe.GeoDataFrame):
    '''
    Creates and saves basic plotly map based on county data, rank data, and school data.
    This function will also include more inputs once more metrics are implemented.
    '''

    if subset == "HBCUs":
        schools = schools[schools["HD2023.Historically Black College or University"] == "Yes"]
    elif subset == "Tribal Colleges":
        schools = schools[schools["HD2023.Tribal college"] == "Yes"]
    elif subset == "Community Colleges":
        schools = schools[schools["community_college"] == 1]

    if metric == "Rank":
        ranks["metric_of_interest"] = ranks["level_0"].copy()
        schools["metric_of_interest"] = schools["level_0"].copy()
        color = "deep_r"
    elif metric == "Raw Disadvantage":
        ranks["metric_of_interest"] = round(ranks["index"].copy(), 2)
        schools["metric_of_interest"] = round(schools["index"].copy(), 2)
        color = "deep_r"
    elif metric == "Percent Below Poverty Line":
        ranks["metric_of_interest"] = ranks["pct_belowpov"].copy()
        schools["metric_of_interest"] = schools["pct_belowpov"].copy()
        color = "deep"
    elif metric == "Percent Below Deep Poverty Line":
        ranks["metric_of_interest"] = ranks["pct_deeppov"].copy()
        schools["metric_of_interest"] = schools["pct_deeppov"].copy()
        color = "deep"
    elif metric == "Life Expectancy":
        ranks["metric_of_interest"] = ranks["life_exp"].copy()
        schools["metric_of_interest"] = schools["life_exp"].copy()
        color = "deep_r"
    elif metric == "Low Birth Weight Rate":
        ranks["metric_of_interest"] = ranks["lbw"].copy()
        schools["metric_of_interest"] = schools["lbw"].copy()
        color = "deep"
    elif metric == "Percent White":
        ranks["metric_of_interest"] = ranks["pct.white.nonhisp"].copy()
        schools["metric_of_interest"] = schools["pct.white.nonhisp"].copy()
        color = "ice_r"
    elif metric == "Percent Black":
        ranks["metric_of_interest"] = ranks["pct.black.nonhisp"].copy()
        schools["metric_of_interest"] = schools["pct.black.nonhisp"].copy()
        color = "ice_r"
    elif metric == "Percent Native":
        ranks["metric_of_interest"] = ranks["pct.native"].copy()
        schools["metric_of_interest"] = schools["pct.native"].copy()
        color = "ice_r"
    elif metric == "Percent Less Than High School Diploma":
        ranks["metric_of_interest"] = ranks["pct.less.than.HS"].copy()
        schools["metric_of_interest"] = schools["pct.less.than.HS"].copy()
        color = "deep"
    elif metric == "Percent College Graduates":
        ranks["metric_of_interest"] = ranks["pct.college.grad"].copy()
        schools["metric_of_interest"] = schools["pct.college.grad"].copy()
        color = "deep_r"
    elif metric == "Unemployment Rate":
        ranks["metric_of_interest"] = ranks["unemployment.rate"].copy()
        schools["metric_of_interest"] = schools["unemployment.rate"].copy()
        color = "deep"
    elif metric == "Gini Coefficient":
        ranks["metric_of_interest"] = ranks["gini"].copy()
        schools["metric_of_interest"] = schools["gini"].copy()
        color = "deep"
    elif metric == "Socioeconomic Mobility":
        ranks["metric_of_interest"] = round(ranks["mobility"].copy(), 2)
        schools["metric_of_interest"] = round(schools["mobility"].copy(), 2)
        color = "deep_r"
    elif metric == "Climate Disasters":
        ranks["metric_of_interest"] = ranks["climate.disasters"].copy().astype(int)
        schools["metric_of_interest"] = schools["climate.disasters"].copy().astype(int)
        color = "deep"

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
                  'title': createTitle(subset, metric)
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

if __name__ == "__main__":
    counties, ranks, schools = collectAndClean()
    basic_fig = createMap("All", "Rank", True, True, counties, ranks, schools)
