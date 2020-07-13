import pandas as pd
import unittest
from unittest.mock import MagicMock

from apple_music_analyser.Utility import Utility
from apple_music_analyser.Track import Track
from apple_music_analyser.Query import Query, QueryFactory
from apple_music_analyser.Parser import Parser
from apple_music_analyser.Process import ProcessTracks, TrackSummaryObject
#from apple_music_analyser.VisualizationDataframe import VisualizationDataframe
#from apple_music_analyser.DataVisualization import SunburstVisualization, RankingListVisualization, HeatMapVisualization, PieChartVisualization, BarChartVisualization


class TestUtils(unittest.TestCase):

    def test_compute_ratio_songs(self):
        serie = pd.Series([1, 1, 1, 1, 2, 2, 3, 3, 3, 3])
        result = Utility.compute_ratio_songs(serie).tolist()
        self.assertEqual(result, [40.0, 40.0, 20.0])

    def test_clean_col_with_list(self):
        serie = pd.Series([['Rock'], ['Pop'], ['Soundtrack', 'Pop']])
        result = serie.apply(Utility.clean_col_with_list).tolist()
        self.assertEqual(result, ['Rock', 'Pop', 'Soundtrack && Pop'])

    def test_concat_title_artist(self):
        title = 'Title'
        artist = 'Artist '
        result = Utility.concat_title_artist(title, artist)
        self.assertEqual(result, 'Title && Artist')

    def test_convert_to_local_time(self):
        serie = pd.date_range('2020-01-01', periods=3, freq='H')
        timezone_serie = pd.Series([3600, -7200, 0])
        result = Utility.convert_to_local_time(serie, timezone_serie).tolist()
        result = [str(x) for x in result]
        self.assertEqual(result, ['2020-01-01 01:00:00', '2019-12-31 23:00:00', '2020-01-01 02:00:00'])

    def test_extract_time_info_from_datetime(self):
        serie = pd.to_datetime(pd.Series('2020-01-01'))
        year, month, dom, dow, hod = Utility.extract_time_info_from_datetime(serie)
        self.assertEqual(year.values[0], 2020)
        self.assertEqual(month.values[0], 1)
        self.assertEqual(dom.values[0], 1)
        self.assertEqual(dow.values[0], 'Wednesday')
        self.assertEqual(hod.values[0], 0)

    def test_parse_date_time_column(self):
        '''
            We only test if it returns a dict, as the values come from another function tested
            in a separate test (cf. test_extract_time_info_from_datetime)
        '''
        df = pd.DataFrame(pd.Series('2020-01-01'), columns=['Timestamp'])
        result = Utility.parse_date_time_column(df, 'Timestamp')
        self.assertEqual(type(result), dict) 

    def test_add_time_related_columns(self):
        df = pd.DataFrame(pd.Series('2020-01-01'), columns=['Timestamp'])
        datetime_series = Utility.parse_date_time_column(df, 'Timestamp')
        Utility.add_time_related_columns(df, datetime_series, col_name_prefix='pref_', col_name_suffix='_suff')
        expected = {'Timestamp':['2020-01-01'], 'pref_date time_suff': ['2020-01-01'], 'pref_Year_suff': [2020], 'pref_Month_suff': [1], 'pref_DOM_suff': [1], 'pref_DOW_suff': ['Wednesday'], 'pref_HOD_suff': [0]}
        expected_output = pd.DataFrame.from_dict(expected)
        self.assertEqual(df.shape, expected_output.shape) 
        self.assertEqual(df.columns.tolist(), expected_output.columns.tolist()) 

    # def test_get_df_from_archive(self):
    #   '''
    #       We only test the case where the path is wrong
    #       This function relies on external package (ZipFile), well covered by tests.
    #   '''
    #   archive_path = None
    #   result = Utility.get_df_from_archive(archive_path)
    #   self.assertEqual(result, {})





class TestTrack(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.track = Track('id')

    def test_init_track(self):
        self.assertTrue(isinstance(self.track, Track))
        self.assertEqual(self.track.identifier, 'id')
        self.assertEqual(self.track.titles, [])
        self.assertEqual(self.track.artist, None)
        self.assertEqual(self.track.is_in_lib, False)
        self.assertEqual(self.track.appearances, [])
        self.assertEqual(self.track.genre, [])
        self.assertEqual(self.track.apple_music_id, [])
        self.assertEqual(self.track.rating, [])

    def test_has_title_name(self):
        self.track.titles = ['Title']
        self.assertEqual(self.track.has_title_name('Title'), True)
        self.assertEqual(self.track.has_title_name('Other Title'), False)
        self.track.titles = []

    def test_add_title(self):
        self.track.add_title('New Title')
        self.assertEqual(self.track.titles, ['New Title'])

    def test_set_artist(self):
        self.track.set_artist('New Artist')
        self.assertEqual(self.track.artist, 'New Artist')


    def test_set_apple_music_id(self):
        self.track.set_apple_music_id(1234567)
        self.assertEqual(self.track.apple_music_id, [1234567])

    def test_set_library_flag(self):
        self.assertEqual(self.track.is_in_lib, False)
        self.track.set_library_flag()
        self.assertEqual(self.track.is_in_lib, True)


    def test_set_genre(self):
        genre = float('NaN')
        self.track.set_genre(genre)
        self.assertEqual(self.track.genre, [])
        genre = 'Genre'
        self.track.set_genre(genre)
        self.assertEqual(self.track.genre, ['Genre'])
        self.track.genre = []


    def test_add_appearance(self):
        appearance_dict = {'source': 'source', 'df_index':'index'}
        self.track.add_appearance(appearance_dict)
        self.assertEqual(self.track.appearances, [{'source': 'source', 'df_index':'index'}])
        self.track.appearances = []

    def test_set_rating(self):
        rating = 'LOVE'
        self.track.set_rating(rating)
        self.assertEqual(self.track.rating, ['LOVE'])
        rating = 'LIKE'
        self.track.set_rating(rating)
        self.assertEqual(self.track.rating, ['LOVE'])
        rating = 'DISLIKE'
        self.track.set_rating(rating)
        self.assertEqual(self.track.rating, ['LOVE', 'DISLIKE'])
        rating = 'other rating'
        self.track.set_rating(rating)
        self.assertEqual(self.track.rating, ['LOVE', 'DISLIKE'])
        self.track.rating = []

    @classmethod
    def tearDownClass(self):
        self.track = None



class TestQueryFactory(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        df = {'Artist':['Artist_1', 'Artist_2'], 'Title': ['Title_1', 'Title_2'], 
            'Offline':[False, True], 'Play_Year':[2020, 2019], 
            'Played_completely':[True, False], 'Track_origin':['library', 'other'],
            'Library_Track':[True, False], 'Rating':['LOVE', 'Unknown'],
            'Genres':['Genre_1', 'Genre_2']
        }
        self.reference_df = pd.DataFrame.from_dict(df)
        self.query_factory = QueryFactory()

    def test_init_QueryFactory(self):
        self.assertTrue(isinstance(self.query_factory, QueryFactory))

    def test_query_creator_without_params(self):
        query = self.query_factory.create_query(self.reference_df)
        query_params_default = {
                'year':self.reference_df['Play_Year'].unique(),
                'genre':[],
                'artist':[],
                'title':[],
                'rating':[],
                'origin':[],
                'offline':None,
                'library':None,
                'skipped':None,
            }
        self.assertTrue(isinstance(query, Query))
        self.assertEqual(query.reference_df.shape, self.reference_df.shape)
        self.assertEqual(query.reference_df.columns.tolist(), self.reference_df.columns.tolist())
        self.assertEqual(len(query.reference_df['Artist']), 2)
        self.assertEqual(len(query.query_params), len(query_params_default))
        self.assertEqual(len(query.query_params['year']), 2)
        self.assertEqual(query.query_params['genre'], [])

    def test_query_creator_with_params(self):
        query_params = {
                'year':[2019],
                'genre':['Genre_1'],
                'artist':['Artist_1'],
                'title':['Title_1'],
                'rating':['LOVE'],
                'origin':['library'],
                'offline':False,
                'library':True,
                'skipped':False,
            }
        query = self.query_factory.create_query(self.reference_df, query_params)
        self.assertTrue(isinstance(query, Query))
        self.assertEqual(query.reference_df.shape, self.reference_df.shape)
        self.assertEqual(query.reference_df.columns.tolist(), self.reference_df.columns.tolist())
        self.assertEqual(len(query.reference_df['Artist']), 2)
        self.assertEqual(len(query.query_params), len(query_params))
        self.assertEqual(len(query.query_params['year']), 1)
        self.assertEqual(query.query_params['genre'], ['Genre_1'])


    @classmethod
    def tearDownClass(self):
        self.reference_df = None
        self.query_factory = None


class TestQuery(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        df = {'Artist':['Artist_1', 'Artist_2'], 'Title': ['Title_1', 'Title_2'], 
            'Offline':[False, True], 'Play_Year':[2020, 2019], 
            'Played_completely':[True, False], 'Track_origin':['library', 'other'],
            'Library_Track':[True, False], 'Rating':['LOVE', 'Unknown'],
            'Genres':['Genre_1', 'Genre_2']
        }
        self.query_params = {
            'year':[2020],
            'genre':['Genre_1'],
            'artist':['Artist_1'],
            'title':['Title_1'],
            'rating':['LOVE'],
            'origin':['library'],
            'offline':False,
            'library':True,
            'skipped':False,
        }
        self.reference_df = pd.DataFrame.from_dict(df)
        self.query = Query(self.reference_df, self.query_params)

    def test_init_Query(self):
        self.assertTrue(isinstance(self.query, Query))
        self.assertEqual(self.query.reference_df.shape, self.reference_df.shape)
        self.assertEqual(self.query.reference_df.columns.tolist(), self.reference_df.columns.tolist())
        self.assertEqual(len(self.query.reference_df['Artist']), 2)
        self.assertEqual(len(self.query.query_params), len(self.query_params))
        self.assertEqual(len(self.query.query_params['year']), 1)
        self.assertEqual(self.query.query_params['genre'], ['Genre_1'])
        # query_string and filtered_df are tested in individual tests

    def test_get_query_params(self):
        result = self.query.get_query_params()
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result), 9)

    def test_get_query_string(self):
        result = self.query.get_query_string()
        self.assertTrue(isinstance(result, str))
        self.assertEqual(result, 'Play_Year==2020&Genres.str.contains("Genre_1")&Artist.str.contains("Artist_1")&Title.str.contains("Title_1")&Rating.str.contains("LOVE")&Track_origin.str.contains("library")&Offline.isin([False])&Library_Track.isin([True])&Played_completely.isin([True])')

    def test_get_filtered_df(self):
        result = self.query.get_filtered_df()
        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assertEqual(result.shape[0], 1)
        self.assertEqual(result['Play_Year'][0], 2020)

    def test_build_string_query_element(self):
        result_one_string = self.query.build_string_query_element('Category', ['value_1'])
        result_two_strings = self.query.build_string_query_element('Category', ['value_1', 'value_2'])
        result_three_strings = self.query.build_string_query_element('Category', ['value_1', 'value_2', 'value_3'])
        self.assertTrue(isinstance(result_one_string, str))
        self.assertEqual(result_one_string, 'Category.str.contains("value_1")')
        self.assertTrue(isinstance(result_two_strings, str))
        self.assertEqual(result_two_strings, '(Category.str.contains("value_1")|Category.str.contains("value_2"))')
        self.assertTrue(isinstance(result_three_strings, str))
        self.assertEqual(result_three_strings, '(Category.str.contains("value_1")|Category.str.contains("value_2")|Category.str.contains("value_3"))')

    def test_build_numeric_query_element(self):
        result_one_num = self.query.build_numeric_query_element('Category', [1])
        result_two_num = self.query.build_numeric_query_element('Category', [1, 2])
        result_three_num = self.query.build_numeric_query_element('Category', [1, 2, 3])
        self.assertTrue(isinstance(result_one_num, str))
        self.assertEqual(result_one_num, 'Category==1')
        self.assertTrue(isinstance(result_two_num, str))
        self.assertEqual(result_two_num, '(Category==1|Category==2)')
        self.assertTrue(isinstance(result_three_num, str))
        self.assertEqual(result_three_num, '(Category==1|Category==2|Category==3)')

    def test_build_boolean_query_element(self):
        result_true = self.query.build_boolean_query_element('Category', True)
        result_false = self.query.build_boolean_query_element('Category', False)
        self.assertTrue(isinstance(result_true, str))
        self.assertEqual(result_true, 'Category.isin([True])')
        self.assertTrue(isinstance(result_false, str))
        self.assertEqual(result_false, 'Category.isin([False])')

    @classmethod
    def tearDownClass(self):
        self.reference_df = None
        self.query = None
        self.query_params = None





class TestParser(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.input_df = Utility.get_df_from_archive('test_df.zip')
        self.parser = None

    def test_parse_input_df(self):
        self.parser = Parser(self.input_df)

    @classmethod
    def tearDownClass(self):
        self.input_df = None
        self.parser = None



class TestProcess(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.process = ProcessTracks()
        self.track_instance = Track(self.process.increment)
        self.library_tracks_df = None
        self.identifier_infos_df = None
        self.play_activity_df = None
        self.likes_dislikes_df = None

    def test_init_Process(self):
        self.assertTrue(isinstance(self.process, ProcessTracks))
        self.assertEqual(self.process.increment, 0)
        self.assertEqual(self.process.track_instance_dict, {})
        self.assertEqual(self.process.artist_tracks_titles, {})
        self.assertEqual(self.process.genres_list, [])
        self.assertEqual(self.process.items_not_matched, {'library_tracks':[], 'identifier_info':[],
                             'play_activity':[], 'likes_dislikes':[]})

    def test_get_track_instance_dict(self):
        self.process.track_instance_dict = {'key':'value', 'key_2':'value_2'}
        result = self.process.get_track_instance_dict()
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result), 2)
        self.process.track_instance_dict = {}

    def test_get_artist_tracks_titles(self):
        self.process.artist_tracks_titles = {'key':'value', 'key_2':'value_2'}
        result = self.process.get_artist_tracks_titles()
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result), 2)
        self.process.artist_tracks_titles = {}

    def test_get_increment(self):
        self.process.increment = 1
        result = self.process.get_increment()
        self.assertTrue(isinstance(result, int))
        self.assertEqual(result, 1)
        self.process.increment = 0

    def test_get_genres_list(self):
        self.process.genres_list = ['Genre', 'Other_genre']
        result = self.process.get_genres_list()
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 2)
        self.process.genres_list = []

    def test_get_items_not_matched(self):
        self.process.items_not_matched = {'library_tracks':['item'], 'identifier_info':['item', 'item_2'],
                             'play_activity':[], 'likes_dislikes':[]}
        result = self.process.get_items_not_matched()
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result), 4)
        self.assertEqual(list(result.keys()), ['library_tracks', 'identifier_info', 'play_activity', 'likes_dislikes'])
        self.assertEqual(len(result['library_tracks']), 1)
        self.assertEqual(len(result['identifier_info']), 2)
        self.process.items_not_matched = {'library_tracks':[], 'identifier_info':[],
                             'play_activity':[], 'likes_dislikes':[]}


    def test_compare_titles_for_artist(self):
        self.process.artist_tracks_titles = { 'Artist_1': ['Title_1', 'Other_Title'], 'Artist_2': ['Title_1', 'Other_Title'] }
        self.process.track_instance_dict = { 'Title_1 && Artist_1': self.track_instance }
        result_no_match = self.process.compare_titles_for_artist('Artist_1', 'Title_Very_Different')
        self.assertEqual(result_no_match, 'No match')
        result_match = self.process.compare_titles_for_artist('Artist_1', 'Title_2')
        self.assertTrue(isinstance(result_match, Track))
        self.process.artist_tracks_titles = {}
        self.process.track_instance_dict = {}


    def test_process_library_tracks_df(self):
        return None


    def test_process_identifier_df(self):
        return None


    def test_process_play_df(self):
        return None


    def test_process_likes_dislikes_df(self):
        return None

    @classmethod
    def tearDownClass(self):
        self.process = None



# self.process_tracks.process_library_tracks_df(self.library_tracks_df)
#         # we process the identifier infos
#         self.process_tracks.process_identifier_df(self.identifier_infos_df)
#         # we process the play activity
#         self.process_tracks.process_play_df(self.play_activity_df)
#         # we process the likes dislikes
#         self.process_tracks.process_likes_dislikes_df(self.likes_dislikes_df)



if __name__ == '__main__':
    unittest.main()