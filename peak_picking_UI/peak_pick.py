import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from dash import dcc, html

class plot_NMR_spec:
    def __init__(self, spectra, ppm):
        self.spectra = spectra
        self.ppm = ppm


    def single_spectra(self, color_map=None, 
                        title='<b>Spectra of <sup>1</sup>H NMR data</b>', title_font_size=28, 
                        legend_name='<b>Group</b>', legend_font_size=20, 
                        axis_font_size=20, 
                        fig_height = 600, fig_width = 1200,
                        line_width = 1.5, legend_order=None):

        from plotly import express as px

        spectra = self.spectra
        ppm = self.ppm

        
        df_spectra = pd.DataFrame(spectra)
        df_spectra.columns = ppm

        if color_map is None:
            color_map = dict(zip(df_spectra.index, px.colors.qualitative.Plotly))
        else:
            if len(color_map) != len(df_spectra.index):
                raise ValueError('Color map must have the same length as group labels')

        fig = go.Figure()
        for i in df_spectra.index:
            fig.add_trace(go.Scatter(x=ppm, y=df_spectra.loc[i,:], mode='lines', name=i, line=dict(width=line_width)))

        fig.update_layout(
            autosize=False,
            width=fig_width,
            height=fig_height,
            margin=dict(l=50, r=50, b=100, t=100, pad=4)
        )

        fig.update_xaxes(showline=True, showgrid=False, linewidth=1, linecolor='rgb(82, 82, 82)', mirror=True)
        fig.update_yaxes(showline=True, showgrid=False, linewidth=1, linecolor='rgb(82, 82, 82)', mirror=True)

        fig.update_layout(
            font=go.layout.Font(size=axis_font_size),
            title={'text': title, 'xanchor': 'center', 'yanchor': 'top'},
            title_x=0.5,
            xaxis_title="<b>δ<sup>1</sup>H</b>", yaxis_title="<b>Intensity</b>",
            title_font_size=title_font_size,
            title_yanchor="top",
            title_xanchor="center",
            legend=dict(title=legend_name, font=dict(size=legend_font_size)),
            xaxis_autorange="reversed",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(tickformat=".2e")
        )

        return fig

# Generate sample NMR data
x = np.linspace(0, 10, 1000)
y = np.exp(-0.5 * ((x - 5)**2) / (0.2**2)) + np.random.normal(0, 0.02, x.size)
spectra = pd.DataFrame(y).T
ppm = x


# Instantiate the class
plotter = plot_NMR_spec(spectra, ppm)

# Create the Dash app
app = dash.Dash(__name__)

# Layout for the app
app.layout = html.Div([
    dcc.Graph(
        id='nmr-plot',
        figure=plotter.single_spectra()
    ),
    html.Div(id='peak-data', children='Click on the plot to select peaks.'),
    dcc.Store(id='stored-peaks', data=[]),
    html.Button("Export X Positions", id="export-button"),
    dcc.Download(id="download-dataframe-csv")
])

@app.callback(
    Output('stored-peaks', 'data'),
    Output('peak-data', 'children'),
    Input('nmr-plot', 'clickData'),
    State('stored-peaks', 'data')
)
def update_peaks(clickData, stored_peaks):
    if clickData is None:
        return stored_peaks, 'Click on the plot to select peaks.'
    
    click_point = clickData['points'][0]
    x_peak = click_point['x']
    y_peak = click_point['y']
    
    stored_peaks.append({'x': x_peak, 'y': y_peak})
    peak_text = f'Picked peaks (X, Y): {[(p["x"], p["y"]) for p in stored_peaks]}'
    
    return stored_peaks, peak_text

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("export-button", "n_clicks"),
    State("stored-peaks", "data"),
    prevent_initial_call=True
)
def export_x_positions(n_clicks, stored_peaks):
    if not stored_peaks:
        return dash.no_update

    x_positions = [p['x'] for p in stored_peaks]
    df = pd.DataFrame(x_positions, columns=["X Positions"])
    csv_string = df.to_csv(index=False)
    
    return dict(content=csv_string, filename="x_positions.csv")

if __name__ == '__main__':
    app.run_server(debug=True)