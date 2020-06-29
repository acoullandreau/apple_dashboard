from difflib import SequenceMatcher
import pandas as pd
from zipfile import ZipFile

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
    def compute_similarity_score(a, b):
        return SequenceMatcher(None, a, b).ratio()

    @staticmethod
    def concat_title_artist(title, artist):
        '''
            Returns a concatenated string without trailing spaces of the title and
            artist names passed as args
        '''
        return title.strip()+' && '+artist.strip()

    @staticmethod
    def clean_col_with_list(x):
        '''
            This function is used to break down the values of a serie containing lists.
            The idea is to return the values as a string ('', the unique value of a list, or a join of
            values separated by '&&').
        '''
        if type(x) != float:
            if x == None or len(x) == 0:
                return 'Unknown'
            elif len(x) == 1:
                return x[0]
            else:
                return ' && '.join(x)
        else:
            return 'Unknown'

    @staticmethod
    def compute_ratio_songs(serie):
        return (serie.value_counts()/serie.count())*100





















