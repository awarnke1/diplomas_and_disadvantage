import pandas as pd
import geopandas as gpd

# function used in create_map function in create_map.py
def create_title(subset: str,
                metric: str
                ) -> str:
    """
    Return the title of the figure based on the chosen metric and subset.
    Subset refers to the set of schools (i.e. "All", "Community Colleges").
    Metric refers to the county disadvantage measure (i.e. "Rank", "Life Expectancy").
    """
    # if no particular subset, use "U.S. Colleges"; otherwise, include the name of the subset in the title
    if subset == "All":
        subset_phrase = "U.S. Colleges"
    else:
        subset_phrase = subset
    
    # get more formal name for metric to be included in the title
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
    
    # return the combined title
    return (subset_phrase + " on " + metric_phrase)

# function used in create_map function in create_map.py
def subset_schools(subset: str,
                   schools: gpd.geodataframe.GeoDataFrame
                   ) -> gpd.geodataframe.GeoDataFrame:
    """
    Returns the schools geopandas dataframe, subset based on the user's choice.
    Subset refers to the set of schools (i.e. "All", "Community Colleges").
    Schools refers to the original schools geopandas dataframe.
    """

    # filters based on the column corresponding to the chosen subset
    if subset == "HBCUs":
        return(schools[schools["HD2023.Historically Black College or University"] == "Yes"])
    elif subset == "Tribal Colleges":
        return(schools[schools["HD2023.Tribal college"] == "Yes"])
    elif subset == "Community Colleges":
        return(schools[schools["community_college"] == 1])
    else:
        # if no particular subset, then original geopandas dataframe is returned
        return schools

# function used in the create_map function in create_map.py
def county_settings(metric: str,
                    ranks: pd.core.frame.DataFrame, 
                    schools: gpd.geodataframe.GeoDataFrame
                    ) -> list:
    """
    Returns a list with the modified ranks dataframe, modified schools geopandas dataframe, and the colorscale.
    Metric refers to the county disadvantage measure (i.e. "Rank", "Life Expectancy").
    Ranks refers to the original ranks dataframe with counties and all of their disadvantage metrics.
    Schools refers to the original schools geopandas dataframe.
    """

    # for each metric
    if metric == "Rank":
        ranks["metric_of_interest"] = ranks["level_0"].copy()           # copy the metric into the metric_of_interest column in ranks
        schools["metric_of_interest"] = schools["level_0"].copy()       # copy the metric into the metric_of_interest column in schools
        color = "deep_r"                                                # set the colorscale - deep_r means that a lower value indicates more disadvantage
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
        color = "deep"                                                  # deep colorscale means that a higher value indicates more disadvantage
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
        color = "ice_r"                      # ice_r colorscale means values don't correspond to disadvantage; higher number indicates higher racial concentration 
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
    
    return [ranks, schools, color]              # return modified ranks and schools, as well as the chosen colorscale

# function used in the description_met function in app.py
def metric_inner_html(met_dd: str
                      ) -> str:
    """
    Returns the description text for the user-chosen metric.
    Met_dd is the metric chosen by the user in Dash.
    """

    # returns a description of the selected metric
    if met_dd == "Rank":
        return("This setting displays the ranking of the Index of Deep Disadvantage, with 1 being the most disadvantaged county and 3,141 being the least disadvantaged county.<br><br>This index is made of metrics in three categories: health, poverty, and social mobility. Health includes life expectancy and infant low birth weight rate. Poverty includes percent of residents in poverty and deep povery. Social mobility includes a social mobility score calculated by Chetty, Hendren, and Katz.<br><br>For more information about this metric, you can visit the project page linked at the bottom of this site.")
    elif met_dd == "Raw Disadvantage":
        return("This setting displays the Index of Deep Disadvantage, with positive numbers indicating less disadvantaged counties and negative numbers indicating more disadvantaged counties.<br><br>This index is made of metrics in three categories: health, poverty, and social mobility. Health includes life expectancy and infant low birth weight rate. Poverty includes percent of residents in poverty and deep povery. Social mobility includes a social mobility score calculated by Chetty et al.<br><br>For more information about this metric, you can visit the project page linked at the bottom of this site.")
    elif met_dd == "Percent Below Poverty Line":
        return("This setting displays the percent of the county population living in poverty, as reported by the 2019 5-year American Community Survey.")
    elif met_dd == "Percent Below Deep Poverty Line":
        return("This setting displays the percent of the county population living below 50% of the Federal Poverty Line, as reported by the 2019 5-year American Community Survey.")
    elif met_dd == "Life Expectancy":
        return("This setting displays the life expectancy at birth, as reported by the County Health Rankings.")
    elif met_dd == "Low Birth Weight Rate":
        return("This setting displays the infant low birth weight rate, which is the share of live births weighing less than 2,500 grams, as reported by the County Health Rankings")
    elif met_dd == "Percent White":
        return("This setting displays the percentage of the county population that identifies as non-Hispanic white, as reported by the 2019 5-year American Community Survey.")
    elif met_dd == "Percent Black":
        return("This setting displays the percentage of the county population that identifies as non-Hispanic Black, as reported by the 2019 5-year American Community Survey.")
    elif met_dd == "Percent Native":
        return("This setting displays the percentage of the county population that identifies as Native, as reported by the 2019 5-year American Community Survey.")
    elif met_dd == "Percent Less Than High School Diploma":
        return("This setting displays the percentage of the county 25 years and over with less than a high school diploma, as reported by the 2019 5-year American Community Survey.")
    elif met_dd == "Percent College Graduates":
        return("This setting displays the percentage of the county 25 years and over with at least a bachelor's degree, as reported by the 2019 5-year American Community Survey.")
    elif met_dd == "Unemployment Rate":
        return("This setting displays the county unemployment rate, as reported by the 2019 5-year American Community Survey.")
    elif met_dd == "Gini Coefficient":
        return("This setting displays the county Gini coefficient, as reported by the 2019 5-year American Community Survey.<br><br>The Gini coefficient is a measure of inequality/wealth income, with 0 representing perfect equality and 1 representing perfect inequality.")
    elif met_dd == "Socioeconomic Mobility":
        return("This setting displays the county social mobility, as measured in research by Chetty, Hendren, and Katz. It represents the mean household income rank for children whose parents were at the 25th percentile of the national income distribution.")
    elif met_dd == "Climate Disasters":
        return("This setting displays how often the county has been hit by climate disasters — floods, hurricanes or wildfires — deemed “major” by the federal government from 1989 through 2017, as reported by the Federal Emergency Management Agency (FEMA).")

#function used in the description_subset function in app.py  
def subset_inner_html(subset_radio: str
                      ) -> str:
    """
    Returns the description text for the user-chosen school subset.
    Subset_radio is the subset chosen by the user in Dash.
    """

    #returns a description of the selected metric, if there is one chosen
    if subset_radio == "HBCUs":
        return('Historically Black Colleges and Universities are defined by the Higher Education Act of 1965 as "...any historically black college or university that was established prior to 1964, whose principal mission was, and is, the education of black Americans..."<br><br>This designation is set by the Department of Education.')
    elif subset_radio == "Tribal Colleges":
        return("The term 'tribal college' describes a college that is a member of the American Indian Higher Education Consortium. Most are tribally controlled and located on reservations.")
    elif subset_radio == "Community Colleges":
        return("Community colleges are public universities that primarily confers associate's degrees and certificates.<br><br>The Integrated Postsecondary Education Data System classifies a school based on its highest degree offered, not the primary degree that it confers. Therefore, for the purposes of this visualization, I defined community colleges as public institutions where 90% of degrees confered in 2023 were associate's degrees or certificates.")
    else:
        return("")