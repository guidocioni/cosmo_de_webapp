import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from utils import b64_image, get_run
from plotting import plot_vars
import os
from dash_extensions import Keyboard

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Processing to do when app is launched goes here 
dropdown_options = [{'label':'Geopotential@500 T@850', 'value':'gph_t_850'}]
projection_options = [{'label':'Northern germany', 'value':'nord'},
                      {'label':'Italy', 'value':'it'},
                      {'label':'Germany', 'value':'de'}]
steps = list(range(0, 28))
run_string, _ = get_run()
#

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
  url_base_pathname='/cosmo-de/')
server = app.server

app.layout = html.Div([
    html.H1("COSMO-DE forecasts"),
    html.Div([dcc.Dropdown(id='chart-dropdown',
                 options=dropdown_options, value='gph_t_850',
                 style=dict(width='40%', verticalAlign="middle")
                 ),
    dcc.Dropdown(id='proj-dropdown',
                 options=projection_options, value='de',
                 style=dict(width='40%', verticalAlign="middle")
                 )],style={'float': 'left', 'width': '100%'}),
    html.Br(),
    html.Div([html.Div([html.Button('Preload', id='preload', n_clicks=0),
        html.P('Forecast lead time'), html.Div(dcc.Slider(id='slider-step', min=0, max=27, value=0,
                               marks={i: i for i in steps}, step=None,
                              tooltip={'always_visible': True}))], style={'float': 'left', 'width': '100%'})]),
    html.Div(html.Img(id="image_plt"), style={'textAlign': 'center'}),
    html.Div(dcc.Loading(fullscreen=True, id="loading", type="default", children=html.P(''))),
    Keyboard(id="keyboard"),
])

# @app.callback(Output(component_id='slider-step', component_property='value'), 
#   [Input("keyboard", "keydown"), Input("slider-step", "value")])
# def update_slider_keyup(event, slider_value):
#   out = 0
#   key_pressed = event['key']
#   if key_pressed == "ArrowRight":
#     if slider_value == max(steps):
#       out = steps[0]
#     else:
#       out = slider_value + 1 
#   elif key_pressed == "ArrowLeft":
#     if slider_value == min(steps):
#       out = steps[-1]
#     else:
#       out = slider_value - 1

#   return out

@app.callback(
    Output('image_plt', 'src'),
    [Input('chart-dropdown', 'value'), Input('slider-step', 'value'), Input('proj-dropdown', 'value')])
def update_figure(chart, f_step, projection):
  filename = '/tmp/' + projection + '_' + chart + '_%s_%03d.png' % (run_string, f_step)

  if os.path.exists(filename):
    out = b64_image(filename)
  else:
    filename_fig = plot_vars(f_step, projection, load_all=False)
    assert filename_fig == filename, "Mismatching filename strings! From plot_vars:%s , defined:%s" % (filename_fig, filename)
    out = b64_image(filename_fig)

  return out

@app.callback(
    Output('loading', 'children'),
    [Input('preload','n_clicks')],
    state=[State('chart-dropdown', 'value'), State('proj-dropdown', 'value')])
def update_output(n_clicks, chart, projection):
    if n_clicks > 1:
      f_steps = list(range(0, 79)) + list(range(81, 121, 3))
      filenames = ['/tmp/' + projection + '_' + chart + '_%s_%03d.png' % (run_string, f_step) for f_step in f_steps]
      test_filenames = [os.path.exists(f) for f in filenames]

      if all(test_filenames): # means the files already exist
        return None
      else:
        none = plot_vars(f_steps, projection, load_all=True)
        return None

if __name__ == '__main__':
    app.run_server(debug=True)
