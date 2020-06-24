from VisualizationDataframe import VisualizationDataframe
from Utility import Utility


import time

#start0 = time.time()

# get the input files
input_df = Utility.get_df_from_archive('Apple_Media_Services.zip')

# create an instance of the visualization dataframe class
df_viz = VisualizationDataframe(input_df)

print(df_viz.play_activity_df['Played completely'].value_counts())

#end = time.time()
#print('Total', end - start0)

