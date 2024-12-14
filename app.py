from dash import Dash, dcc, html, Input, Output, State, callback
import dash_dangerously_set_inner_html
from src.create_map import collect_and_clean, create_map
from src.util import metric_inner_html, subset_inner_html

# create app instance
app = Dash(__name__)
# add an app title
app.title = 'Diplomas and Disadvantage Map'

# run the collect_and_clean function in create_map.py
counties, ranks, schools = collect_and_clean("raw_data/Index of Deep Disadvantage - Updated.xlsx", "raw_data/CSV_10312024-789.csv")

# create the layout for the page
def layout() -> list:

    # define a header for the top of the page
    header = html.H1('Diplomas and Disadvantage: Mapping U.S. Colleges on County Disadvantage Metrics')

    # create the label for the metric dropdown
    met_label = html.Label('Select a metric to map (scroll down on the list for more options):')
    
    # create the metric dropdown list, Rank is default
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

    # create the label for the subset selection
    subset_label = html.Label("Select a subset of schools to include:")

    # create the subset radio buttons, All is default
    subset_radio = dcc.RadioItems(id="subset_radio",
                                  options=["All", "HBCUs", "Tribal Colleges", "Community Colleges"],
                                  value="All"
                                 )

    # create the label for the check buttons
    tooltip_label = html.Label("Select which tooltips you would like to see:")

    # create the tooltip check buttons, both are selected by default
    tooltip_checklist = dcc.Checklist(id = "tooltip_checklist",
                                      options=["County", "School"],
                                      value=["County", "School"])

    # add all the elements to the children
    children = [header,                             # add the header (defined above)
                met_label,                          # add the metric dropdown label (defined above)
                met_dd,                             # add the metric dropdown (defined above)
                html.Div(id='met_description'),     # add a description for the metric (controlled by callback below)
                subset_label,                       # add the subset radio buttons label (defined above)
                subset_radio,                       # add the subset radio buttons (defined above)
                html.Div(id='subset_description'),  # add a description for the subset (controlled by callback below)
                dcc.Graph(id='graph'),              # add map (controlled by callback below)
                tooltip_label,                      # add the tooltip check buttons label (defined above)
                tooltip_checklist,                  # add the tooltip check buttons (defined above)
                # add link to the University of Michigan site at the bottom
                html.Div(html.A("Visit Index of Deep Disadvantage data source.", href='https://poverty.umich.edu/projects/understanding-communities-of-deep-disadvantage/', target="_blank"))
                ]
    # return the layout
    return children

# add the layout to the application
app.layout = html.Div(id='main-div', children=layout())

# callback for creating the map
@app.callback(
    Output("graph", "figure"),
    Input("subset_radio", "value"),
    Input("met_dd", "value"),
    Input("tooltip_checklist", "value")
)

# function for displaying/refreshing the mpa
def display_map(subset_radio, met_dd, tooltip_checklist):

    # set county tooltip option based on tooltip check button
    if "County" in tooltip_checklist:
        county_tooltip = True
    else:
        county_tooltip = False
    
    # set school tooltip option based on tooltip check button
    if "School" in tooltip_checklist:
        school_tooltip = True
    else:
        school_tooltip = False
    
    # run create_map function in create_map.py
    return create_map(subset_radio, met_dd, county_tooltip, school_tooltip, counties, ranks, schools)

# callback for metric description
@app.callback(
    Output("met_description", "children"),
    Input("met_dd", "value")
)

# function for metric description
def description_met(met_dd):
    # dash_dangerously_set_inner_html used to include line breaks in descriptions
    # run metric_inner_html function in util.py to get metric-specific description
    return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(metric_inner_html(met_dd))

# callback for subset description
@app.callback(
    Output("subset_description", "children"),
    Input("subset_radio", "value")
)

# function for subset description
def description_subset(subset_radio):
    # run subset_inner_html in util.py to get subset-specific description
    return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(subset_inner_html(subset_radio))

# when this script is run, app starts
if __name__ == "__main__":
    app.run(debug=True)
