"""
Script that gets the coordinates of locations and plots them in three different styles (folium, geopandas, plotly). 
"""
# base tools
import os
import pandas as pd
from tqdm import tqdm
import argparse

# geocoding tools
from functools import partial
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# plotting tools
import folium
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
import geopandas as gpd
import plotly.express as px


def parse_args():
    '''
    Function that specifies the available arguments.
    '''
    ap = argparse.ArgumentParser()
    
    # command line parameters
    ap.add_argument("-f", "--file_input", required = False, default = os.path.join('data', 'csv', 'loc_count.csv'), help = "The CSV file we want to work with") 
    ap.add_argument("-p", "--plot", required = False, type = bool, default = 0, help = "Run only the plotting? This requires that the geocode CSV has already been created.")
        
    args = vars(ap.parse_args())
    return args


def read_data(file):
    '''
    Function that reads a CSV file into a pandas dataframe.
    
    file: path to a CSV file
    '''
    filepath = os.path.join(file)
    df = pd.read_csv(filepath)
    
    return df

def geocode(df):
    '''
    Function that finds and saves the coordinates of locations. The results are saved in the 'csv' folder.
    
    df: dataframe that has a column named 'loc' containing locations. 
    '''
    # initiate progress bar
    tqdm.pandas()
    
    # create geolocator objects and insert mandatory delay between queries
    geolocator = Nominatim(user_agent="ibsen_locations")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    # apply geocode function and return english results
    df['location'] = df['loc'].progress_apply(partial(geocode, language='en'))

    # add coordinates as separate column to dataframe
    df['point'] = df['location'].apply(lambda loc: tuple(loc.point) if loc else None) 
    
    # split the 'point' column and save the results
    df['point'] = df['point'].astype('string')
    df[['lat', 'long', 'x']] = df['point'].str.split(',', expand=True)
    df['lat'] = df['lat'].str.replace('(', '', regex=False)

    path = os.path.join('data', 'csv', 'loc_coordinates.csv')
    df.to_csv(path, index = False)
    return df


def format_df(df):
    '''
    Function that alters the type of the values in the columns for the plotting.
    
    df: a dataframe containing lat, long and count columns.
    '''
    df = df.dropna(subset=['lat', 'long'])
    convert_dict = {'lat': float,
                    'long': float,
                    'count' : float}
  
    df = df.astype(convert_dict)
    return df


def folium_plot(df):
    '''
    Function that generates a plot with the Folium package and saves it as an interactive html file.
    
    df: a dataframe containing loc, lat, long and count columns.
    '''
    world_map= folium.Map(tiles="cartodbpositron")
    marker_cluster = MarkerCluster().add_to(world_map)

    #for each coordinate create circlemarker
    for i in range(len(df)):
            lat = df.iloc[i]['lat']
            long = df.iloc[i]['long']
            radius= df.iloc[i]['count']
            popup_text = """Location: {}<br>
                            Count: {}<br>"""
            popup_text = popup_text.format(df.iloc[i]['loc'],
                                       df.iloc[i]['count'])
            folium.CircleMarker(location = [lat, long], radius=radius, popup= popup_text, fill = True).add_to(marker_cluster)

    # saving the map created
    world_map.save('output/folium_plot.html')
    return


def geopandas_plot(df):
    '''
    Function that creates a world sized plot with the GeoPandas package and saves it.
    
    df: a dataframe containing lat, long and count columns.
    '''
    # From GeoPandas, load world map
    worldmap = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

    # Creating axes and plotting world map
    fig, ax = plt.subplots(figsize=(20, 10))
    worldmap.plot(color="lightgrey", ax=ax)

    # Plotting data with a color map
    x = df['long']
    y = df['lat']
    z = df['count']
    plt.scatter(x, y, s=z, c=z, alpha=0.6, vmin=0, 
                cmap='autumn')
    plt.colorbar(label='count')

    # Creating axis limits and title
    plt.xlim([-150, 180])
    plt.ylim([-60, 90])

    plt.title("Henrik Ibsen - locations from his letters by count")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    
    plt.savefig(f'output/geopandas_world.jpg', bbox_inches='tight')
    return


def geopandas_plot_sm(df):
    '''
    Function that creates a Europe sized plot with the GeoPandas package and saves it.
    
    df: a dataframe containing lat, long and count columns.
    '''
    # From GeoPandas
    worldmap = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    # Filtering Europe
    europemap = worldmap.loc[worldmap['continent'] == 'Europe']
    
    # Creating axes and plotting world map
    fig, ax = plt.subplots(figsize=(20, 10))
    europemap.plot(color="lightgrey", ax=ax)

    # Plotting our data with a color map
    x = df['long']
    y = df['lat']
    z = df['count']
    plt.scatter(x, y, s=z, c=z, alpha=0.6, vmin=0, 
                cmap='autumn')
    plt.colorbar(label='count')

    # Creating axis limits and title
    plt.xlim([-20, 35])
    plt.ylim([35, 73])

    plt.title("Henrik Ibsen - locations from his letters by count")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    
    plt.savefig(f'output/geopandas_europe.jpg', bbox_inches='tight')
    return


def plotly_plot(df):
    '''
    Function that creates a plot with the Plotly package. Both a static and interactive version is saved. 
    
    df: a dataframe containing loc, lat, long and count columns.
    '''
    fig = px.scatter_mapbox(df, 
                            lat="lat", lon="long", color="count", size="count",
                            color_continuous_scale = px.colors.cyclical.IceFire,
                            size_max=15,
                            zoom=2,
                            hover_name = df["loc"],
                      mapbox_style="carto-positron")
    
    # saving the plot as both static and interactive
    fig.write_image(f'output/plotly_europe.png')
    fig.write_html(f'output/plotly_world.html')
    return


def main():
    '''
    The process of the script from the geocoding or from the plotting. 
    '''
    # parse argument
    args = parse_args()
    p_only = args['plot']
    
    if p_only == False:
        print('[INFO] Geocoding locations ...')
        
        df = read_data(args['file_input'])
        geocode(df)
        
        print('[INFO] Geocoding done')
        print('[INFO] Plotting results')
        
        df = read_data(file = 'loc_coordinates.csv')
        df = format_df(df)
        
        folium_plot(df)
        geopandas_plot(df)
        geopandas_plot_sm(df)
        plotly_plot(df)
        
        print('[INFO] Script success')

    if p_only == True:
        print('[INFO] Plotting results ONLY')
        file_path = os.path.join('data', 'csv', 'loc_coordinates.csv')
        df = read_data(file = file_path)
        df = format_df(df)
        
        folium_plot(df)
        geopandas_plot(df)
        geopandas_plot_sm(df)
        plotly_plot(df)
        
        print('[INFO] Script success')   
    return


if __name__ == '__main__':
    main()