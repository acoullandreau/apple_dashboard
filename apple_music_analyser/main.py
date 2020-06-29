from VisualizationDataframe import VisualizationDataframe
from Utility import Utility
from Query import Query


import time

start0 = time.time()

# get the input files
input_df = Utility.get_df_from_archive('Apple_Media_Services.zip')

# create an instance of the visualization dataframe class
df_viz = VisualizationDataframe(input_df)

query = Query(df_viz.get_df_viz())
print(query.get_query_params())
#print(df_viz.track_summary_objects.genres_list)

query_params = {
    'year':[2017, 2018, 2019],
    'rating':['LOVE']
}
query.query_params = query_params
print(query.get_query_params())


end = time.time()
print('Total', end - start0)

