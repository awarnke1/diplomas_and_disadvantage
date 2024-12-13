from dash import Dash, dcc, html, Input, Output, State, callback
import dash_dangerously_set_inner_html
from src.create_map import collectAndClean, createMap
from src.util import metric_inner_html, subset_inner_html

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
def description_met(met_dd):
    return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(metric_inner_html(met_dd))

@app.callback(
    Output("subset_description", "children"),
    Input("subset_radio", "value")
)
def description_subset(subset_radio):
    return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(subset_inner_html(subset_radio))

if __name__ == "__main__":
    app.run(debug=True)
