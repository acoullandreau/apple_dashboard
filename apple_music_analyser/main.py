from VisualizationDataframe import VisualizationDataframe
from Utility import Utility


import time

#start0 = time.time()

# get the input files
input_df = Utility.get_df_from_archive('Apple_Media_Services.zip')

# create an instance of the visualization dataframe class
df_viz = VisualizationDataframe(input_df)
# from the input files, get the necessary dataframes used to build the visualization dataframe, and parse them
df_viz.parse_input_df()
df_viz.parse_library_activity_df()
df_viz.parse_play_activity_df()
df_viz.parse_library_tracks_infos_df()
df_viz.parse_likes_dislikes_df()

#end = time.time()
#print('Total', end - start0)

