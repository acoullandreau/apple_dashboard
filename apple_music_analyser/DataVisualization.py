import plotly.graph_objs as go
from plotly.subplots import make_subplots

from apple_music_analyser.Utility import Utility

class SunburstVisualization():

    def __init__(self, viz_dict, center_title=''):
        self.viz_dict = viz_dict
        self.center_title = center_title
        self.plot_title = 'Ranking across years: ' + self.center_title
        self.labels = []
        self.parents = []
        self.values = []
        self.ids = []
        self.build_sunburst_arrays()

    def build_sunburst_arrays(self):
        labels = []
        parents = []
        values = []
        ids = []
        for year in self.viz_dict.keys():
            current_index = len(labels)
            ids.append(str(year))
            labels.append(str(year))
            parents.append(self.center_title)
            total_count = 0
            for genre in self.viz_dict[year].keys():
                ids.append(str(year)+' - '+genre)
                labels.append(genre)
                parents.append(str(year))
                values.append(self.viz_dict[year][genre])
                total_count += self.viz_dict[year][genre]
            values.insert(current_index, total_count)

        self.labels = labels
        self.parents = parents
        self.values = values
        self.ids = ids

    def render_sunburst_plot(self):
        fig =go.Figure(go.Sunburst(
            ids=self.ids,
            labels=self.labels,
            parents=self.parents,
            values=self.values,
            branchvalues="total",
            insidetextorientation='radial'
        ))
        # Update layout for tight margin
        fig.update_layout(
            title = self.plot_title,
            margin = dict(l=0, r=0, b=0)
        )

        fig.show()



class RankingListVisualization():

    def __init__(self, viz_dict, number_of_items_in_ranking=10):
        self.viz_dict = viz_dict
        self.num_ranks = number_of_items_in_ranking
        self.ranked_dict = self.rank_items_in_dict()

    def rank_items_in_dict(self):
        ranked_dict = {}
        for year in self.viz_dict.keys():
            ranked_dict[year] = {key: self.viz_dict[year][key] for key in sorted(self.viz_dict[year], key=self.viz_dict[year].get, reverse=True)[:self.num_ranks]}

        return ranked_dict



class HeatMapVisualization():

    def __init__(self, df_viz, with_subplots=1):
        self.df = df_viz
        self.with_subplots = with_subplots
        self.title = 'Heat map of the play duration in minutes for each day'
        self.figure = make_subplots(rows=self.with_subplots, cols=1)
        self.height = 0
        self.row = 1
        self.data = None
        self.xaxis = None

    def build_day_heat_map(self, title):
        '''
            This function is in charge of building a single 2D Histogram trace.
        '''
        hist = go.Histogram2d(
            y=self.df['Play_DOM'],
            x=self.df['Play_Month'],
            autobiny=False,
            ybins=dict(start=1.5, end=31.5, size=1),
            autobinx=False,
            xbins=dict(start=0.5, end=12.5, size=1),
            z=self.df['Play_duration_in_minutes'],
            histfunc="sum",
            hovertemplate=
            "<b>%{y} %{x}</b><b> "+title+"<b><br>" +
            "Time listening: %{z:,.0f} minutes<br>" +
            "<extra></extra>",
            coloraxis="coloraxis"
        )
        self.data = hist
       
    def build_week_heat_map(self, title):
        '''
            This function is in charge of building a single 2D Histogram trace.
        '''
        hist = go.Histogram2d(
            y=self.df['Play_HOD'],
            x=self.df['Play_DOW'],
            ybins=dict(start=0.5, end=23.5, size=1),
            z=self.df['Play_duration_in_minutes'],
            histfunc="sum",
            hovertemplate=
            title +" - %{x}s, %{y}h<b><br>" +
            "Time listening: %{z:,.0f} minutes<br>" +
            "<extra></extra>",
            coloraxis="coloraxis"
        )
        self.data = hist 

    def render_heat_map(self, type, title):
        if type == 'DOM':
            self.build_day_heat_map(title)
            self.xaxis = dict(tickangle = -45, tickmode = 'array', tickvals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                ticktext = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])
        elif type == 'DOW':
            self.build_week_heat_map(title)
            #self.xaxis = dict(tickangle = -45, tickmode = 'array', tickvals = [0, 1, 2, 3, 4, 5, 6])
            self.xaxis = dict(tickangle = -45, categoryorder='array', categoryarray = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

        self.figure.add_trace(self.data, row = self.row, col=1)
        self.height += 500
        self.update_figure_info()
        self.row +=1

    def update_figure_info(self):
        self.figure.update_xaxes(self.xaxis)
        self.figure.update_yaxes(autorange="reversed")

        self.figure.update_layout(
            title=self.title,
            height = self.height,
            coloraxis=dict(colorscale='hot'),
            showlegend=False,
        )
        self.figure.update_xaxes(matches='x')


class BarChartVisualization():

    def __init__(self, df_viz, with_subplots=0):
        self.df = df_viz
        self.with_subplots = with_subplots
        self.title = 'Distribution of tracks'
        self.figure = self.create_figure()
        self.hover_unit = ''
        self.height = 500
        self.row = 1
        self.data = None

    def create_figure(self):
        if self.with_subplots == 0:
            return go.Figure()
        else:
            return make_subplots(rows=self.with_subplots, cols=1)


    def build_bar_chart(self, x_serie, y_serie, name):
        '''
            This function is in charge of building a single 2D Histogram trace.
        '''
        bar = go.Bar(
            name=name,
            x=x_serie,
            y=y_serie,
            hovertemplate=
            "<b>{0}</b><br>".format(name) +
            "<b>%{x}</b><br>" +
            "%{y:,.0f}" + "{0}<br>".format(self.hover_unit) +
            "<extra></extra>"
            )

        self.data = bar


    def render_bar_chart(self, x_serie, y_serie, name):
        self.build_bar_chart(x_serie, y_serie, name)

        if self.with_subplots == 0:
            self.figure.add_trace(self.data)
        else:
            self.figure.add_trace(self.data, row = self.row, col=1)
            self.height += 500
        self.update_figure_info()
        self.row +=1


    def update_figure_info(self):
        self.figure.update_layout(
            title=self.title,
            height = self.height,
        )




class PieChartVisualization():

    def __init__(self, serie_to_plot):
        self.serie_to_plot = serie_to_plot
        self.title = 'Pie chart'
        self.figure = go.Figure()
        self.height = 500
        self.data = None

    def build_pie(self):
        labels = self.serie_to_plot.dropna().unique()
        values = self.serie_to_plot.value_counts()
        pie = go.Pie(labels=labels, values=values, textinfo='label+percent')
        self.data = pie

    def render_pie_chart(self):
        self.build_pie()
        self.figure.add_trace(self.data)
        self.update_figure_info()

    def update_figure_info(self):
        self.figure.update_layout(
            title=self.title,
            height = self.height,
            showlegend=False,
        )


