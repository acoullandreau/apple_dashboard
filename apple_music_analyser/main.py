from VisualizationDataframe import VisualizationDataframe
from Utility import Utility

input_df = Utility.get_df_from_archive('Apple_Media_Services.zip')
df_viz = VisualizationDataframe(input_df)
df_viz.parse_input_df()
#print(type(input_df['likes_dislikes_df']))
