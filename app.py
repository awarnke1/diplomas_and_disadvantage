from dash import Dash, dcc, html, Input, Output, State, callback
import dash_dangerously_set_inner_html
from create_map import collectAndClean, createMap

app = Dash(__name__)
app.title = 'Hello World!'

counties, ranks, schools = collectAndClean()

def layout() -> list:
    # Various items on the webpage
    children = []

    header = html.H1('College Map')
    children += [header]

    met_label = html.Label('Select a metric to map:')
    met_dd = dcc.Dropdown(id='met_dd', 
                          options=['Rank', 'Raw Disadvantage'],
                          value='Rank'
                          )
    children += [met_label, met_dd]

    children += [html.Div(id='met_description')]

    subset_label = html.Label("Select a subset of schools to include:")
    subset_radio = dcc.RadioItems(id="subset_radio",
                                  options=["All", "HBCUs", "Tribal Colleges"],
                                  value="All"
                                 )
    children += [subset_label, subset_radio]

    children += [html.Div(id='subset_description')]
    
    children += [dcc.Graph(id='graph')]

    return children

# Add the layout to the application
app.layout = html.Div(id='main-div', children=layout())

@app.callback(
    Output("graph", "figure"),
    Input("subset_radio", "value"),
    Input("met_dd", "value")
)
def display_map(subset_radio, met_dd):
    return createMap(subset_radio, met_dd, counties, ranks, schools)

@app.callback(
    Output("met_description", "children"),
    Input("met_dd", "value")
)
def description_1(met_dd):
    if met_dd == "Rank":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("This setting displays the ranking of the Index of Deep Disadvantage, with 1 being the most disadvantaged county and 3,618 being the least disadvantaged county.<br><br>This index is made of metrics in three categories: health, poverty, and social mobility. Health includes life expectancy and infant low birth weight rate. Poverty includes percent of residents in poverty and deep povery. Social mobility includes a social mobility score calculated by Chetty et al.<br><br>For more information about this metric, you can visit the project page linked at the bottom of this site.")) 
    else:
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("This setting displays the Index of Deep Disadvantage, with positive numbers indicating less disadvantaged counties and negative numbers indicating more disadvantaged counties.<br><br>This index is made of metrics in three categories: health, poverty, and social mobility. Health includes life expectancy and infant low birth weight rate. Poverty includes percent of residents in poverty and deep povery. Social mobility includes a social mobility score calculated by Chetty et al.<br><br>For more information about this metric, you can visit the project page linked at the bottom of this site."))

@app.callback(
    Output("subset_description", "children"),
    Input("subset_radio", "value")
)
def description_2(subset_radio):
    if subset_radio == "HBCUs":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML('Historically Black Colleges and Universities are defined by the Higher Education Act of 1965 as "...any historically black college or university that was established prior to 1964, whose principal mission was, and is, the education of black Americans..."<br><br>This designation is set by the Department of Education.'))
    elif subset_radio == "Tribal Colleges":
        return(dash_dangerously_set_inner_html.DangerouslySetInnerHTML("The term 'tribal college' describes a college that is a member of the American Indian Higher Education Consortium. Most are tribally controlled and located on reservations."))
    else:
        return("")

if __name__ == "__main__":
    app.run(debug=True)