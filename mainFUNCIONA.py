''' Create a simple stocks correlation dashboard.
Choose stocks to compare in the drop down widgets, and make selections
on the plots to update the summary and histograms accordingly.
.. note::
    Running this example requires downloading sample data. See
    the included `README`_ for more information.
Use the ``bokeh serve`` command to run the example by executing:
    bokeh serve stocks
at your command prompt. Then navigate to the URL
    http://localhost:5006/stocks
.. _README: https://github.com/bokeh/bokeh/blob/master/examples/app/stocks/README.md
'''
from functools import lru_cache
from os.path import dirname, join

import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, PreText, Select
from bokeh.plotting import figure

DATA_DIR = join(dirname(__file__), 'daily')

# Etiquetas para el menú desplegable
DEFAULT_TICKERS = ['AAPL', 'GOOG', 'INTC', 'BRCM', 'YHOO']

"""
DEFAULT_TICKERS = []
Orgeval = pd.read_csv('AllData-Nehuen.csv')
for cols in Orgeval:
    DEFAULT_TICKERS.append(cols)
"""
def nix(val, lst):
    return [x for x in lst if x != val]

# ESTE ES EL QUE HAY QUE MODIFICAR PARA QUE BUSQUE LA DATA QUE QUIERO YO (DEFAULT_TICKERS TIENE QUE ESTAR MODIFICADO ANTES)
"""
@lru_cache()
def load_ticker(ticker):
    data = pd.read_csv('AllData-Nehuen.csv')
    data = data.set_index('date')
    return pd.DataFrame({ticker: data[ticker]})
"""

@lru_cache()
def load_ticker(ticker):
    fname = join(DATA_DIR, 'table_%s.csv' % ticker.lower())
    data = pd.read_csv(fname, header=None, parse_dates=['date'],
                       names=['date', 'foo', 'o', 'h', 'l', 'c', 'v'])
    data = data.set_index('date')
    return pd.DataFrame({ticker: data.c}) # Tengo que referenciar el nombre de la columna
    # , ticker+'_returns': data.c.diff()})

@lru_cache()
def get_data(t1, t2):
    df1 = load_ticker(t1)
    df2 = load_ticker(t2)
    data = pd.concat([df1, df2], axis=1)
    data = data.dropna()
    data['t1'] = data[t1]
    data['t2'] = data[t2]
    # data['t1_returns'] = data[t1+'_returns']
    # data['t2_returns'] = data[t2+'_returns']
    return data

# set up widgets

# Estos tienen que coincidir con lo que haya en DEFAULT_TICKERS
stats = PreText(text='', width=250)
ticker1 = Select(value='AAPL', options=nix('GOOG', DEFAULT_TICKERS)) # Premier menú desplegable AAPL por defecto
ticker2 = Select(value='GOOG', options=nix('AAPL', DEFAULT_TICKERS)) # Segundo menú desplegable GOOG por defecto

# set up plots

# De acá saca las columnas para plotear el scatter plot
source = ColumnDataSource(data=dict(date=[], t1=[], t2=[]))
# , t1_returns=[], t2_returns=[]))

# De acá saca las columnas para plotear las curbas de abajo
source_static = ColumnDataSource(data=dict(date=[], t1=[], t2=[]))
# , t1_returns=[], t2_returns=[]))
tools = 'pan,wheel_zoom,xbox_select,reset'


# Esto es el scatter plot
corr = figure(plot_width=600, plot_height=400,
              tools='pan,wheel_zoom,box_select,reset')
corr.circle('t1', 't2', size=2, source=source,
             selection_color="orange", alpha=0.6, nonselection_alpha=0.1, selection_alpha=0.4)


# Curva número 1

ts1 = figure(plot_width=1300, plot_height=200, tools=tools, x_axis_type='datetime', active_drag="xbox_select")
ts1.line('date', 't1', source=source_static)
ts1.circle('date', 't1', size=1, source=source, color=None, selection_color="orange")

# Curva número 2

ts2 = figure(plot_width=1300, plot_height=200, tools=tools, x_axis_type='datetime', active_drag="xbox_select")
ts2.x_range = ts1.x_range
ts2.line('date', 't2', source=source_static)
ts2.circle('date', 't2', size=1, source=source, color=None, selection_color="orange")

# set up callbacks

def ticker1_change(attrname, old, new):
    ticker2.options = nix(new, DEFAULT_TICKERS)
    update()

def ticker2_change(attrname, old, new):
    ticker1.options = nix(new, DEFAULT_TICKERS)
    update()

def update(selected=None):
    t1, t2 = ticker1.value, ticker2.value

    df = get_data(t1, t2)
    data = df[['t1', 't2']]
    # , 't1_returns', 't2_returns']]
    source.data = data
    source_static.data = data

    update_stats(df, t1, t2)

    # corr.title.text = '%s returns vs. %s returns' % (t1, t2)
    ts1.title.text, ts2.title.text = t1, t2

def update_stats(data, t1, t2):
    stats.text = str(data[[t1, t2]].describe())
    # , t1+'_returns', t2+'_returns']].describe())

ticker1.on_change('value', ticker1_change)
ticker2.on_change('value', ticker2_change)

def selection_change(attrname, old, new):
    t1, t2 = ticker1.value, ticker2.value
    data = get_data(t1, t2)
    selected = source.selected.indices
    if selected:
        data = data.iloc[selected, :]
    update_stats(data, t1, t2)

source.selected.on_change('indices', selection_change)

# set up layout
widgets = column(ticker1, ticker2, stats)
main_row = row(corr, widgets)
series = column(ts1, ts2)
layout = column(main_row, series)

# initialize
update()

curdoc().add_root(layout)
curdoc().title = "Orgeval baby"
