import pandas as pd
import numpy as np
from apple_music_analyser.Utility import Utility

class Parser():

    def __init__(self, source_files):
        self.source_files = source_files
        self.source_dataframes = self.parse_input_df(self.source_files)
        self.parse_source_dataframes()

    @staticmethod
    def parse_input_df(source_files):

        error_message_bad_input = ("Please ensure that the input_df object has the following structure...\n"

        '{  "identifier_infos_df" : identifier_infos_df, "library_tracks_df" : library_tracks_df,\n'
        '"library_activity_df" : library_activity_df, "likes_dislikes_df" : likes_dislikes_df, "play_activity_df" : play_activity_df    }\n'

        '...And that the values in this dictionary are pandas dataframes.')

        dataframes = {}
        if len(source_files) != 5:
            print(error_message_bad_input)

        else:
            if Utility.validate_input_df_files(source_files):
                dataframes['likes_dislikes_df'] = source_files['likes_dislikes_df']
                dataframes['play_activity_df'] = source_files['play_activity_df']
                dataframes['identifier_infos_df'] = source_files['identifier_infos_df']
                dataframes['library_tracks_df'] = source_files['library_tracks_df']
                dataframes['library_activity_df'] = source_files['library_activity_df']
            else:
                print(error_message_bad_input)
        
        return dataframes


    def parse_source_dataframes(self):
        if self.source_dataframes != {}:
            self.likes_dislikes_df = self.parse_likes_dislikes_df(self.source_dataframes['likes_dislikes_df'])
            self.play_activity_df = self.parse_play_activity_df(self.source_dataframes['play_activity_df'])
            self.identifier_infos_df = self.source_dataframes['identifier_infos_df']
            self.library_tracks_df = self.parse_library_tracks_infos_df(self.source_dataframes['library_tracks_df'])
            self.library_activity_df = self.parse_library_activity_df(self.source_dataframes['library_activity_df'])
        else:
            print('No source dataframes found in input.')


    @staticmethod
    def parse_library_activity_df(library_activity_df):
        # parse time related column
        parsed_datetime_series = Utility.parse_date_time_column(library_activity_df, 'Transaction Date')
        Utility.add_time_related_columns(library_activity_df, parsed_datetime_series, col_name_prefix='Transaction ')
    
        # parse action agent column
        library_activity_df['Transaction Agent'] = library_activity_df['UserAgent'].str.split('/').str.get(0)
        library_activity_df.replace({'Transaction Agent' : { 'itunescloudd' : 'iPhone', 'iTunes' : 'Macintosh'}}, inplace=True)
        library_activity_df['Transaction Agent Model'] = library_activity_df[library_activity_df['Transaction Agent'] == 'iPhone']['UserAgent'].str.split('/').str.get(3).str.split(',').str.get(0)
        library_activity_df.loc[library_activity_df['Transaction Agent'].eq('Macintosh'), 'Transaction Agent Model'] = 'Macintosh'

        return library_activity_df

    @staticmethod
    def parse_play_activity_df(play_activity_df, convert_to_local_time = True, drop_columns=True):
        columns_to_drop = [
        'Apple Id Number', 'Apple Music Subscription', 'Build Version', 'Client IP Address',
        'Content Specific Type', 'Device Identifier', 'Event Reason Hint Type', 'Activity date time',
        'End Position In Milliseconds', 'Event Received Timestamp', 'Media Type', 'Metrics Bucket Id', 
        'Metrics Client Id','Original Title', 'Source Type', 'Start Position In Milliseconds',
        'Store Country Name', 'Milliseconds Since Play', 'Event End Timestamp', 'Event Start Timestamp',
        'UTC Offset In Seconds','Play Duration Milliseconds', 'Media Duration In Milliseconds', 'Feature Name'
        ]
        # Rename columns for merges later
        play_activity_df.rename(columns={'Content Name':'Title', 'Artist Name':'Artist'}, inplace=True)
        
        # Add time related columns
        play_activity_df['Activity date time'] = pd.to_datetime(play_activity_df['Event Start Timestamp'])
        play_activity_df['Activity date time'].fillna(pd.to_datetime(play_activity_df['Event End Timestamp']), inplace=True)
        if convert_to_local_time is True:
            play_activity_df['Activity date time'] = Utility.convert_to_local_time(play_activity_df['Activity date time'], play_activity_df['UTC Offset In Seconds'])
        parsed_datetime_series = Utility.parse_date_time_column(play_activity_df, 'Activity date time')
        Utility.add_time_related_columns(play_activity_df, parsed_datetime_series, col_name_prefix='Play ')

        # We remove year outliers (Apple Music started in 2015, whatever is reported before is a mistake)
        play_activity_df = play_activity_df.drop(play_activity_df[play_activity_df['Play Year']< 2015].index)

        # Add partial listening column 
        play_duration = play_activity_df['Play Duration Milliseconds']
        media_duration = play_activity_df['Media Duration In Milliseconds']
        Parser.set_partial_listening(play_activity_df, play_activity_df['End Reason Type'], play_duration, media_duration)

        # Add track origin column
        play_activity_df['Track origin'] = play_activity_df['Feature Name'].apply(Parser.get_track_origin)

        # Add play duration column
        activity_start = pd.to_datetime(play_activity_df['Event Start Timestamp'])
        activity_end = pd.to_datetime(play_activity_df['Event End Timestamp'])
        played_completely = play_activity_df['Played completely']
        Parser.compute_play_duration(play_activity_df, activity_start, activity_end, played_completely, play_duration, media_duration)

        # we remove outliers from this play duration column, saying that if a value if above the 99th percentile,
        # we drop it, and replace it by the duration of the media
        percentile = play_activity_df['Play duration in minutes'].quantile(0.99)
        Parser.remove_play_duration_outliers(play_activity_df, play_activity_df['Play duration in minutes'], media_duration, percentile)

        #we can then remove the columns we do not need anymore!
        if drop_columns:
            play_activity_df = play_activity_df.drop(columns_to_drop, axis=1, errors='ignore')

        return play_activity_df

    @staticmethod
    def parse_library_tracks_infos_df(library_tracks_infos_df):
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
        library_tracks_df = library_tracks_infos_df.drop(columns_to_drop, axis=1, errors='ignore')
        return library_tracks_df

    @staticmethod
    def parse_likes_dislikes_df(likes_dislikes_df):
        likes_dislikes_df['Title'] = likes_dislikes_df['Item Description'].str.split(' -').str.get(1).str.strip()
        likes_dislikes_df['Artist'] = likes_dislikes_df['Item Description'].str.split(' - ').str.get(0).str.strip()
        return likes_dislikes_df

    @staticmethod
    def set_partial_listening(play_activity_df, end_reason_type, play_duration, media_duration):
        play_activity_df['Played completely'] = False
        play_activity_df.loc[end_reason_type == 'NATURAL_END_OF_TRACK', 'Played completely'] = True
        play_activity_df.loc[play_duration >= media_duration, 'Played completely'] = True


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
    def compute_play_duration(play_activity_df, start, end, played_completely, play_duration, media_duration):
        play_activity_df['Play duration in minutes'] = media_duration/60000
        play_activity_df.loc[start.dt.day == end.dt.day, 'Play duration in minutes'] = (end - start).dt.total_seconds()/60
        play_activity_df.loc[(played_completely == False)&(type(play_duration)!=float)&(play_duration>0), 'Play duration in minutes'] = play_duration/60000

    @staticmethod
    def remove_play_duration_outliers(play_activity_df, play_duration, media_duration, percentile):
        play_activity_df.loc[play_duration > percentile, 'Play duration in minutes'] = media_duration/60000




