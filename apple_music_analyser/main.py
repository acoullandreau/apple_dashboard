from VisualizationDataframe import VisualizationDataframe
from Utility import Utility
from DataVisualization import DataVisualization

start0 = time.time()

# get the input files
#input_df = Utility.get_df_from_archive('Apple_Media_Services.zip')

# create an instance of the visualization dataframe class
#df_viz = VisualizationDataframe(input_df)
#Utility.save_to_pickle(df_viz, 'df_viz')

df_viz = Utility.load_from_pickle('df_viz.pkl')

query_params = {
    'year':[2017, 2018, 2019],
    'rating':['LOVE']
}

visualization = DataVisualization(df_viz.get_df_viz(), query_params)
#print(df_viz.get_df_viz().shape)

end = time.time()
print('Total', end - start0)

