import pandas as pd
import numpy as np
import pysal.esda.mapclassify as mapclassify
import sys
import os
from mapboxgl.viz import *
from mapboxgl.utils import *
from mapboxgl.colors import *
import plotly.offline as py_off
from plotly.graph_objs import *
import mapbox
import geojson
from plotly.graph_objs import *
import config 

def df_to_geojson(df, properties, lat='Lat', lon='Lon'):
    """
    Turn a dataframe containing point data into a geojson formatted python dictionary

    df : the dataframe to convert to geojson
    properties : a list of columns in the dataframe to turn into geojson feature properties
    lat : the name of the column in the dataframe that contains latitude data
    lon : the name of the column in the dataframe that contains longitude data
    """

    # create a new python dict to contain our geojson data, using geojson format
    geojson = {'type':'FeatureCollection', 'features':[]}

    # loop through each row in the dataframe and convert each row to geojson format
    for _, row in df.iterrows():
        # create a feature template to fill in
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':{'type':'Point',
                               'coordinates':[]}}

        # fill in the coordinates
        feature['geometry']['coordinates'] = [row[lon],row[lat]]

        # for each column, get the value and add it as a new feature property
        for prop in properties:
            feature['properties'][prop] = row[prop]

        # add this feature (aka, converted dataframe row) to the list of features inside our dict
        geojson['features'].append(feature)
    return geojson

def max_wineries(df,num_vineyards):
    '''
    find the fastest route the vineyards
    '''
    vineyards = []
    time = []
    current = 'Home'
    while len(vineyards)<num_vineyards:
        if current not in vineyards and not 'Home':
            print(current)
            spot = df[current].sort_values().index[1]
            current = spot
            time.append(df[current].sort_values()[1])
            vineyards.append(current)
        else:
            for i,index in enumerate(df[current].sort_values().index[1:]):
                if index not in vineyards and index !='Home':
                    time.append(df[current].sort_values()[1:][i])
                    vineyards.append(index)
                    current=index
                    break
    return vineyards,time

def drop_vineyard():
    '''
    drop vineyard from dataframe
    '''


def trip(df):
    token = config.plotly_key
    directions_api = mapbox.Directions(access_token=token)
    df_tour['Winery']=df_tour.index
    feat = df_to_geojson(df_tour,properties=['Winery'])
    feat['features'].append({'geometry': {'coordinates': [ -121.945778,37.281630],
        'type': 'Point'},
       'properties': {'Winery': 'Home'},
       'type': 'Feature'})
    res = directions_api.directions(feat['features'])

    data = Data([
            Scattermapbox(
                lat=[item_x[1] for item_x in res.geojson()['features'][0]['geometry']['coordinates']],
                lon=[item_y[0] for item_y in res.geojson()['features'][0]['geometry']['coordinates']],
                mode='markers+lines',
                marker=Marker(
                    size=3
                ),
            ),
            (Scattermapbox(
            lon=df_tour['Lon'],
            lat=df_tour['Lat'],
            mode='markers',
            hoverinfo='text',
            marker=Marker(
                color='purple',size=12
            ),text=df_tour['Winery'],name='Stops'))
        ])
    layout = Layout(
        margin=dict(t=0,b=0,r=0,l=0),
        autosize=True,
        hovermode='closest',
        showlegend=False,
        mapbox=dict(
            accesstoken=token,
            bearing=0,
            center=dict(
                lat=37,
                lon=-122
            ),
            pitch=0,
            zoom=8,
            style='outdoors'
        ),
    )

    fig = dict(data=data, layout=layout)
    py_off.plot(fig, filename='tour.html')
