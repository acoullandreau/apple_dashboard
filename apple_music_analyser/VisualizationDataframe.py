import pandas as pd
import time

from Utility import Utility
from Parser import Parser


class VisualizationDataframe():

    def __init__(self, input_df):
        self.input_df = input_df
        self.parser = Parser(input_df)
        self.source_dataframes = self.parser.source_dataframes
        self.likes_dislikes_df = None
        self.play_activity_df = None
        self.identifier_infos_df = None
        self.library_tracks_df = None
        self.library_activity_df = None
        self.get_df_from_source()
        self.df_visualization = None

    def get_df_viz(self):
        return self.df_visualization

    def get_source_dataframes(self):
        return self.source_dataframes

    def get_play_activity_df(self):
        return self.play_activity_df

    def get_identifier_info_df(self):
        return self.identifier_infos_df

    def get_library_tracks_df(self):
        return self.library_tracks_df

    def get_library_activity_df(self):
        return self.library_activity_df

    def get_likes_dislikes_df(self):
        return self.likes_dislikes_df

    def get_df_from_source(self):
        if self.source_dataframes != {}:
            self.likes_dislikes_df = self.parser.likes_dislikes_df
            self.play_activity_df = self.parser.play_activity_df
            self.identifier_infos_df = self.parser.identifier_infos_df
            self.library_tracks_df = self.parser.library_tracks_df
            self.library_activity_df = self.parser.library_activity_df
