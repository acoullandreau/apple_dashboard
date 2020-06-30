from VisualizationDataframe import VisualizationDataframe
from Utility import Utility
from DataVisualization import DataVisualization

########################################################
from Process import ProcessTracks, TrackSummaryObject
import time
import pandas as pd
########################################################



start0 = time.time()

# get the input files
input_df = Utility.get_df_from_archive('Apple_Media_Services.zip')

# create an instance of the visualization dataframe class
df_viz = VisualizationDataframe(input_df)


query_params = {
    'year':[2017, 2018, 2019],
    'rating':['LOVE']
}

visualization = DataVisualization(df_viz.get_df_viz(), query_params)


end = time.time()
print('Total', end - start0)

