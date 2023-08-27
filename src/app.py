import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from components.sidebar import get_sidebar_layout
from components.dashboards import get_dashboard_layout

estilos = ["https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css", "https://fonts.googleapis.com/icon?family=Material+Icons", dbc.themes.COSMO]
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"
# FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"


app = dash.Dash(__name__, external_stylesheets=estilos + [dbc_css])


app.config['suppress_callback_exceptions'] = True
app.scripts.config.serve_locally = True
server = app.server

# =========  Layout  =========== #
content = html.Div(id="page-content")


app.layout = dbc.Container(
    children=[
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Location(id='url'),
                        get_sidebar_layout(app)
                    ],md=2, style={'background-color': '#966F33','height':'210vh'}),
                dbc.Col(
                    [
                        get_dashboard_layout(app)
                    ],md=10, style={'background-color': '#f0f0f0', 'height':'210vh'})
            ]
        )
    ],
    fluid=True,
)

if __name__ == '__main__':
    app.run_server(debug=False)