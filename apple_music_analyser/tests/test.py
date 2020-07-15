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

    def test_parse_input_df(self):
        result = Parser.parse_input_df(self.input_df)
        # we expect a dictionary of dataframes
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result), 5)
        self.assertEqual(list(result.keys()), ['likes_dislikes_df', 'play_activity_df', 'identifier_infos_df', 'library_tracks_df', 'library_activity_df'])
        for i in range(len(list(result.values()))):
            self.assertTrue(isinstance(list(result.values())[i], pd.DataFrame))

    def test_parse_library_activity_df(self):
        library_activity_df = self.input_df['library_activity_df']
        shape_input_df = library_activity_df.shape
        result = Parser.parse_library_activity_df(library_activity_df)
        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assertEqual(result.shape[0], shape_input_df[0])
        self.assertEqual(result.shape[1], shape_input_df[1] + 8)
        self.assertIn('Transaction date time', result.columns)
        self.assertIn('Transaction Year', result.columns)
        self.assertIn('Transaction Month', result.columns)
        self.assertIn('Transaction DOM', result.columns)
        self.assertIn('Transaction DOW', result.columns)
        self.assertIn('Transaction HOD', result.columns)
        self.assertIn('Transaction HOD', result.columns)
        self.assertIn('Transaction Agent', result.columns)
        self.assertIn('Transaction Agent Model', result.columns)

    def test_parse_library_tracks_infos_df(self):
        library_tracks_df = self.input_df['library_tracks_df']
        shape_input_df = library_tracks_df.shape
        result = Parser.parse_library_tracks_infos_df(library_tracks_df)
        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assertEqual(result.shape[0], shape_input_df[0])
        self.assertEqual(result.shape[1], shape_input_df[1] - 34)
        # we reset the df

    def test_parse_likes_dislikes_df(self):
        likes_dislikes_df = self.input_df['likes_dislikes_df']
        shape_input_df = likes_dislikes_df.shape
        result = Parser.parse_likes_dislikes_df(likes_dislikes_df)
        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assertEqual(result.shape[0], shape_input_df[0])
        self.assertEqual(result.shape[1], shape_input_df[1] + 2)
        self.assertIn('Title', result.columns)
        self.assertIn('Artist', result.columns)

    def test_set_partial_listening(self):
        df = pd.DataFrame.from_dict({
            'End Reason Type':['NATURAL_END_OF_TRACK', 'SCRUB_END', 'FAILED_TO_LOAD'],
            'Play Duration Milliseconds':[111, 22222, 1234],
            'Media Duration In Milliseconds':[444, 3, 12345]
            })
        shape_input_df = df.shape
        Parser.set_partial_listening(df, df['End Reason Type'], df['Play Duration Milliseconds'], df['Media Duration In Milliseconds'])

        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertEqual(df.shape[0], shape_input_df[0])
        self.assertEqual(df.shape[1], shape_input_df[1] + 1)
        self.assertIn('Played completely', df.columns)
        self.assertEqual(df.iloc[0, 3], True)
        self.assertEqual(df.iloc[1, 3], True)
        self.assertEqual(df.iloc[2, 3], False)


    def test_get_track_origin(self):
        df = pd.DataFrame.from_dict({
            'Feature Name':['library / playlist_detail', 'my-music', 'for_you / personalized_mix / playlist_detail', 'now_playing', 'for_you / playlist_detail / album_detail',
            'browse', 'search:none / profile-all', 'for_you / recently_played / playlist_detail', 'Siri-actions-local', 'library / songs']
            })
        shape_input_df = df.shape
        df['Track origin'] = df['Feature Name'].apply(Parser.get_track_origin)
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertEqual(df.shape[0], shape_input_df[0])
        self.assertEqual(df.shape[1], shape_input_df[1] + 1)
        self.assertIn('Track origin', df.columns)
        self.assertEqual(df['Track origin'].tolist(), ['library', 'library', 'for you - personalized mix', 'other', 'for you - other', 'search', 'other', 'for you - recently played', 'other', 'library'])


    def test_compute_play_duration(self):
        df = pd.DataFrame.from_dict({
            'Event Start Timestamp':['2016-12-02T07:22:34.766Z', '', '2016-10-27T09:45:31.817Z'],
            'Event End Timestamp':['2016-12-02T07:25:34.766Z', '2019-06-19T15:51:09.477Z', '2016-10-27T09:47:36.482Z'],
            'Play Duration Milliseconds':[123, 5342, 60000],
            'Media Duration In Milliseconds':[123, 120000, 120000],
            'Played completely':[True, True, False]
            })

        shape_input_df = df.shape
        activity_start = pd.to_datetime(df['Event Start Timestamp'])
        activity_end = pd.to_datetime(df['Event End Timestamp'])
        played_completely = df['Played completely']
        play_duration = df['Play Duration Milliseconds']
        media_duration = df['Media Duration In Milliseconds']
        Parser.compute_play_duration(df, activity_start, activity_end, played_completely, play_duration, media_duration)

        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertEqual(df.shape[0], shape_input_df[0])
        self.assertEqual(df.shape[1], shape_input_df[1] + 1)
        self.assertEqual(int(df.iloc[0, 5]), 3)
        self.assertEqual(df.iloc[1, 5], 2)
        self.assertEqual(df.iloc[2, 5], 1)


    def test_remove_play_duration_outliers(self):
        df = pd.DataFrame.from_dict({
            'Play duration in minutes':[1, 4, 6, 999],
            'Media Duration In Milliseconds':[123, 345, 678, 120000],
            })

        shape_input_df = df.shape
        duration_minutes = df['Play duration in minutes']
        media_duration = df['Media Duration In Milliseconds']
        percentile = df['Play duration in minutes'].quantile(0.99)
        Parser.remove_play_duration_outliers(df, duration_minutes, media_duration, percentile)
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertEqual(df.shape[0], shape_input_df[0])
        self.assertEqual(df.shape[1], shape_input_df[1])
        self.assertEqual(int(df.iloc[0, 0]), 1)
        self.assertEqual(df.iloc[1, 0], 4)
        self.assertEqual(df.iloc[2, 0], 6)
        self.assertEqual(df.iloc[3, 0], 2)

    def test_parse_play_activity_df(self):
        play_activity_df = self.input_df['play_activity_df']
        shape_input_df = play_activity_df.shape
        result = Parser.parse_play_activity_df(play_activity_df)
        self.assertTrue(isinstance(result, pd.DataFrame))
        #we expect 1 row with date before 2015 to be dropped
        self.assertEqual(result.shape[0], shape_input_df[0] -1)
        self.assertEqual(result.shape[1], shape_input_df[1] -14)
        self.assertIn('Play date time', result.columns)
        self.assertIn('Play Year', result.columns)
        self.assertIn('Play Month', result.columns)
        self.assertIn('Play DOM', result.columns)
        self.assertIn('Play DOW', result.columns)
        self.assertIn('Play HOD', result.columns)
        self.assertIn('Play HOD', result.columns)
        self.assertIn('Played completely', result.columns)
        self.assertIn('Track origin', result.columns)
        self.assertIn('Play duration in minutes', result.columns)


    def test_init_Parser(self):
        input_df = Utility.get_df_from_archive('test_df.zip')
        shape_input_likes_dislikes_df = input_df['likes_dislikes_df'].shape
        shape_input_play_activity_df = input_df['play_activity_df'].shape
        shape_input_identifier_infos_df = input_df['identifier_infos_df'].shape
        shape_input_library_tracks_df = input_df['library_tracks_df'].shape
        shape_input_library_activity_df = input_df['library_activity_df'].shape
        result = Parser(input_df)
        self.assertTrue(isinstance(result.likes_dislikes_df, pd.DataFrame))
        self.assertEqual(result.likes_dislikes_df.shape, (shape_input_likes_dislikes_df[0], shape_input_likes_dislikes_df[1] + 2))
        self.assertTrue(isinstance(result.play_activity_df, pd.DataFrame))
        self.assertEqual(result.play_activity_df.shape, (shape_input_play_activity_df[0] - 1, shape_input_play_activity_df[1] - 14))
        self.assertTrue(isinstance(result.identifier_infos_df, pd.DataFrame))
        self.assertEqual(result.identifier_infos_df.shape, (shape_input_identifier_infos_df[0], shape_input_identifier_infos_df[1]))
        self.assertTrue(isinstance(result.library_tracks_df, pd.DataFrame))
        self.assertEqual(result.library_tracks_df.shape, (shape_input_library_tracks_df[0], shape_input_library_tracks_df[1] - 34))
        self.assertTrue(isinstance(result.library_activity_df, pd.DataFrame))
        self.assertEqual(result.library_activity_df.shape, (shape_input_library_activity_df[0], shape_input_library_activity_df[1] + 8))

    @classmethod
    def tearDownClass(self):
        self.input_df = None




class TestProcess(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        input_df = Utility.get_df_from_archive('test_df.zip')
        self.parser = Parser(input_df)
        self.likes_dislikes_df = self.parser.likes_dislikes_df
        self.play_activity_df = self.parser.play_activity_df
        self.identifier_infos_df = self.parser.identifier_infos_df
        self.library_tracks_df = self.parser.library_tracks_df
        self.library_activity_df = self.parser.library_activity_df
        self.process = ProcessTracks()
        self.track_instance = Track(self.process.increment)

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


    def test_update_track_instance_play(self):
        index_play = 50
        row_play = self.play_activity_df.iloc[50]
        self.process.update_track_instance('play_activity_df', self.track_instance, index_play, row_play)
        self.assertEqual(self.process.genres_list, ['Soundtrack'])
        self.assertEqual(self.track_instance.genre, ['Soundtrack'])
        self.assertEqual(self.track_instance.appearances, [{'source': 'play_activity', 'df_index': 50}])
        self.process.genres_list = []
        self.track_instance.genre = []
        self.track_instance.appearances = []

    def test_update_track_instance_lib(self):
        index_lib = 30
        row_lib = self.library_tracks_df.iloc[30]
        self.process.update_track_instance('library_tracks_df', self.track_instance, index_lib, row_lib)
        self.assertEqual(self.process.genres_list, ['French Pop'])
        self.assertEqual(self.track_instance.genre, ['French Pop'])
        self.assertEqual(self.track_instance.appearances, [{'source': 'library_tracks', 'df_index': 30}])
        self.process.genres_list = []
        self.track_instance.genre = []
        self.track_instance.appearances = []

    # def test_update_track_instance_other(self):
    #     index_other = 10
    #     row_other = self.identifier_infos_df.iloc[10]
    #     self.process.update_track_instance('identifier_infos_df', self.track_instance, index_other, row_other)
    #     self.assertEqual(self.process.genres_list, [])
    #     self.assertEqual(self.track_instance.genre, [])
    #     self.assertEqual(self.track_instance.appearances, [])


    def test_process_library_tracks_df(self):
        self.process.process_library_tracks_df(self.library_tracks_df)
        self.assertEqual(len(self.process.track_instance_dict), 35)
        self.assertIn('Clandestino && Manu Chao', self.process.track_instance_dict.keys())
        self.assertEqual(len(self.process.artist_tracks_titles), 29)
        self.assertEqual(len(self.process.artist_tracks_titles['Céline Dion']), 3)
        self.assertEqual(len(self.process.genres_list), 16)
        self.process.genres_list = []
        self.process.artist_tracks_titles = {}
        self.process.track_instance_dict = {}
        self.process.increment = 0
        self.process.items_not_matched = {'library_tracks':[], 'identifier_info':[],
                     'play_activity':[], 'likes_dislikes':[]}


    def test_process_identifier_df(self):
        # we expect modifications of the process objects only if they are not empty
        self.process.process_identifier_df(self.identifier_infos_df)
        self.assertEqual(self.process.track_instance_dict, {})
        self.assertEqual(self.process.genres_list, [])
        self.assertEqual(self.process.artist_tracks_titles, {})
        self.assertEqual(self.process.increment, 0)

    def test_process_play_df(self):
        self.process.process_play_df(self.play_activity_df)
        self.assertEqual(self.process.increment, 110)
        # because the Genre nan is associated to a row without title it is dropped in the process
        self.assertEqual(len(self.process.genres_list), 25)
        self.assertEqual(len(self.process.track_instance_dict), 110)
        self.assertEqual(self.process.track_instance_dict['The Unforgiven && Metallica'].titles, ['The Unforgiven'])
        self.assertEqual(self.process.track_instance_dict['The Unforgiven && Metallica'].artist, 'Metallica')
        self.assertEqual(self.process.track_instance_dict['The Unforgiven && Metallica'].appearances, [{'source': 'play_activity', 'df_index': 101}, {'source': 'play_activity', 'df_index': 153}, {'source': 'play_activity', 'df_index': 154}])
        self.assertEqual(self.process.track_instance_dict['The Unforgiven && Metallica'].genre, ['Heavy Metal'])
        self.assertEqual(self.process.track_instance_dict['The Unforgiven && Metallica'].identifier, 70)
        self.assertEqual(self.process.track_instance_dict['The Unforgiven && Metallica'].is_in_lib, True)
        # these info come from other df, so they should remain empty
        self.assertEqual(self.process.track_instance_dict['The Unforgiven && Metallica'].rating, [])
        self.assertEqual(self.process.track_instance_dict['The Unforgiven && Metallica'].apple_music_id, [])
        self.assertIn('The Unforgiven', self.process.artist_tracks_titles['Metallica'])
        self.assertEqual(self.process.items_not_matched, {'library_tracks': [], 'identifier_info': [], 'play_activity': [0, 1, 2, 3, 96, 116, 165], 'likes_dislikes': []})
        self.process.genres_list = []
        self.process.artist_tracks_titles = {}
        self.process.track_instance_dict = {}
        self.process.increment = 0
        self.process.items_not_matched = {'library_tracks':[], 'identifier_info':[],
                     'play_activity':[], 'likes_dislikes':[]}



    def test_process_likes_dislikes_df(self):
        return None


    def test_process_all_df(self):
        self.process.process_library_tracks_df(self.library_tracks_df)
        self.process.process_identifier_df(self.identifier_infos_df)
        self.process.process_play_df(self.play_activity_df)
        self.process.process_likes_dislikes_df(self.likes_dislikes_df)
        #self.assertEqual(len(self.process.track_instance_dict), )
        #self.assertEqual(len(self.process.artist_tracks_titles), )
        #self.assertEqual(len(self.process.genres_list), )
        #self.assertEqual(len(self.process.increment), )
        #self.assertEqual(len(self.process.items_not_matched), )
        #look at titles, appeareances of a song in particular
        self.process.increment = 0
        self.process.genres_list = []
        self.process.artist_tracks_titles = {}
        self.process.track_instance_dict = {}
        self.process.items_not_matched = {'library_tracks':[], 'identifier_info':[],
                     'play_activity':[], 'likes_dislikes':[]}



    @classmethod
    def tearDownClass(self):
        self.process = None
        self.parser = None
        self.likes_dislikes_df = None
        self.play_activity_df = None
        self.identifier_infos_df = None
        self.library_tracks_df = None
        self.library_activity_df = None
        self.track_instance = None



    # def process_library_tracks_df(self, library_df):
    #     '''
    #         This function goes through each row of the library tracks dataframe, creating and updating
    #         track instances as they appear.
    #         As this is the first dataframe we go through, we want to create new instances whenever
    #         we are not facing unknown songs (NaN as a title)
    #         The logic works as follows, knowing that we do this for each row of the dataframe:
    #             - we look only at rows with a title different than NaN, and we set the artist to
    #             'No Artist' if the artist is also Nan
    #             - if the track is not in the dictionary of track instances, it means that we never
    #             saw the combination title/artist of this row. So two options here:
    #                 - either we know this artist and we can find a similar title in the artist dict, and in
    #                 this case we update the existing track using update_track_from_library
    #                 - or we do not know this artist, or we do not find a close match of title for this artist
    #                 and in this case we create a new track instance using instantiate_track and then
    #                 update_track_from_library
    #             - else, we update the existing track using update_track_from_library
    #     '''
    #     for index, row in library_df.iterrows():
    #         if str(row['Title']) != 'nan':
    #             title = row['Title']
    #             if str(row['Artist']) != 'nan':
    #                 artist = row['Artist']
    #             else:
    #                 artist = 'No Artist'

    #             title_artist = Utility.concat_title_artist(title, artist)

    #             if title_artist not in self.track_instance_dict.keys():
    #                 if artist in self.artist_tracks_titles.keys():
    #                     titles_comparison_result = self.compare_titles_for_artist(artist, title)

    #                     if titles_comparison_result == 'No match':
    #                         #we instantiate the Track object
    #                         track_instance = Track(self.increment)
    #                         track_instance.instantiate_track(title, artist)
    #                         self.update_track_instance('library_tracks_df', track_instance, index, row, title_artist)
    #                         self.track_instance_dict[title_artist] = track_instance
    #                         self.increment += 1

    #                     else:
    #                         track_instance = titles_comparison_result
    #                         if not track_instance.has_title_name(title):
    #                             track_instance.add_title(title)
    #                         self.update_track_instance('library_tracks_df', track_instance, index, row, title_artist)
    #                         self.track_instance_dict[title_artist] = track_instance
    #                         self.artist_tracks_titles[artist].append(title)
                    
    #                 else:
    #                     #there was no close match, and the song was never seen, so we instantiate a new Track
    #                     track_instance = Track(self.increment)
    #                     track_instance.instantiate_track(title, artist)
    #                     self.update_track_instance('library_tracks_df', track_instance, index, row, title_artist)
    #                     self.track_instance_dict[title_artist] = track_instance
    #                     self.increment += 1


    #             else:
    #                 track_instance = self.track_instance_dict[title_artist]
    #                 self.update_track_instance('library_tracks_df', track_instance, index, row, title_artist)


    #             #we update the artist/track names dictionnary
    #             if artist not in self.artist_tracks_titles:
    #                 self.artist_tracks_titles[artist]=[]
    #             if title not in self.artist_tracks_titles[artist]:
    #                 self.artist_tracks_titles[artist].append(title)
    #         else:
    #             self.items_not_matched['library_tracks'].append(index)



    # def process_identifier_df(self, identifier_df):
    #     '''
    #         This function goes through each row of the identifier information dataframe, updating
    #         track instances as they appear.
    #         Unlike for the tracks dataframe, we have very limited information here, just an identifier
    #         and a title (not even an artist name). So we need to have a different approach, only
    #         based on the identifiers. Which may excluse some songs... But prevents false positives.
    #         The logic works as follows, knowing that we do this for each row of the dataframe:
    #             - we loop through all the track instances we created so far, and see if any of their 
    #             identifier matches the id of the row we are looking at
    #             - if it matches, and if we didn't already have the associated title, we add it to the
    #             list of titles of that track
    #             - otherwise, we add it to the tracks we could not match and we ignored.
    #     '''
    #     for index, row in identifier_df.iterrows():
    #         found_match = False
    #         for title_name in self.track_instance_dict.keys():
    #             track_instance = self.track_instance_dict[title_name]
    #             if row['Identifier'] in track_instance.apple_music_id:
    #                 track_instance.add_appearance({'source': 'identifier_info', 'df_index':index})
    #                 if not track_instance.has_title_name(row['Title']):
    #                     track_instance.add_title(row['Title'])
    #                 found_match = True
    #                 break
    #         if found_match is False:
    #             self.items_not_matched['identifier_info'].append((index, row['Identifier']))


    # def process_play_df(self, play_activity_df):
    #     '''
    #         This function goes through each row of the play activity dataframe, creating and updating
    #         track instances as they appear.
    #         As this is the dataframe we are able to get the most information from, we want to create
    #         new instances whenever we are not facing unknown songs (NaN as a title).The approach is
    #         very similar to the one used for the library tracks.
            
    #         The logic works as follows, knowing that we do this for each row of the dataframe:
    #             - if the track is in the dictionary of track instances, we update the existing
    #             track using update_track_from_play_activity
    #             - else, we have two options :
    #                 - either we know this artist and we can find a similar title in the artist dict,
    #                 and in this case we update the existing track using update_track_from_play_activity
    #                 - or we do not know this artist, or we do not find a close match of title for this
    #                 artist and in this case we create a new track instance using instantiate_track and
    #                 then update_track_from_play_activity
    #     '''
    #     for index, row in play_activity_df.iterrows():
    #         #we want to look only at rows where the name of the song is available
    #         if str(row['Title']) != 'nan':
    #             title = row['Title']
    #             if str(row['Artist']) != 'nan':
    #                 artist = row['Artist']
    #             else:
    #                 artist = 'No Artist'
    #         else:
    #             self.items_not_matched['play_activity'].append(index)
    #             continue

    #         #we check if we already saw this track (using title and artist names)
    #         title_artist = Utility.concat_title_artist(title, artist)
    #         if title_artist in self.track_instance_dict.keys():
    #             track_instance = self.track_instance_dict[title_artist]
    #             self.update_track_instance('play_activity_df', track_instance, index, row, title_artist)

    #         else:
    #             # if we had no match with title and artist, we look for similarity in the title for the artist
    #             if artist in self.artist_tracks_titles.keys():
    #                 titles_comparison_result = self.compare_titles_for_artist(artist, title)
    #                 if titles_comparison_result == 'No match':
    #                     #we instantiate the Track object
    #                     track_instance = Track(self.increment)
    #                     track_instance.instantiate_track(title, artist)
    #                     self.update_track_instance('play_activity_df', track_instance, index, row, title_artist)
    #                     #we update the dictionary that keeps track of our instances, and increment
    #                     self.track_instance_dict[title_artist] = track_instance
    #                     self.increment+=1

    #                 else:
    #                     track_instance = titles_comparison_result
    #                     if not track_instance.has_title_name(title):
    #                         track_instance.add_title(title)
    #                     track_instance.add_appearance({'source': 'play_activity', 'df_index':index})
    #                     #we also track the match in the track_instances and artist dicts
    #                     self.track_instance_dict[title_artist] = track_instance
    #                     self.artist_tracks_titles[artist].append(title)

    #             # else we know we never saw this track because the artist is unknown      
    #             else:
    #                 #we update the artist/track names dictionnary
    #                 self.artist_tracks_titles[artist]=[]
    #                 self.artist_tracks_titles[artist].append(title)

    #                 #we instantiate the Track object
    #                 track_instance = Track(self.increment)
    #                 track_instance.instantiate_track(title, artist)
    #                 self.update_track_instance('play_activity_df', track_instance, index, row, title_artist)

    #                 #we update the dictionary that keeps track of our instances, and increment
    #                 self.track_instance_dict[title_artist] = track_instance
    #                 self.increment+=1

    # def process_likes_dislikes_df(self, likes_dislikes_df):
    #     '''
    #         This function goes through each row of the likes_dislikes dataframe, updating
    #         track instances as they appear.
    #         This dataframe contains a small proportion of all the tracks ever listened to, and/or in
    #         the library. As a result, we only want to update existing tracks, and not create new ones.
    #         The logic works as follows, knowing that we do this for each row of the dataframe:
    #             - we loop through all the track instances we created so far, and see if any of their 
    #             identifier matches the id of the row we are looking at
    #             - if we find a match, we update the track with the rating, appearance, and if we didn't
    #             already have the associated title, we add it to the list of titles of that track
    #             - else:
    #                 - if the track is in the dictionary of track instances, we update the existing
    #             track's rating and appearance
    #                 - otherwise, we have two options:
    #                     - either we know the artist and we can find a similar title in the artist dict,
    #                 and in this case we update the existing track
    #                     - or we do not know this artist, or we do not find a close match of title for this
    #                 artist and in this case we add it to the tracks we could not match and we ignored
    #     ''' 
    #     for index, row in likes_dislikes_df.iterrows():
    #         #we want to look only at rows where the name of the song is available
    #         if str(row['Title']) != 'nan':
    #             title = row['Title']
    #             if str(row['Artist']) != 'nan':
    #                 artist = row['Artist']
    #             else:
    #                 artist = 'No Artist'
    #         else:
    #             self.items_not_matched['likes_dislikes'].append(index)
    #             continue

    #         title_artist = Utility.concat_title_artist(title, artist)

    #         # first we check using the Item Reference as an id
    #         found_match = False
    #         for title_name in self.track_instance_dict.keys():
    #             track_instance = self.track_instance_dict[title_name]
    #             if row['Item Reference'] in track_instance.apple_music_id:
    #                 track_instance.add_appearance({'source': 'likes_dislikes', 'df_index':index})
    #                 track_instance.set_rating(row['Preference'])
    #                 if not track_instance.has_title_name(row['Title']):
    #                     track_instance.add_title(row['Title'])
    #                     self.track_instance_dict[title_artist] = track_instance
    #                     if row['Title'] not in self.artist_tracks_titles[artist]:
    #                         self.artist_tracks_titles[artist].append(title)
    #                 found_match = True
    #                 break

    #         if found_match is False:
    #             #we check if we already saw this track (using title and artist names)
    #             if title_artist in self.track_instance_dict.keys():
    #                 track_instance = self.track_instance_dict[title_artist]
    #                 track_instance.add_appearance({'source': 'likes_dislikes', 'df_index':index})
    #                 track_instance.set_rating(row['Preference'])

    #             else:
    #                 # if we had no match with title and artist, we look for similarity in the title for the artist
    #                 if artist in self.artist_tracks_titles.keys():
    #                     titles_comparison_result = self.compare_titles_for_artist(artist, title)
    #                     if titles_comparison_result == 'No match':
    #                         #we add the item to the items_not_matched
    #                         self.items_not_matched['likes_dislikes'].append(index)
    #                         #continue
    #                     else:
    #                         track_instance = titles_comparison_result
    #                         if not track_instance.has_title_name(title):
    #                             track_instance.add_title(title)
    #                         track_instance.add_appearance({'source': 'likes_dislikes', 'df_index':index})
    #                         track_instance.set_rating(row['Preference'])
    #                         self.track_instance_dict[title_artist] = track_instance
    #                         self.artist_tracks_titles[artist].append(title)
    #                 else:
    #                     #we add the item to the items_not_matched,
    #                     #we choose not to add it to the Track instances as the amount of information is little
    #                     #and our reference really is the play activity!
    #                     self.items_not_matched['likes_dislikes'].append(index)
    #                     continue





# self.process_tracks.process_library_tracks_df(self.library_tracks_df)
#         # we process the identifier infos
#         self.process_tracks.process_identifier_df(self.identifier_infos_df)
#         # we process the play activity
#         self.process_tracks.process_play_df(self.play_activity_df)
#         # we process the likes dislikes
#         self.process_tracks.process_likes_dislikes_df(self.likes_dislikes_df)



if __name__ == '__main__':
    unittest.main()