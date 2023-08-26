from dash import html, dcc
from dash.dependencies import Input, Output, State
from datetime import date, datetime, timedelta
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import calendar
from globals import *
from src.app import app
import re
import pycountry
from pycountry_convert import country_name_to_country_alpha2, country_alpha2_to_continent_code


# ========== Styles ============ #
tab_card = {'height': '100%'}

main_config = {
    "hovermode": "x unified",
    "legend": {
        "yanchor": "top",
        "y": 0.9,
        "xanchor": "left",
        "x": 0.1,
        "title": {"text": None},
        "font": {"color": "white"},
        "bgcolor": "rgba(0,0,0,0.5)"
    },
    "margin": {"l": 10, "r": 10, "t": 10, "b": 10},
    "hoverlabel": {"font": {"size": 20}} 
}

config_graph = {"displayModeBar": False, "showTips": False}


# =========  Data Reading and Cleaning  =========== #
df = pd.read_csv('Food_Loss_and_Waste.csv',low_memory=False)

df.drop(columns=['m49_code','region','cpc_code','loss_percentage_original','loss_quantity','activity','treatment','cause_of_loss',
                      'sample_size','method_data_collection','reference','url','notes'],inplace=True)

def remove_text_between_parentheses(text):
    return re.sub(r'\([^)]*\)', '', text).strip()

df['country'] = df['country'].apply(remove_text_between_parentheses)
# Replace China,Taiwan to Taiwan
df['country'] = df['country'].str.replace('China,Taiwan','Taiwan')

# Replace Republic of Korea to South Korea
df['country'] = df['country'].str.replace('Republic of Korea','South Korea')

# Replace Democratic People's South Korea to South Korea
df['country'] = df['country'].str.replace("Democratic People's South Korea",'South Korea')

# Replace the The former Yugoslav Republic of Macedonia to North Macedonia
df['country'] = df['country'].str.replace('The former Yugoslav Republic of Macedonia','North Macedonia')

# Get Country ISO-3 Code
def get_iso3_country_codes(country_name):
    try:
        country = pycountry.countries.get(name=country_name)
        return country.alpha_3
    except AttributeError:
        return None
    
def get_iso_codes(country_name):
    if country_name == 'United States of America':
        return 'USA'
    if country_name == 'Venezuela':
        return 'VEN'
    if country_name == 'United Republic of Tanzania':
        return 'TZA'
    if country_name == 'Democratic Republic of the Congo':
        return 'COD'
    if country_name == 'United Kingdom of Great Britain and Northern Ireland':
        return 'GBR'
    if country_name == 'Iran':
        return 'IRN'
    if country_name == 'South Korea':
        return 'KOR'
    if country_name == 'Bolivia':
        return 'BOL'
    if country_name == 'Republic of Moldova':
        return 'MDA'
    if country_name == 'Taiwan':
        return 'TWN'

def get_country_codes(country_name):
    iso_code = get_iso3_country_codes(country_name)
    if iso_code:
        return iso_code
    else:
        return get_iso_codes(country_name)

df['country_code_iso'] = df['country'].apply(get_country_codes)

# Let´s remove the countries with 'nan' country code
no_cc = df[df['country_code_iso'].isna()].index
df.drop(no_cc, inplace=True)

# Get the Alpha-2 continent code
def get_continent(row):
    try:
        cn_code = country_name_to_country_alpha2(row['country'], cn_name_format="default")
        cont_code = country_alpha2_to_continent_code(cn_code)
        return cont_code
    except KeyError:
        return "Unknown Continent"
    
df['continent_code'] = df.apply(get_continent, axis=1)

# Let´s get the continent-code of the country 'Timor-Leste'
timor_leste = df[df['country'] == 'Timor-Leste'].index

df.loc[timor_leste, 'continent_code'] = 'AS'

# Convert the 'commodity' column to lowercase
df['commodity'] = df['commodity'].str.lower()

mask = df['commodity'].str.contains('maize')
df.loc[mask, 'commodity'] = 'maize'

def replace_comm(commodity_searched,commodity_new):
    mask = df['commodity'].str.contains(commodity_searched)
    df.loc[mask, 'commodity'] = commodity_new
    
replace_comm('rice','rice')
replace_comm('wheat','wheat')
replace_comm('potatoes','potatoes')
replace_comm('groundnuts','groundnuts')
replace_comm('coconuts','coconuts')
replace_comm('walnuts','walnuts')
replace_comm('cashew nuts','cashew nuts')
replace_comm('hazelnuts','hazelnuts')
replace_comm('other nuts','other nuts')
replace_comm('chestnuts','chestnuts')
replace_comm('brazil nuts','brazil nuts')
replace_comm('cranberries','cranberries')
replace_comm('raspeberries','raspberries')
replace_comm('other berries and fruits of the genus vaccinium n.e.','other berries')
replace_comm('anise, badian, coriander, cumin, caraway, fennel and juniper berries, raw','other berries')
replace_comm('kiwi','kiwi')
replace_comm('other fruits, n.e.c.','other fruits')
replace_comm('other tropical and subtropical fruits, n.e.c.','other fruits')
replace_comm('other tropical and subtropical fruits, n.e.','other fruits')
replace_comm('other fruits, n.e.','other fruits')
replace_comm('citrus','other fruits')
replace_comm('other stone fruits','other fruits')
replace_comm('juice of citrus fruit n.e.c.','citrus juice')
replace_comm('grapefruit juice','grapefruit juice')
replace_comm('meat of cattle','cattle meat')
replace_comm('edible offal of cattle, fresh, chilled or frozen','cattle meat')
replace_comm('cattle fat, unrendered','cattle meat')
df.loc[df['commodity'].isin(['meat of pig, fresh or chilled',
                            'meat of pig, fresh or chilled',
                            'edible offal of pigs, fresh, chilled or frozen',
                            'pig, butcher fat',
                            'pig, butcher fat',
                            'pig, butcher fat',
                            'meat of pig boneless (pork), fresh or chilled',
                            'meat of pig with the bone, fresh or chilled',
                            'pig meat, cuts, salted, dried or smoked (bacon and ham)']),'commodity'] = 'pig meat'
replace_comm('chicken','poultry meat')
df.loc[df['commodity'].isin(['meat of sheep, fresh or chilled',
                            'sheep']),'commodity'] = 'sheep meat'
df.loc[df['commodity'].isin(['meat of goat, fresh or chilled',
                            'goats',
                            'meat of goat, fresh or chilled (indigenous)']),'commodity'] = 'goat meat'
df.loc[df['commodity'].isin(['meat of other domestic camelids (fresh)']),'commodity'] = 'other meat'
replace_comm('vegetable','other vegetables')
replace_comm('eggs','eggs')
df.loc[df['commodity'].isin(['plantains and others',
                            'plantains and cooking bananas']),'commodity'] = 'plantains'
df.loc[df['commodity'].isin(['eggplants (aubergines)']),'commodity'] = 'eggplants'
replace_comm('mangoes','mangoes, guavas and mangosteens')
replace_comm('cheese','cheese')
replace_comm('butter','butter')
df.loc[df['commodity'].isin(['beans, dry']),'commodity'] = 'beans'
df.loc[df['commodity'].isin(['broad beans and horse beans, dry',
                            'cocoa beans',
                            'broad beans and horse beans, green',
                            'bambara beans, dry']),'commodity'] = 'beans'
df.loc[df['commodity'].isin(['cane sugar, non-centrifugal',
                            'sugar cane']),'commodity'] = 'cane sugar'
df.loc[df['commodity'].isin(['sugar beet']),'commodity'] = 'beet sugar'
df.loc[df['commodity'].isin(['peas, dry',
                            'peas, green']),'commodity'] = 'peas'
df.loc[df['commodity'].isin(['cow peas, dry']),'commodity'] = 'cow peas'
df.loc[df['commodity'].isin(['pigeon peas, dry']),'commodity'] = 'pigeon peas'
df.loc[df['commodity'].isin(['chick peas, dry']),'commodity'] = 'chick peas'
replace_comm('onions','onions and shallots')
replace_comm('cereals','other cereals')
replace_comm('cassava','cassava')
replace_comm('honey','honey')
# Let´s remove the commodities with less then 15 count
commodity_count = df['commodity'].value_counts()
less_commodity = commodity_count[commodity_count<15].index
df = df[~df['commodity'].isin(less_commodity)]
replace_comm('mushrooms','mushrooms')
replace_comm('pepper','chillies and peppers')
replace_comm('green','garlic')
df.loc[df['commodity'].isin(['other stimulant, spice and aromatic crops, n.e.c.']),'commodity'] = 'others stimulants, spices and aromatics crops'
replace_comm('dairy','other dairy products')
replace_comm('roots','edible roots')
replace_comm('almond','almonds')
replace_comm('pulse','pulses')
replace_comm('lentils','lentils')
# Dictionary mapping commodities to food groups
commodity_to_food_group = {
    'groundnuts': 'Nuts',
    'rice': 'Grains',
    'wheat': 'Grains',
    'maize': 'Grains',
    'sorghum': 'Grains',
    'millet': 'Grains',
    'beans': 'Legumes',
    'raw milk of cattle': 'Dairy',
    'eggs': 'Meat & Animal Products',
    'tomatoes': 'Vegetables',
    'cauliflowers and broccoli': 'Vegetables',
    'cucumbers and gherkins': 'Vegetables',
    'garlic': 'Vegetables',
    'potatoes': 'Vegetables',
    'plantains': 'Fruits',
    'pig meat': 'Meat & Animal Products',
    'mixed grain': 'Grains',
    'cattle meat': 'Meat & Animal Products',
    'grapes': 'Fruits',
    'peas': 'Legumes',
    'barley': 'Grains',
    'asparagus': 'Vegetables',
    'cabbages': 'Vegetables',
    'lettuce and chicory': 'Vegetables',
    'watermelons': 'Fruits',
    'cantaloupes and other melons': 'Fruits',
    'chillies and peppers': 'Vegetables',
    'carrots and turnips': 'Vegetables',
    'onions and shallots': 'Vegetables',
    'other vegetables': 'Vegetables',
    'apples': 'Fruits',
    'pears': 'Fruits',
    'apricots': 'Fruits',
    'cherries': 'Fruits',
    'peaches and nectarines': 'Fruits',
    'plums and sloes': 'Fruits',
    'kiwi': 'Fruits',
    'strawberries': 'Fruits',
    'blueberries': 'Fruits',
    'cranberries': 'Fruits',
    'other berries': 'Fruits',
    'other fruits': 'Fruits',
    'oats': 'Grains',
    'rye': 'Grains',
    'soya beans': 'Legumes',
    'eggplants': 'Vegetables',
    'pumpkins, squash and gourds': 'Vegetables',
    'okra': 'Vegetables',
    'bananas': 'Fruits',
    'papayas': 'Fruits',
    'pineapples': 'Fruits',
    'other cereals': 'Grains',
    'poultry meat': 'Meat & Animal Products',
    'mangoes, guavas and mangosteens': 'Fruits',
    'avocados': 'Fruits',
    'spinach': 'Vegetables',
    'pomelos and grapefruits': 'Fruits',
    'lemons and limes': 'Fruits',
    'fonio': 'Grains',
    'cassava': 'Tubers',
    'oranges': 'Fruits',
    'yams': 'Tubers',
    'cow peas': 'Legumes',
    'pulses': 'Legumes',
    'quinoa': 'Grains',
    'tangerines, mandarins, clementines': 'Fruits',
    'lupins': 'Legumes',
    'edible roots': 'Roots',
    'lentils': 'Legumes',
    'coconuts': 'Nuts',
    'other dairy products': 'Dairy',
    'cheese': 'Dairy',
    'raw milk of sheep': 'Dairy',
    'triticale': 'Grains',
    'rapeseed or colza seed': 'Oilseeds',
    'sunflower seed': 'Oilseeds',
    'linseed': 'Oilseeds',
    'cane sugar': 'Sweeteners',
    'refined sugar': 'Sweeteners',
    'beet sugar': 'Sweeteners',
    'raspberries': 'Fruits',
    'mushrooms': 'Vegetables',
    'cashew nuts': 'Nuts',
    'areca nuts': 'Nuts',
    'cottonseed': 'Oilseeds',
    'mustard seed': 'Oilseeds',
    'safflower seed': 'Oilseeds',
    'others stimulants, spices and aromatics crops': 'Spices',
    'chick peas': 'Legumes',
    'pigeon peas': 'Legumes',
    'sheep meat': 'Meat & Animal Products',
    'figs': 'Fruits',
    'almonds': 'Nuts',
    'walnuts': 'Nuts',
    'raw milk of goats': 'Dairy',
    'sesame seed': 'Oilseeds',
    'oil palm fruit': 'Oilseeds',
    'yautia': 'Tubers',
    'olives': 'Fruits',
    'artichokes': 'Vegetables',
    'grapefruit juice': 'Beverages',
    'orange juice': 'Beverages',
    'pineapple juice': 'Beverages',
    'grape juice': 'Beverages',
    'apple juice': 'Beverages',
    'hazelnuts': 'Nuts',
    'copra': 'Oilseeds'
}
df['food group']=df['commodity'].map(commodity_to_food_group)
# Based on the loss percentage let´s get the loss quantity by 1 kg
df['loss quantity by 1 kg (g/kg)'] = (df['loss_percentage'] /100) * 1

# =========  Layout  =========== #
layout = dbc.Col([
    # Row 1 -- Food Group Filter
    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.Legend('Choose the Food Group:', className='card-title', style={'font-size': '40px', 'font-weight': 'bold'}),
                html.Div(
                    dcc.Dropdown(
                        id='dropdown_food_group',  # Fixed typo in id
                        options=[{'label': food_group, 'value': food_group} for food_group in df['food group'].unique()],
                        persistence=True,
                        persistence_type='session',
                        style={'font-size': '26px', 'width': '600px', 'height': '50px'}
                    )
                )
            ], style={'margin': '20px'})
        ])
    ]),
    
    # Row 2 (2 columns) -- Food Loss By Commodity and Indicator By Supply Stage
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H1('Food Loss Quantity (g/kg) By Commodity', className='card-title', style={'font-weight': 'bold'}),
                    dcc.Graph(id='food_loss_commodity', className='dbc')
                ]),
            ], style={'padding-left': '20px', 'padding-top': '5px'})
        ),
        
        # Divider or Annotation Here
        html.Div(style={'width': '20px'}),  # Example divider with width
        
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H1("Top 5 Supply Stages With The Highest Food Losses", className='card-title', style={'font-weight': 'bold', 'color': '#343a40'}),
                    html.Span("Compared To The Average Food Lost Quantity By Supply Stage", style={'font-size': '28px'}),
                    dcc.Graph(id='food_loss_supply_stage_indicator', className='dbc'),
                    
                    # Text Block Below the Graph
                    html.P("Do you know the main reasons for food loss?", style={'font-weight': 'bold','font-size': '24px', 'color': 'black'}),
                    html.P(['Food loss refers to the wastage of edible food before it reaches consumers. It occurs due to inefficiencies in various stages of the food supply chain, like:',
                       html.Br(),
                       '- Production: Poor harvesting practices and pest damage result in unharvested or unusable crops.',
                       html.Br(),
                       '- Post-Harvest Handling: Improper storage and transportation lead to spoilage.',
                       html.Br(),
                       '- Processing: Inefficient processing techniques can reduce food quality.',
                       html.Br(),
                       '- Market Factors: Lack of market access or demand causes unsold produce.',
                       html.Br(),
                       '- Consumer Preferences: Rejecting imperfect-looking produce contributes to waste.'], style={'font-size': '22px', 'color': 'black'}),
                    html.Div(html.Img(src=app.get_asset_url('food_text.png'), alt="Food Loss", className="img-fluid mx-auto", style={'width': '30%', 'margin': '10px auto'}),className='text-center')
                ]),
            ], style={'padding-left': '20px', 'padding-top': '5px'})
        ),
    ], style={'margin': '20px'}),
    
    # Row 3 -- Sunburst and Map
    dbc.Row([
        dbc.Col(
            dbc.CardGroup([
                dbc.Card(
                    dbc.CardBody([
                        html.H1('Food Loss Quantity (%)', className='card-title', style={'font-weight': 'bold', 'color': '#343a40'}),
                        dcc.Graph(id='sunburst', className='dbc'),
                        ]),style={'padding-left': '20px', 'padding-top': '5px'}
                    )
                ]),width=6,
            ),
        dbc.Col(
            dbc.CardGroup([
                dbc.Card(
                    dbc.CardBody([
                        html.H1('Food Loss (g/kg) By Country', className='card-title', style={'font-weight': 'bold', 'color': '#343a40'}),
                        dcc.Dropdown(  
                            options=[
                                {'label': 'World', 'value': 'world'},
                                {'label': 'Asia', 'value': 'AS'},
                                {'label': 'Africa', 'value': 'AF'},
                                {'label': 'Europe', 'value': 'EU'},
                                {'label': 'North America', 'value': 'NA'},
                                {'label': 'South America', 'value': 'SA'}
                            ],
                            value='world',
                            id='dropdown_map',
                            style={'font-size': '20px', 'width': '200px'}
                        ),
                        dcc.Graph(id='map', className='dbc',style={'height': '600px'}),
                    ]),
                    style={'padding-left': '20px', 'padding-top': '5px'}
                )
            ]), width=6,
        )
    ], style={'margin': '20px'}),
    
    # Row 4 - Year
    dbc.Row([
        dbc.Col(
            dbc.CardGroup([
                dbc.Card(
                    dbc.CardBody([
                        html.H1('Food Loss (g/kg) By Year', className='card-title',style={'font-weight':'bold','color':'#343a40'}),
                        dcc.RangeSlider(
                            id='year_slider',
                            min=df['year'].min(),
                            max=df['year'].max(),
                            step=1,
                            marks={str(year): {'label': str(year), 'style': {'font-size': '22px'}} for year in range(df['year'].min(), df['year'].max() + 1, 2)},
                            value=[df['year'].min(), df['year'].max()],
                        ),
                        html.Br(),
                        dcc.Graph(id='food_loss_year', className='dbc')
                    ]),
                    style={'padding-left':'18px', 'padding-top':'5px'}
                )
            ]), width=12,
        )
    ], style={'margin':'20px'}),
    
    # Row 5 - Author and Data Source
    dbc.Row([
        dbc.Col(
            dbc.CardGroup([
                dbc.Card(
                    dbc.CardBody([
                        html.H2('Author:',className='card-title',style={'font-weight':'bold','color':'#343a40'}),
                        html.P('Rafael Vieira, e-mail: rafael11934@hotmail.com', style={'color':'black','font-size':'26px'}),
                        html.H2('Data Source', className='card-title',style={'font-weight':'bold', 'color':'#343a40'}),
                        html.A('FAO Food Loss and Waste',href='https://www.fao.org/platform-food-loss-waste/flw-data/en/', style={'color':'black','font-size':'26px'})
                    ]),
                    style={'padding-left':'18px','padding-top':'5px'}
                )
            ])
        )
    ], style={'margin':'20px'})

])


# =========  Functions To Filter the Data  =========== #

# Food Group
def food_group_filter(selected_food_group):
    food_group_mask = df['food group'].isin([selected_food_group])
    return food_group_mask

# Continent
def continent_filter(selected_continent):
    continent_mask = df['continent_code'].isin([selected_continent])
    return continent_mask

# Years
def filter_years(selected_years):
    filtered_df = df[(df['year'] >= selected_years[0]) & (df['year'] <= selected_years[1])]
    return filtered_df

# =========  Callbacks  =========== #

# Commodity - Graph
@app.callback(Output('food_loss_commodity', 'figure'),
              [Input('dropdown_food_group', 'value')])
def commodity(selected_food_group):
    if selected_food_group is None:
        df_filtered = df.copy()  # Display all food groups when no specific group is selected
    else:
        food_group_mask = food_group_filter(selected_food_group)
        df_filtered = df[food_group_mask]

    df1 = df_filtered.groupby('commodity')['loss quantity by 1 kg (g/kg)'].sum().reset_index().sort_values(by='loss quantity by 1 kg (g/kg)', ascending=False).head(10)

    if not df1.empty:
        max_loss_index = df1['loss quantity by 1 kg (g/kg)'].idxmax()
        highest_loss_commodity = df1.loc[max_loss_index, 'commodity']
        highest_loss_quantity = df1.loc[max_loss_index, 'loss quantity by 1 kg (g/kg)']
    else:
        highest_loss_commodity = "N/A"
        highest_loss_quantity = 0

    text_labels = [f'{round(loss, 2)} g/kg' for loss in df1['loss quantity by 1 kg (g/kg)']]
    hover_labels = [f'Commodity: {commodity}<br>Loss Quantity: {loss:.0f} g/kg' for commodity, loss in zip(df1['commodity'], df1['loss quantity by 1 kg (g/kg)'])]

    fig = go.Figure(go.Bar(
        x=df1['loss quantity by 1 kg (g/kg)'],
        y=df1['commodity'],
        orientation='h',
        text=text_labels,
        hovertext=hover_labels,
        marker=dict(color='#966F33')
    ))

    fig.update_layout(
        main_config,
        width=1000,
        height=750,
        template='simple_white',
        annotations=[{
            'x': 1.1,
            'y': 1.15,  # Adjust this value to move the annotation closer to the bottom
            'text': f'<b>Did you know?</b><br>{highest_loss_commodity} has the highest loss quantity,<br>where {highest_loss_quantity:.0f}g put out of 1kg is lost!',
            'showarrow': False,
            'xref': 'paper',
            'yref': 'paper',
            'align': 'center',
            'font': {'size': 20, 'color': 'black'}
        }]
    )
    fig.update_xaxes(title_text='', tickvals=[])
    fig.update_yaxes(tickfont=dict(size=20))
    fig.update_traces(texttemplate='%{text}', textposition='inside', insidetextfont=dict(size=22))

    return fig

#  Food Loss By Supply stage indicator
@app.callback(Output('food_loss_supply_stage_indicator', 'figure'),
              [Input('dropdown_food_group', 'value')])
def food_supply_stage(selected_food_group):
    if selected_food_group is None:
        df_filtered = df.copy()  # Display all food groups when no specific group is selected
    else:
        food_group_mask = food_group_filter(selected_food_group)
        df_filtered = df[food_group_mask]
    
    df2 = df_filtered.groupby('food_supply_stage')['loss quantity by 1 kg (g/kg)'].sum().reset_index().sort_values(by='loss quantity by 1 kg (g/kg)', ascending=False).head(5)
    df3 = df_filtered.groupby('food_supply_stage')['loss quantity by 1 kg (g/kg)'].sum().reset_index().sort_values(by='loss quantity by 1 kg (g/kg)', ascending=True)
    
    indicator_plots = []

    # Iterate through stages and loss quantities to create indicators
    for stage, loss_quantity in zip(df2['food_supply_stage'], df2['loss quantity by 1 kg (g/kg)']):
        indicator = go.Indicator(
            mode="number+delta",
            value=loss_quantity,
            delta={'reference': df3['loss quantity by 1 kg (g/kg)'].mean(), 'relative': True, 'valueformat': '.1%', 'font': {'size': 24}},  
            domain={'row': 0, 'column': df2['food_supply_stage'].tolist().index(stage)},
            title={'text': f"<span style='font-size:22px; color: #9c6666a; font-weight: bold;'>{stage}</span>"},
            number={'font': {'size': 26, 'color': '#343a40'}},
            gauge={'axis': {'visible': False}},
        )
        indicator_plots.append(indicator)

    # Create a subplot containing the indicator plots
    fig_indicator = go.Figure(
        data=indicator_plots,
        layout=go.Layout(
            grid={'rows': 1, 'columns': len(df2)},
            template={'data': {'indicator': [{'number': {'suffix': " g/kg"}}]}},
            height=200,
            width=1135,
            margin={'l': 40, 'r': 40, 'b': 20, 't': 20},  # Add margins for spacing
            showlegend=False,
            xaxis={'showticklabels': False, 'showgrid': False},
            yaxis={'showticklabels': False, 'showgrid': False},
            paper_bgcolor='white',
            plot_bgcolor='rgba(240, 240, 240, 0.7)')
    )
    return fig_indicator

# Sunbusrt
@app.callback(Output('sunburst', 'figure'),
              [Input('dropdown_food_group', 'value')])
def food_supply_stage(selected_food_group):
    if selected_food_group is None:
        df_filtered = df.copy()  # Display all food groups when no specific group is selected
    else:
        food_group_mask = food_group_filter(selected_food_group)
        df_filtered = df[food_group_mask]
        
    sunburst = px.sunburst(df_filtered,
                 path=['food group','commodity'],
                 values = 'loss quantity by 1 kg (g/kg)',
                 color='food group',
                 color_discrete_sequence = px.colors.qualitative.Antique,
                 maxdepth=2)

    sunburst.update_traces(textinfo='label+percent entry')

    sunburst.update_layout(
        main_config,
        width=1100,
        height=850,
        font=dict(size=24),  
        template='simple_white')
    
    return sunburst
    
# Map
@app.callback(
    Output('map', 'figure'),
    [Input('dropdown_map', 'value')]
)
def commodity(selected_continent):
    fig = None  

    if selected_continent == 'world' or selected_continent is None:
        df_filtered = df.copy()
        df4 = df_filtered.groupby(['country', 'country_code_iso'])['loss quantity by 1 kg (g/kg)'].sum().reset_index()
        fig = px.choropleth(
            df4,
            locations='country_code_iso',
            locationmode='ISO-3',
            color='loss quantity by 1 kg (g/kg)',
            scope='world',
            hover_name='country',
            color_continuous_scale='brwnyl')
        fig.update_traces(hovertemplate='<b>%{hovertext}</b><br>' +
                                  'Country: %{hovertext}<br>' +
                                  'Loss Quantity: %{z:.1f} g/kg')
        fig.update_layout(main_config,template='simple_white',width=1100, height=600)
        fig.update_layout(coloraxis_colorbar={'len': 0.8,  # Adjust the color bar length
                                      'thickness': 40,  # Adjust the color bar thickness
                                      'title': 'Loss Quantity (g/kg)',  # Adjust the color bar title
                                      'title_side': 'top', 
                                      'title_font': {'size': 22},  # Increase color bar title font size
                                      'tickfont': {'size': 20} # Place the title at the top
                                      })
        
    elif selected_continent == 'AS':
        asia = df[df['continent_code']=='AS']
        df6 = asia.groupby(['country','country_code_iso'])['loss quantity by 1 kg (g/kg)'].sum().reset_index()
        fig = px.choropleth(
            df6,
            locations='country_code_iso',
            locationmode='ISO-3',
            color='loss quantity by 1 kg (g/kg)',
            scope='asia',
            hover_name='country',
            color_continuous_scale='brwnyl')
        fig.update_traces(hovertemplate='<b>%{hovertext}</b><br>' +
                                                        'Country: %{hovertext}<br>' +
                                                        'Loss Quantity: %{z:.1f} g/kg')
        fig.update_layout(main_config,template='simple_white',width=1100, height=600)
        fig.update_layout(coloraxis_colorbar={'len': 0.8,  # Adjust the color bar length
                                      'thickness': 40,  # Adjust the color bar thickness
                                      'title': 'Loss Quantity (g/kg)',  # Adjust the color bar title
                                      'title_side': 'top', 
                                      'title_font': {'size': 22},  # Increase color bar title font size
                                      'tickfont': {'size': 20} # Place the title at the top
                                      })
        
    elif selected_continent == 'AF':
        africa = df[df['continent_code']=='AF']
        df7 = africa.groupby(['country','country_code_iso'])['loss quantity by 1 kg (g/kg)'].sum().reset_index()
        fig = px.choropleth(
            df7,
            locations='country_code_iso',
            locationmode='ISO-3',
            color='loss quantity by 1 kg (g/kg)',
            scope='africa',
            hover_name='country',
            color_continuous_scale='brwnyl')
        fig.update_traces(hovertemplate='<b>%{hovertext}</b><br>' +
                                  'Country: %{hovertext}<br>' +
                                  'Loss Quantity: %{z:.1f} g/kg')
        fig.update_layout(main_config,template='simple_white',width=1100, height=600)
        fig.update_layout(coloraxis_colorbar={'len': 0.8,  # Adjust the color bar length
                                      'thickness': 40,  # Adjust the color bar thickness
                                      'title': 'Loss Quantity (g/kg)',  # Adjust the color bar title
                                      'title_side': 'top', 
                                      'title_font': {'size': 22},  # Increase color bar title font size
                                      'tickfont': {'size': 20} # Place the title at the top
                                      })
    elif selected_continent == 'EU':
        europe = df[df['continent_code']=='EU']
        df5 = europe.groupby(['country','country_code_iso'])['loss quantity by 1 kg (g/kg)'].sum().reset_index()
        fig = px.choropleth(
            df5,
            locations='country_code_iso',
            locationmode='ISO-3',
            color='loss quantity by 1 kg (g/kg)',
            scope='europe',
            hover_name='country',
            color_continuous_scale='brwnyl')
        fig.update_traces(hovertemplate='<b>%{hovertext}</b><br>' +
                                  'Country: %{hovertext}<br>' +
                                  'Loss Quantity: %{z:.1f} g/kg')
        fig.update_layout(main_config,template='simple_white',width=1100, height=600)
        fig.update_layout(coloraxis_colorbar={'len': 0.8,  # Adjust the color bar length
                                      'thickness': 40,  # Adjust the color bar thickness
                                      'title': 'Loss Quantity (g/kg)',  # Adjust the color bar title
                                      'title_side': 'top', 
                                      'title_font': {'size': 22},  # Increase color bar title font size
                                      'tickfont': {'size': 20} # Place the title at the top
                                      })
        
    elif selected_continent == 'SA':
        sa = df[df['continent_code']=='SA']
        df8 = sa.groupby(['country','country_code_iso'])['loss quantity by 1 kg (g/kg)'].sum().reset_index()
        fig = px.choropleth(
            df8,
            locations='country_code_iso',
            locationmode='ISO-3',
            color='loss quantity by 1 kg (g/kg)',
            scope='south america',
            hover_name='country',
            color_continuous_scale='brwnyl')
        fig.update_traces(hovertemplate='<b>%{hovertext}</b><br>' +
                                  'Country: %{hovertext}<br>' +
                                  'Loss Quantity: %{z:.1f} g/kg')
        fig.update_layout(main_config,template='simple_white',width=1100, height=600)
        fig.update_layout(coloraxis_colorbar={'len': 0.8,  # Adjust the color bar length
                                      'thickness': 40,  # Adjust the color bar thickness
                                      'title': 'Loss Quantity (g/kg)',  # Adjust the color bar title
                                      'title_side': 'top', 
                                      'title_font': {'size': 22},  # Increase color bar title font size
                                      'tickfont': {'size': 20} # Place the title at the top
                                      })
        
    elif selected_continent == 'NA':
        no = df[df['continent_code']=='NA']
        df9 = no.groupby(['country','country_code_iso'])['loss quantity by 1 kg (g/kg)'].sum().reset_index()
        fig = px.choropleth(
            df9,
            locations='country_code_iso',
            locationmode='ISO-3',
            color='loss quantity by 1 kg (g/kg)',
            scope='north america',
            hover_name='country',
            color_continuous_scale='brwnyl')
        fig.update_traces(hovertemplate='<b>%{hovertext}</b><br>' +
                                        'Country: %{hovertext}<br>' +
                                        'Loss Quantity: %{z:.1f} g/kg')
        fig.update_layout(main_config,template='simple_white',width=1100, height=600)
        fig.update_layout(coloraxis_colorbar={'len': 0.8,  # Adjust the color bar length
                                      'thickness': 40,  # Adjust the color bar thickness
                                      'title': 'Loss Quantity (g/kg)',  # Adjust the color bar title
                                      'title_side': 'top', 
                                      'title_font': {'size': 22},  # Increase color bar title font size
                                      'tickfont': {'size': 20} # Place the title at the top
                                      })
        
    return fig  

# Food Loss - Year
@app.callback(Output('food_loss_year','figure'),
              [Input('year_slider','value')])
def food_loss_year(selected_years):
    year_df_filtered = filter_years(selected_years)
    df11 = year_df_filtered.groupby('year')['loss quantity by 1 kg (g/kg)'].sum().reset_index()
    by_year = go.Figure(go.Scatter(
        x=df11['year'],
        y=df11['loss quantity by 1 kg (g/kg)'],
        mode='lines',
        line=dict(color='#966F33'),
        fill='tonexty',
        hovertext=[f'Year: {year}<br>Average Price: {loss:.2f} g/kg' for year, loss in zip(df11['year'], df11['loss quantity by 1 kg (g/kg)'])]
    ))
    by_year.update_layout(
        main_config,
        width=2325,
        height=550,
        template='simple_white')
    by_year.update_yaxes(title_text='Food Loss (g/kg)', title_font={'size': 26},
                         tickfont=dict(size=24))
    by_year.update_xaxes(tickfont=dict(size=24))
    
    return by_year
        