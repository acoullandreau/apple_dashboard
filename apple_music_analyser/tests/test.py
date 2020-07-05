import pandas as pd
import unittest
from unittest.mock import MagicMock

from apple_music_analyser.Utility import Utility
from apple_music_analyser.Track import Track
from apple_music_analyser.Query import Query, QueryFactory
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
                'offline':[],
                'library':[],
                'skipped':[],
            }
        self.assertTrue(isinstance(query, Query))
        self.assertEqual(query.reference_df.shape, self.reference_df.shape)
        self.assertEqual(query.reference_df.columns.tolist(), self.reference_df.columns.tolist())
        self.assertEqual(len(query.reference_df['Artist']), 2)
        self.assertEqual(len(query.query_params), len(query_params_default))
        self.assertEqual(len(query.query_params['year']), 2)
        self.assertEqual(query.query_params['genre'], [])

    # def test_query_creator_with_params(self):
    #     query_params = {
    #             'year':reference_df['Play_Year'].unique(),
    #             'genre':['Genre'],
    #             'artist':['Artist'],
    #             'title':['Title'],
    #             'rating':['LOVE'],
    #             'origin':['Library'],
    #             'offline':[False],
    #             'library':[True],
    #             'skipped':[False],
    #         }
    #     self.query.create_query(self.reference_df, query_params)
    #     self.assertTrue(isinstance(self.query, Query))
    #     self.assertEqual(self.query.reference_df, self.reference_df)
    #     self.assertEqual(self.query.query_params, query_params)


    @classmethod
    def tearDownClass(self):
        self.reference_df = None


if __name__ == '__main__':
    unittest.main()