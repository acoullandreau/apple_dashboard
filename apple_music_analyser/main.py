from VisualizationDataframe import VisualizationDataframe
from Utility import Utility
from DataVisualization import SunburstVisualization, RankingListVisualization, HeatMapVisualization
from Query import Query, QueryFactory

import time

start0 = time.time()

# get the input files
#input_df = Utility.get_df_from_archive('Apple_Media_Services.zip')

# create an instance of the visualization dataframe class
#df_viz = VisualizationDataframe(input_df)
#Utility.save_to_pickle(df_viz, 'df_viz')

df_viz = Utility.load_from_pickle('df_viz.pkl')

#extract a df using a query
# query_params = {
#     'year':[2017, 2018, 2019],
#     'rating':['LOVE']
# }
#filtered_df = QueryFactory().create_query(df_viz.get_df_viz(), query_params)
#print(filtered_df.filtered_df.shape)

#plot a sunburst
# query_params = {
#     'year':[2017, 2018, 2019],
#     'rating':['LOVE']
# }
# ranking_dict = df_viz.track_summary_objects.build_ranking_dict_per_year(df_viz.get_df_viz(), 'Genres', query_params)
# sunburst = SunburstVisualization(ranking_dict, 'Genres')
# sunburst.render_sunburst_plot()


#get a ranking dict
# query_params = {
#     'year':[2017, 2018, 2019],
#     'rating':['LOVE']
# }
# ranking_dict = df_viz.track_summary_objects.build_ranking_dict_per_year(df_viz.get_df_viz(), 'Artist', query_params)
# ranking = RankingListVisualization(ranking_dict, 5)
# print(ranking.ranked_dict)

#plot a heatmap for a single year
# query_params = {
#     'year':[2018],
#     'rating':['LOVE']
# }
# filtered_df = QueryFactory().create_query(df_viz.get_df_viz(), query_params)
# heat_map = HeatMapVisualization(filtered_df.filtered_df)
# data = heat_map.render_day_heat_map('2018')
# heat_map.render_single_heat_map(data)
# heat_map.figure.show()

#plot a heatmap for multiple years
# query_params = {
#     'year':[2017, 2018, 2019],
#     'rating':['LOVE']
# }

# heat_map = HeatMapVisualization(df_viz.get_df_viz(), 3)

# for year in query_params['year']:
# 	year_query_params = query_params
# 	year_query_params['year'] = [year]
# 	filtered_df = QueryFactory().create_query(df_viz.get_df_viz(), query_params)
# 	heat_map.df = filtered_df.filtered_df
# 	heat_map.build_day_heat_map(str(year))
# 	heat_map.render_heat_map()

# heat_map.figure.show()













#visualization = DataVisualization(df_viz.get_df_viz(), query_params)
#print(df_viz.get_df_viz().shape)

#logic : 
#decide what to plot, with agg and subplot
#if no agg and no subplot -> multiple query, one output df per year, add_trace
#if no agg and subplot -> multiple query, one output df per year, make_subplots
#if agg -> query with all years, single_trace

# visualization_params = {
# 	aggregate:False,
# 	subplots:False,
# 	plot_type:'',
# 	query_params:query_params
# }
#plot_type in ['sunburst', 'pie', 'bar', 'list']


end = time.time()
print('Total', end - start0)

# def list_top_ranked(df, ranking_target, num_ranks, query_params=query_params_default):
#     ranking_dict = build_ranking_dict_per_year(df, ranking_target, query_params)
#     for year in query_params['year']:
#         ranking = {key: ranking_dict[year][key] for key in sorted(ranking_dict[year], key=ranking_dict[year].get, reverse=True)[:num_ranks]}
#         print('Top ranking for '+ str(year))
#         print('   ', ranking)
#         print('\n')



#cases to cover
#default dict, aggregated, no subplots
#default dict, not aggregated, no subplots
#default dict, not aggregated, subplots
#query dict, aggregated, no subplots
#query dict, not aggregated, no subplots
#query dict, not aggregated, subplots