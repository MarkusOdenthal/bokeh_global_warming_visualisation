# lib for data preprocessing
import pandas as pd
import numpy as np
from datetime import date

# basic plotting
from bokeh.models import ColumnDataSource
from bokeh.io import curdoc

# Geo mapping
from bokeh.plotting import gmap
from bokeh.models import GMapOptions

# color patches
from bokeh.models import LinearColorMapper, ColorBar
from bokeh.colors import RGB
from matplotlib import cm

# widgetbox for the app
from bokeh.layouts import widgetbox, column
from bokeh.models import DateSlider


# read input data
climate_data = pd.read_csv('ghcn-m-v1.csv')
climate_data['date'] = climate_data['year'].astype('str') + '-' + climate_data['month'].astype('str')
climate_data['date'] = pd.to_datetime(climate_data['date'], format='%Y-%m')
climate_data = climate_data.set_index(['date'])
climate_data.drop(['year', 'month'], axis=1, inplace=True)
climate_data = climate_data.replace(-9999, 0)

# data processing for input data
xs_column_a = np.arange(-175, 175, 5)
xs_column_b = np.arange(-170, 180, 5)
xs = np.column_stack((xs_column_a, xs_column_a, xs_column_b, xs_column_b))
xs = np.repeat(xs, 34, axis=0)
xs = xs.tolist()

ys_column_a = np.arange(-80, 90, 5)
ys_column_b = np.arange(-85, 85, 5)
ys = np.column_stack((ys_column_a, ys_column_b, ys_column_b, ys_column_a))
ys = np.tile(ys, (70, 1))
ys = ys.tolist()

# Make the ColumnDataSource: source
source = ColumnDataSource(data={
    'x': xs,
    'y': ys,
    'temp_anomalies': (climate_data.loc[date(1980, 1, 1)].iloc[1:-1, 2:-1].values.reshape(-1, 1)) / 100,
})


# Define the callback function: update_plot
def update_plot(attr, old, new):
    # set the `yr` name to `slider.value` and `source.data = new_data`
    slider_value = slider.value
    year = slider_value.year
    month = slider_value.month
    new_data = {
        'x': xs,
        'y': ys,
        'temp_anomalies': (climate_data.loc[date(year, month, 1)].iloc[1:-1,2:-1].values.reshape(-1,1))/100,
    }
    source.data = new_data


# create the plot
m_coolwarm_rgb = (255 * cm.coolwarm(range(256))).astype('int')
coolwarm_palette = [RGB(*tuple(rgb)).to_hex() for rgb in m_coolwarm_rgb]
color_mapper = LinearColorMapper(palette=coolwarm_palette, low=-2, high=2)

map_options = GMapOptions(lat=38.733680, lng=-9.173207, map_type="roadmap", zoom=3)
p = gmap("API-KEy",
         map_options, title='Temperature anomalies from 1800-2016', plot_width=1200, plot_height=700)

p.patches('x', 'y', source=source,
          fill_color={'field': 'temp_anomalies', 'transform': color_mapper},
          fill_alpha=0.5, line_color=None)

color_bar = ColorBar(color_mapper=color_mapper,
                     label_standoff=12, border_line_color=None, location=(0,0))
p.add_layout(color_bar, 'right')

# Make a slider object: slider
slider = DateSlider(title="Date", value=min(climate_data.index), start=min(climate_data.index),
                    end=max(climate_data.index), step=1, width=900)

# Attach the callback to the 'value' property of slider
slider.on_change('value', update_plot)

# Make a row layout of widgetbox(slider) and plot and add it to the current document
layout = column(widgetbox(slider, sizing_mode='scale_width'), p)

# Add the plot to the current document and add a title
curdoc().add_root(layout)
curdoc().title = 'Global Warming'
