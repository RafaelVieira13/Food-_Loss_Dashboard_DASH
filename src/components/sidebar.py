import os
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from datetime import datetime, date
import plotly.express as px
import numpy as np
import pandas as pd

def get_sidebar_layout(app):
    # ========= Layout ========= #
    layout = dbc.Col([
        
        # Sidebar Title
        html.H1('Food Loss',className='text font-weight-bold font-weight-bolder text-center display-2'),
        html.Hr(),
        
        # Sidebar Image
        html.Img(src=app.get_asset_url('FOOD_WASTE.png'), alt="Food Image",style={'width': '100%'}),
        
        # Dashboard Description
        html.P('The Food Loss Quantity Dashboard provides an interactive visualization of food loss quantities across various dimensions, including country, commodity, food group, and year.',
            style={'text-align':'justify','padding':'15px', 'font-size':'26px'}),
        html.P('It offers insights into the scale and distribution of food loss, aiding stakeholders in understanding and addressing food wastage on a global scale. Users can explore trends, patterns, and disparities in food loss, enabling informed decision-making and targeted interventions.',
            style={'text-align':'justify','padding':'15px', 'font-size':'26px'}),
                    
                ], style={'color': 'white', 'margin': '30px'})
    
    return layout





# =========  Callbacks  =========== #
# Pop-up receita
