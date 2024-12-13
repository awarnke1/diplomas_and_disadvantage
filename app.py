from dash import Dash, dcc, html, Input, Output, State, callback
import dash_dangerously_set_inner_html
from create_map import collectAndClean, createMap

app = Dash(__name__)
app.title = 'College Map'

counties, ranks, schools = collectAndClean()

def layout() -> list:
    # Various items on the webpage
    children = []

    header = html.H1('Diplomas and Disadvantage: Mapping U.S. Colleges on County Disadvantage Metrics')
    children += [header]

    met_label = html.Label('Select a metric to map (scroll down on the list for more options):')
    met_dd = dcc.Dropdown(id='met_dd', 
                          options=['Rank',
                                   'Raw Disadvantage',
                                   'Percent Below Poverty Line',
                                   'Percent Below Deep Poverty Line',
                                   'Life Expectancy',
                                   'Low Birth Weight Rate',
                                   'Percent White', 
                                   'Percent Black',
                                   'Percent Native',
                                   'Percent Less Than High School Diploma',
                                   'Percent College Graduates', 
                                   'Unemployment Rate',
                                   'Gini Coefficient',
                                   'Socioeconomic Mobility',
                                   'Climate Disasters'],
                          value='Rank'
                          )
    children += [met_label, met_dd]

    children += [html.Div(id='met_description')]

    subset_label = html.Label("Select a subset of schools to include:")
    subset_radio = dcc.RadioItems(id="subset_radio",
                                  options=["All", "HBCUs", "Tribal Colleges", "Community Colleges"],
                                  value="All"
                                 )
    children += [subset_label, subset_radio]

    children += [html.Div(id='subset_description')]
    
    children += [dcc.Graph(id='graph')]

    tooltip_label = html.Label("Select which tooltips you would like to see:")
    tooltip_checklist = dcc.Checklist(id = "tooltip_checklist",
                                      options=["County", "School"],
                                      value=["County", "School"])
    children += [tooltip_label, tooltip_checklist]

    return children

# Add the layout to the application
app.layout = html.Div(id='main-div', children=layout())

@app.callback(
    Output("graph", "figure"),
    Input("subset_radio", "value"),
    Input("met_dd", "value"),
    Input("tooltip_checklist", "value")
)
def display_map(subset_radio, met_dd, tooltip_checklist):
    if "County" in tooltip_checklist:
        county_tooltip = True
    else:
        county_tooltip = False
    
    if "School" in tooltip_checklist:
        school_tooltip = True
    else:
        school_tooltip = False
    
    return createMap(subset_radio, met_dd, county_tooltip, school_tooltip, counties, ranks, schools)

@app.callback(
    Output("met_description", "children"),
    Input("met_dd", "value")
)
def description_1(met_dd):
    if met_dd == "Rank":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("This setting displays the ranking of the Index of Deep Disadvantage, with 1 being the most disadvantaged county and 3,141 being the least disadvantaged county.<br><br>This index is made of metrics in three categories: health, poverty, and social mobility. Health includes life expectancy and infant low birth weight rate. Poverty includes percent of residents in poverty and deep povery. Social mobility includes a social mobility score calculated by Chetty et al.<br><br>For more information about this metric, you can visit the project page linked at the bottom of this site.")) 
    elif met_dd == "Raw Disadvantage":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("This setting displays the Index of Deep Disadvantage, with positive numbers indicating less disadvantaged counties and negative numbers indicating more disadvantaged counties.<br><br>This index is made of metrics in three categories: health, poverty, and social mobility. Health includes life expectancy and infant low birth weight rate. Poverty includes percent of residents in poverty and deep povery. Social mobility includes a social mobility score calculated by Chetty et al.<br><br>For more information about this metric, you can visit the project page linked at the bottom of this site."))
    elif met_dd == "Percent Below Poverty Line":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("This setting displays the percent of the county population living in poverty, as reported by the 2019 5-year American Community Survey."))
    elif met_dd == "Percent Below Deep Poverty Line":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("This setting displays the percent of the county population living below 50% of the Federal Poverty Line, as reported by the 2019 5-year American Community Survey."))
    elif met_dd == "Life Expectancy":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("This setting displays the life expectancy at birth, as reported by the County Health Rankings."))
    elif met_dd == "Low Birth Weight Rate":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("This setting displays the infant low birth weight rate, which is the share of live births weighing less than 2,500 grams, as reported by the County Health Rankings"))
    elif met_dd == "Percent White":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("This setting displays the percentage of the county population that identifies as non-Hispanic white, as reported by the 2019 5-year American Community Survey."))
    elif met_dd == "Percent Black":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("This setting displays the percentage of the county population that identifies as non-Hispanic Black, as reported by the 2019 5-year American Community Survey."))
    elif met_dd == "Percent Native":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("This setting displays the percentage of the county population that identifies as Native, as reported by the 2019 5-year American Community Survey."))
    elif met_dd == "Percent Less Than High School Diploma":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("This setting displays the percentage of the county 25 years and over with less than a high school diploma, as reported by the 2019 5-year American Community Survey."))
    elif met_dd == "Percent College Graduates":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("This setting displays the percentage of the county 25 years and over with at least a bachelor's degree, as reported by the 2019 5-year American Community Survey."))
    elif met_dd == "Unemployment Rate":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("This setting displays the county unemployment rate, as reported by the 2019 5-year American Community Survey."))
    elif met_dd == "Gini Coefficient":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("This setting displays the county Gini coefficient, as reported by the 2019 5-year American Community Survey.<br><br>The Gini coefficient is a measure of inequality/wealth income, with 0 representing perfect equality and 1 representing perfect inequality."))
    elif met_dd == "Socioeconomic Mobility":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("This setting displays the county social mobility, as measured in research by Chetty and Hendren. It represents the mean household income rank for children whose parents were at the 25th percentile of the national income distribution."))
    elif met_dd == "Climate Disasters":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("This setting displays how often the county has been hit by climate disasters — floods, hurricanes or wildfires — deemed “major” by the federal government from 1989 through 2017, as reported by the Federal Emergency Management Agency (FEMA)."))

@app.callback(
    Output("subset_description", "children"),
    Input("subset_radio", "value")
)
def description_2(subset_radio):
    if subset_radio == "HBCUs":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML('Historically Black Colleges and Universities are defined by the Higher Education Act of 1965 as "...any historically black college or university that was established prior to 1964, whose principal mission was, and is, the education of black Americans..."<br><br>This designation is set by the Department of Education.'))
    elif subset_radio == "Tribal Colleges":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("The term 'tribal college' describes a college that is a member of the American Indian Higher Education Consortium. Most are tribally controlled and located on reservations."))
    elif subset_radio == "Community Colleges":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("Community colleges are public universities that primarily confers associate's degrees and certificates.<br><br>The Integrated Postsecondary Education Data System classifies a school based on its highest degree offered, not the primary degree that it confers. Therefore, for the purposes of this visualization, I defined community colleges as public institutions where 90% of degrees confered in 2023 were associate's degrees or certificates."))
    else:
        return("")

if __name__ == "__main__":
    app.run(debug=True)