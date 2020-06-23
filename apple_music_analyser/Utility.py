from zipfile import ZipFile
import pandas as pd


class Utility():

    @staticmethod
    def get_df_from_archive(archive_path):

        archive_files = ZipFile(archive_path)

        target_files = {
            'identifier_infos_path' : 'Apple_Media_Services/Apple Music Activity/Identifier Information.json.zip',
            'library_tracks_path' : 'Apple_Media_Services/Apple Music Activity/Apple Music Library Tracks.json.zip',
            'library_activity_path': 'Apple_Media_Services/Apple Music Activity/Apple Music Library Activity.json.zip',
            'likes_dislikes_path' : 'Apple_Media_Services/Apple Music Activity/Apple Music Likes and Dislikes.csv',
            'play_activity_path': 'Apple_Media_Services/Apple Music Activity/Apple Music Play Activity.csv'
        }

        dataframes = {}

        if archive_files.testzip() == None:
            identifier_infos_df = Utility.get_df_from_file(archive_files.open(target_files['identifier_infos_path']))
            dataframes['identifier_infos_df']=identifier_infos_df

            library_tracks_df = Utility.get_df_from_file(archive_files.open(target_files['library_tracks_path']))
            dataframes['library_tracks_df']=library_tracks_df

            library_activity_df = Utility.get_df_from_file(archive_files.open(target_files['library_activity_path']))
            dataframes['library_activity_df']=library_activity_df

            likes_dislikes_df = Utility.get_df_from_file(archive_files.open(target_files['likes_dislikes_path']))
            dataframes['likes_dislikes_df']=likes_dislikes_df

            play_activity_df = Utility.get_df_from_file(archive_files.open(target_files['play_activity_path']))
            #play_activity_df = []
            dataframes['play_activity_df']=play_activity_df

            archive_files.close()

        else:
            print('Please verify that you are passing a valid zip file')

        return dataframes

    @staticmethod
    def get_df_from_file(file_path):

        df = None
        if file_path.name.endswith('.json.zip'):
            df = pd.read_json(file_path, compression='zip')
        elif file_path.name.endswith('.json'):
            df = pd.read_json(file_path)
        elif file_path.name.endswith('.csv'):
            df = pd.read_csv(file_path, error_bad_lines=False)
        else:
            print('Please provide a file with extension .csv, .json or .json.zip')
        
        return df


    @staticmethod
    def validate_input_df_files(input_df):
        expected_files = ['identifier_infos_df','library_tracks_df', 'library_activity_df', 'likes_dislikes_df', 'play_activity_df']
        expected_format = pd.DataFrame
        for key in input_df.keys():
            if key not in expected_files:
                print('The input_df contains an unknown key: ', key)
                return False
            if not isinstance(input_df[key], expected_format):
                print('The value of '+key+' is not a pandas dataframe object.')
                return False
        return True


    @staticmethod
    def parse_date_time_column(df, input_timestamp_col):
        datetime_col = pd.to_datetime(df[input_timestamp_col])
        year, month, dom, dow, hod = Utility.extract_time_info_from_datetime(df, datetime_col)

        datetime_series = {
            'datetime':datetime_col,
            'year':year,
            'month':month,
            'dom':dom,
            'dow':dow,
            'hod':hod
        }

        return datetime_series


    @staticmethod
    def extract_time_info_from_datetime(df, datetime_col):
        year=datetime_col.dt.year
        month=datetime_col.dt.month
        dom=datetime_col.dt.day
        dow=datetime_col.dt.day_name()
        hod=datetime_col.dt.hour

        return year, month, dom, dow, hod


    @staticmethod
    def add_time_related_columns(df, datetime_series, col_name_prefix):
        df[col_name_prefix+' date time'] = datetime_series['datetime']
        df[col_name_prefix+' Year'] = datetime_series['year']
        df[col_name_prefix+' Month'] = datetime_series['month']
        df[col_name_prefix+' DOM'] = datetime_series['dom']
        df[col_name_prefix+' DOW'] = datetime_series['dow']
        df[col_name_prefix+' HOD'] = datetime_series['hod']

    @staticmethod
    def set_partial_listening(df):
        if df['End Reason Type'] == 'NATURAL_END_OF_TRACK':
            return True
        else:
        #if the play duration is above the media duration, we consider the track to be listened to completely
            if df['Play Duration Milliseconds'] >= df['Media Duration In Milliseconds']:
                return True
            else:
                return False

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




























