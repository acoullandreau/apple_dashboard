import pandas as pd
import pickle

from apple_music_analyser.Utility import Utility
from apple_music_analyser.Parser import Parser
from apple_music_analyser.Process import ProcessTracks, TrackSummaryObject

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
        self.process_tracks = ProcessTracks()
        self.process_tracks_in_df()
        self.track_summary_objects = TrackSummaryObject(self.process_tracks.track_instance_dict, self.process_tracks.artist_tracks_titles, self.process_tracks.genres_list, self.process_tracks.items_not_matched)
        self.df_visualization = self.build_df_visualisation('play_activity')

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

    def process_tracks_in_df(self):
        # we process the library tracks
        self.process_tracks.process_library_tracks_df(self.library_tracks_df)
        # # we process the identifier infos
        self.process_tracks.process_identifier_df(self.identifier_infos_df)
        # # we process the play activity
        self.process_tracks.process_play_df(self.play_activity_df)
        # # we process the likes dislikes
        self.process_tracks.process_likes_dislikes_df(self.likes_dislikes_df)

    def build_df_visualisation(self, target_df):
        self.track_summary_objects.build_index_track_instance_dict(target_df)
        match_index_instance_activity = self.track_summary_objects.match_index_instance
        index_instance_df = pd.DataFrame.from_dict(match_index_instance_activity, orient='index', columns=['Track Instance', 'Library Track', 'Rating', 'Genres'])
        df_visualization = self.play_activity_df.drop(['Genre'], axis=1)
        df_visualization = pd.concat([df_visualization,index_instance_df], axis=1)
        df_visualization['Rating'] = df_visualization['Rating'].apply(Utility.clean_col_with_list)
        df_visualization['Genres'] = df_visualization['Genres'].apply(Utility.clean_col_with_list)
        df_visualization['Library Track'].fillna(False, inplace=True)
        df_visualization.columns = [c.replace(' ', '_') for c in df_visualization.columns]
        return df_visualization







