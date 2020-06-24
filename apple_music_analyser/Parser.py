import pandas as pd
import numpy as np
from Utility import Utility
import time

class Parser():

    def __init__(self, source_files):
        self.source_files = source_files
        self.source_dataframes = self.parse_input_df()
        self.parse_source_dataframes()

    def parse_input_df(self):

        error_message_bad_input = ("Please ensure that the input_df object has the following structure...\n"

        '{  "identifier_infos_df" : identifier_infos_df, "library_tracks_df" : library_tracks_df,\n'
        '"library_activity_df" : library_activity_df, "likes_dislikes_df" : likes_dislikes_df, "play_activity_df" : play_activity_df    }\n'

        '...And that the values in this dictionary are pandas dataframes.')

        dataframes = {}
        if len(self.source_files) != 5:
            print(error_message_bad_input)

        else:
            if Utility.validate_input_df_files(self.source_files):
                dataframes['likes_dislikes_df'] = self.source_files['likes_dislikes_df']
                dataframes['play_activity_df'] = self.source_files['play_activity_df']
                dataframes['identifier_infos_df'] = self.source_files['identifier_infos_df']
                dataframes['library_tracks_df'] = self.source_files['library_tracks_df']
                dataframes['library_activity_df'] = self.source_files['library_activity_df']
            else:
                print(error_message_bad_input)
        
        return dataframes


    def parse_source_dataframes(self):
        if self.source_dataframes != {}:
            self.likes_dislikes_df = self.source_dataframes['likes_dislikes_df']
            self.parse_likes_dislikes_df()
            self.play_activity_df = self.source_dataframes['play_activity_df']
            self.parse_play_activity_df()
            self.identifier_infos_df = self.source_dataframes['identifier_infos_df']
            self.library_tracks_df = self.source_dataframes['library_tracks_df']
            self.parse_library_tracks_infos_df()
            self.library_activity_df = self.source_dataframes['library_activity_df']
            self.parse_library_activity_df()
        else:
            print('No source dataframes found in input.')


    def parse_library_activity_df(self):
        # parse time related column
        parsed_datetime_series = Utility.parse_date_time_column(self.library_activity_df, 'Transaction Date')
        Utility.add_time_related_columns(self.library_activity_df, parsed_datetime_series, 'Transaction')
    
        # parse action agent column
        self.library_activity_df['Transaction Agent'] = self.library_activity_df['UserAgent'].str.split('/').str.get(0)
        self.library_activity_df['Transaction Agent'] = self.library_activity_df.replace({'Transaction Agent' : { 'itunescloudd' : 'iPhone', 'iTunes' : 'Macintosh'}})
        self.library_activity_df['Transaction Agent Model'] = self.library_activity_df[self.library_activity_df['Transaction Agent'] == 'iPhone']['UserAgent'].str.split('/').str.get(3).str.split(',').str.get(0)
        self.library_activity_df.loc[self.library_activity_df['Transaction Agent'].eq('Macintosh'), 'Transaction Agent Model'] = 'Macintosh'


    def parse_play_activity_df(self, drop_columns=True):
        columns_to_drop = [
        'Apple Id Number', 'Apple Music Subscription', 'Build Version', 'Client IP Address',
        'Content Specific Type', 'Device Identifier', 'Event Reason Hint Type',
        'End Position In Milliseconds', 'Event Received Timestamp', 'Media Type', 'Metrics Bucket Id', 
        'Metrics Client Id','Original Title', 'Source Type', 'Start Position In Milliseconds',
        'Store Country Name', 'Milliseconds Since Play', 'Event End Timestamp', 'Event Start Timestamp',
        'UTC Offset In Seconds','Play Duration Milliseconds', 'Media Duration In Milliseconds', 'Feature Name'
        ]
        # Rename columns for merges later
        self.play_activity_df.rename(columns={'Content Name':'Title', 'Artist Name':'Artist'}, inplace=True)
        # Add time related columns
        self.play_activity_df['Activity date time'] = pd.to_datetime(self.play_activity_df['Event Start Timestamp'])
        self.play_activity_df['Activity date time'].fillna(pd.to_datetime(self.play_activity_df['Event End Timestamp']), inplace=True)
        parsed_datetime_series = Utility.parse_date_time_column(self.play_activity_df, 'Activity date time')
        Utility.add_time_related_columns(self.play_activity_df, parsed_datetime_series, 'Play')
        self.play_activity_df = self.play_activity_df.rename(columns={'Play HOD':'Play HOD UTC'})
        self.play_activity_df['Play HOD Local Time']= self.play_activity_df['Play HOD UTC'] + self.play_activity_df['UTC Offset In Seconds']/3600
        self.play_activity_df['Play HOD Local Time'] = self.play_activity_df['Play HOD Local Time'].astype(int)

        # Add partial listening column 
        self.set_partial_listening(self.play_activity_df['End Reason Type'], self.play_activity_df['Play Duration Milliseconds'], self.play_activity_df['Media Duration In Milliseconds'])

        # Add track origin column
        self.play_activity_df['Track origin'] = self.play_activity_df['Feature Name'].apply(self.get_track_origin)

        start = time.time()
        # Add play duration column
        self.play_activity_df['Play duration in minutes'] = self.play_activity_df.apply(self.compute_play_duration, axis=1)
        # we remove outliers from this column, saying that if a value if above the 99th percentile,
        # we drop it, and replace it by the duration of the media
        percentile = self.play_activity_df['Play duration in minutes'].quantile(0.99)
        self.play_activity_df['Play duration in minutes'] = self.play_activity_df.apply(self.remove_play_duration_outliers, percentile=percentile, axis=1)
        end = time.time()
        print(end - start)
        #we can then remove the columns we do not need anymore!
        if drop_columns:
            self.play_activity_df = self.play_activity_df.drop(columns_to_drop, axis=1)


    def parse_library_tracks_infos_df(self):
        columns_to_drop = ['Content Type', 'Sort Name',
        'Sort Artist', 'Is Part of Compilation', 'Sort Album',
        'Album Artist', 'Track Number On Album',
        'Track Count On Album', 'Disc Number Of Album', 'Disc Count Of Album',
        'Date Added To iCloud Music Library', 'Last Modified Date',
        'Purchase Date', 'Is Purchased', 'Audio File Extension',
        'Is Checked', 'Audio Matched Track Identifier', 'Grouping', 'Comments', 
        'Beats Per Minute', 'Album Rating', 'Remember Playback Position', 
        'Album Like Rating', 'Album Rating Method', 'Work Name', 'Rating',
        'Movement Name', 'Movement Number', 'Movement Count',
        'Display Work Name', 'Copyright', 'Playlist Only Track',
        'Sort Album Artist', 'Sort Composer']

        self.library_tracks_df.drop(columns_to_drop, axis=1, inplace=True)


    def parse_likes_dislikes_df(self):
        self.likes_dislikes_df['Title'] = self.likes_dislikes_df['Item Description'].str.split(' -').str.get(1).str.strip()
        self.likes_dislikes_df['Artist'] = self.likes_dislikes_df['Item Description'].str.split(' - ').str.get(0).str.strip()



    def set_partial_listening(self, end_reason_type, play_duration, media_duration):
        self.play_activity_df['Played completely'] = False
        self.play_activity_df.loc[end_reason_type == 'NATURAL_END_OF_TRACK', 'Played completely'] = True
        self.play_activity_df.loc[play_duration >= media_duration, 'Played completely'] = True


    @staticmethod
    def get_track_origin(x):
        if str(x) != 'nan':
            x_cat = str(x).split('/')[0].strip()
            if x_cat == 'search' or x_cat =='browse':
                return 'search'
            elif x_cat == 'library' or x_cat == 'my-music' or x_cat == 'playlists' or x_cat == 'playlist_detail':
                return 'library'
            elif x_cat == 'for_you':
                if len(str(x).split('/')) > 1:
                    x_subcat = str(x).split('/')[1].strip()
                    if x_subcat == 'recently_played':
                        return 'for you - recently played'
                    elif x_subcat == 'personalized_mix':
                        return 'for you - personalized mix'
                    else:
                        return 'for you - other'
                else:
                    return 'for you - other'
            else:
                return 'other'
        else:
            return 'other'

    @staticmethod
    def compute_play_duration(df):
        end = pd.to_datetime(df['Event End Timestamp'])
        start = pd.to_datetime(df['Event Start Timestamp'])
        if str(end) != 'NaT' and str(start) != 'NaT':
            if end.day == start.day:
                diff = end - start
                duration = diff.total_seconds()/60
            else:
                duration = df['Media Duration In Milliseconds']/60000
        else:
            if df['Played completely'] is False:
                if type(df['Play Duration Milliseconds']) == float:
                    duration = df['Media Duration In Milliseconds']/60000
                else:
                    duration = df['Play Duration Milliseconds']/60000       
            else:
                duration = df['Media Duration In Milliseconds']/60000
        return duration

    @staticmethod
    def remove_play_duration_outliers(df, percentile):
        if df['Play duration in minutes'] <= percentile:
            return df['Play duration in minutes']
        else:
            return df['Media Duration In Milliseconds']/60000








