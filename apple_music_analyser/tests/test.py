import pandas as pd
import unittest
from unittest.mock import MagicMock

from apple_music_analyser.Utility import Utility
from apple_music_analyser.Track import Track
from apple_music_analyser.Query import Query, QueryFactory
from apple_music_analyser.Parser import Parser
from apple_music_analyser.Process import ProcessTracks, TrackSummaryObject
#from apple_music_analyser.VisualizationDataframe import VisualizationDataframe


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
    def setUp(self):
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


    def test_add_appearance(self):
        appearance_dict = {'source': 'source', 'df_index':'index'}
        self.track.add_appearance(appearance_dict)
        self.assertEqual(self.track.appearances, [{'source': 'source', 'df_index':'index'}])

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

    @classmethod
    def tearDown(self):
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
    def setUp(self):
        self.input_df = Utility.get_df_from_archive('test_df.zip')
        self.parser = Parser(self.input_df)
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

    def test_get_artist_tracks_titles(self):
        self.process.artist_tracks_titles = {'key':'value', 'key_2':'value_2'}
        result = self.process.get_artist_tracks_titles()
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result), 2)

    def test_get_increment(self):
        self.process.increment = 1
        result = self.process.get_increment()
        self.assertTrue(isinstance(result, int))
        self.assertEqual(result, 1)

    def test_get_genres_list(self):
        self.process.genres_list = ['Genre', 'Other_genre']
        result = self.process.get_genres_list()
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 2)

    def test_get_items_not_matched(self):
        self.process.items_not_matched = {'library_tracks':['item'], 'identifier_info':['item', 'item_2'],
                             'play_activity':[], 'likes_dislikes':[]}
        result = self.process.get_items_not_matched()
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result), 4)
        self.assertEqual(list(result.keys()), ['library_tracks', 'identifier_info', 'play_activity', 'likes_dislikes'])
        self.assertEqual(len(result['library_tracks']), 1)
        self.assertEqual(len(result['identifier_info']), 2)


    def test_compare_titles_for_artist(self):
        self.process.artist_tracks_titles = { 'Artist_1': ['Title_1', 'Other_Title'], 'Artist_2': ['Title_1', 'Other_Title'] }
        self.process.track_instance_dict = { 'Title_1 && Artist_1': self.track_instance }
        result_no_match = self.process.compare_titles_for_artist('Artist_1', 'Title_Very_Different')
        self.assertEqual(result_no_match, 'No match')
        result_match = self.process.compare_titles_for_artist('Artist_1', 'Title_2')
        self.assertTrue(isinstance(result_match, Track))


    def test_update_track_instance_play(self):
        index_play = 50
        row_play = self.play_activity_df.iloc[50]
        self.process.update_track_instance('play_activity_df', self.track_instance, index_play, row_play)
        self.assertEqual(self.process.genres_list, ['Soundtrack'])
        self.assertEqual(self.track_instance.genre, ['Soundtrack'])
        self.assertEqual(self.track_instance.appearances, [{'source': 'play_activity', 'df_index': 50}])

    def test_update_track_instance_lib(self):
        index_lib = 30
        row_lib = self.library_tracks_df.iloc[30]
        self.process.update_track_instance('library_tracks_df', self.track_instance, index_lib, row_lib)
        self.assertEqual(self.process.genres_list, ['French Pop'])
        self.assertEqual(self.track_instance.genre, ['French Pop'])
        self.assertEqual(self.track_instance.appearances, [{'source': 'library_tracks', 'df_index': 30}])

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
        self.assertEqual(self.process.items_not_matched['library_tracks'], [])

    def test_process_identifier_df(self):
        # we expect modifications of the process objects only if they are not empty
        self.process.process_identifier_df(self.identifier_infos_df)
        self.assertEqual(self.process.track_instance_dict, {})
        self.assertEqual(self.process.genres_list, [])
        self.assertEqual(self.process.artist_tracks_titles, {})
        self.assertEqual(self.process.increment, 0)
        self.assertEqual(len(self.process.items_not_matched['identifier_info']), self.identifier_infos_df.shape[0])

    def test_process_play_df(self):
        self.process.process_play_df(self.play_activity_df)
        self.assertEqual(self.process.increment, 110)
        # because the Genre nan is associated to a row without title it is dropped in the process
        self.assertEqual(len(self.process.genres_list), 25)
        self.assertEqual(len(self.process.track_instance_dict), 110)
        self.assertEqual(len(self.process.artist_tracks_titles), 89)
        self.assertEqual(self.process.track_instance_dict['The Unforgiven && Metallica'].titles, ['The Unforgiven'])
        self.assertEqual(self.process.track_instance_dict['The Unforgiven && Metallica'].artist, 'Metallica')
        self.assertEqual(self.process.track_instance_dict['The Unforgiven && Metallica'].appearances, [{'source': 'play_activity', 'df_index': 101}, {'source': 'play_activity', 'df_index': 153}, {'source': 'play_activity', 'df_index': 154}])
        self.assertEqual(self.process.track_instance_dict['The Unforgiven && Metallica'].genre, ['Heavy Metal'])
        self.assertEqual(self.process.track_instance_dict['The Unforgiven && Metallica'].identifier, 70)
        self.assertEqual(self.process.track_instance_dict['The Unforgiven && Metallica'].is_in_lib, True)
        self.assertIn('The Unforgiven', self.process.artist_tracks_titles['Metallica'])
        # rows with NaN as the title are added to items_not_matched
        self.assertEqual(self.process.items_not_matched['play_activity'], [0, 1, 2, 3, 96, 116, 165])
        # these info come from other df, so they should remain empty
        self.assertEqual(self.process.track_instance_dict['The Unforgiven && Metallica'].rating, [])
        self.assertEqual(self.process.track_instance_dict['The Unforgiven && Metallica'].apple_music_id, [])


    def test_process_likes_dislikes_df(self):
        # we expect modifications of the process objects only if they are not empty
        self.process.process_likes_dislikes_df(self.likes_dislikes_df)
        self.process.process_identifier_df(self.identifier_infos_df)
        self.assertEqual(self.process.track_instance_dict, {})
        self.assertEqual(self.process.genres_list, [])
        self.assertEqual(self.process.artist_tracks_titles, {})
        self.assertEqual(self.process.increment, 0)
        self.assertEqual(len(self.process.items_not_matched['likes_dislikes']), self.likes_dislikes_df.shape[0])


    def test_process_all_df(self):
        self.process.process_library_tracks_df(self.library_tracks_df)
        self.process.process_identifier_df(self.identifier_infos_df)
        self.process.process_play_df(self.play_activity_df)
        self.process.process_likes_dislikes_df(self.likes_dislikes_df)
        # in the test df, there are 3 tracks with similar names
        # and 15 common tracks (among them one is already counted in the 3 similarly named tracks)
        # so we want to validate that the number of track instances is :
        # 110 (play_activity tracks) + 35 (library tracks) - 3 - 14 = 128
        # and that increment is one unit above, so 129
        self.assertEqual(self.process.increment, 129)
        # and that we have 132 entries in track_instance_dict (110 (play_activity tracks) + 35 (library tracks) - 14 (common) + 3 (similar names))
        self.assertEqual(len(self.process.track_instance_dict), 132)
        # there are 10 songs labeled with the same genre, so output genres_list should have 31 values
        self.assertEqual(len(self.process.genres_list), 31)
        #the items not matched of library_tracks_df and play_activity_df should be the same than in the individual test functions defined above
        self.assertEqual(self.process.items_not_matched['play_activity'], [0, 1, 2, 3, 96, 116, 165])
        self.assertEqual(self.process.items_not_matched['library_tracks'], [])
        # but for the other df the values are different!
        # for likes and dislikes, we expect 7 rows to be unmatched
        self.assertEqual(self.process.items_not_matched['likes_dislikes'], [3, 4, 5, 10, 19, 20, 21])
        # for increment actually many more! Total of 51 unmatched, because we use the identifier as a key to match, and not the title
        self.assertEqual(len(self.process.items_not_matched['identifier_info']), 51)
        # we expect to find 19 common artists, so the length of artist_tracks_titles should be 29 + 89 - 19 = 99 
        self.assertEqual(len(self.process.artist_tracks_titles), 99)
        #and the artist with the more songs should be Michele McLaughlin with 5 tracks
        max_artist = max(self.process.artist_tracks_titles, key=lambda x:len(self.process.artist_tracks_titles[x]))
        max_value = len(self.process.artist_tracks_titles[max_artist])
        self.assertEqual(max_artist, 'Michele McLaughlin')
        self.assertEqual(max_value, 5)

        #now we focus on one song that appears in multiple df
        self.assertEqual(self.process.track_instance_dict['Nicolas Le Floch - Générique && Stéphane Moucha'].titles, ['Nicolas Le Floch - Générique', 'Nicolas Le Floch'])
        self.assertEqual(self.process.track_instance_dict['Nicolas Le Floch - Générique && Stéphane Moucha'].artist, 'Stéphane Moucha')
        self.assertEqual(self.process.track_instance_dict['Nicolas Le Floch - Générique && Stéphane Moucha'].appearances, [{'source': 'library_tracks', 'df_index': 10}, {'source': 'identifier_info', 'df_index': 14}, {'source': 'play_activity', 'df_index': 72}, {'source': 'likes_dislikes', 'df_index': 28}])
        self.assertEqual(self.process.track_instance_dict['Nicolas Le Floch - Générique && Stéphane Moucha'].identifier, 9)
        # we verify that the track is indeed in the library and properly flagged
        self.assertIn('Nicolas Le Floch - Générique', self.library_tracks_df['Title'].unique())
        self.assertEqual(self.process.track_instance_dict['Nicolas Le Floch - Générique && Stéphane Moucha'].is_in_lib, True)
        #we verify that the genre assigned to the track matches in all df available
        self.assertEqual(self.process.track_instance_dict['Nicolas Le Floch - Générique && Stéphane Moucha'].genre, self.library_tracks_df[self.library_tracks_df['Title']=='Nicolas Le Floch - Générique']['Genre'].values)
        self.assertEqual(self.process.track_instance_dict['Nicolas Le Floch - Générique && Stéphane Moucha'].genre, self.play_activity_df[self.play_activity_df['Title']=='Nicolas Le Floch - Générique']['Genre'].values)
        self.assertIn('Nicolas Le Floch - Générique', self.process.artist_tracks_titles['Stéphane Moucha'])
        #we verify that the rating corresponds to the value in likes_dislikes_df
        #note that in likes_dislikes_df the song rated is represented by the same track, but a different title!
        self.assertEqual(self.process.track_instance_dict['Nicolas Le Floch - Générique && Stéphane Moucha'].rating, self.likes_dislikes_df[self.likes_dislikes_df['Title']=='Nicolas Le Floch']['Preference'].values)
        #we verify that the apple id corresponds to the value in identifier_infos_df
        self.assertEqual(self.process.track_instance_dict['Nicolas Le Floch - Générique && Stéphane Moucha'].apple_music_id, self.identifier_infos_df[self.identifier_infos_df['Title']=='Nicolas Le Floch - Générique']['Identifier'].values)
        #let's note here that this value has to be also available in library_tracks_df, as the match from identifier_infos_df are made on the ids and not the titles
        ids_from_library = [int(x) for x in self.library_tracks_df[self.library_tracks_df['Title']=='Nicolas Le Floch - Générique'][['Apple Music Track Identifier', 'Track Identifier', 'Purchased Track Identifier', 'Tag Matched Track Identifier']].values[0]]
        self.assertIn(int(self.process.track_instance_dict['Nicolas Le Floch - Générique && Stéphane Moucha'].apple_music_id[0]), ids_from_library)


    @classmethod
    def tearDown(self):
        self.process = None
        self.parser = None
        self.likes_dislikes_df = None
        self.play_activity_df = None
        self.identifier_infos_df = None
        self.library_tracks_df = None
        self.library_activity_df = None
        self.track_instance = None





class TestProcessTrackSummaryObject(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        #we use the test df
        self.input_df = Utility.get_df_from_archive('test_df.zip')
        self.parser = Parser(self.input_df)
        self.likes_dislikes_df = self.parser.likes_dislikes_df
        self.play_activity_df = self.parser.play_activity_df
        self.identifier_infos_df = self.parser.identifier_infos_df
        self.library_tracks_df = self.parser.library_tracks_df
        self.library_activity_df = self.parser.library_activity_df
        #we process the df
        self.process = ProcessTracks()
        self.process.process_library_tracks_df(self.library_tracks_df)
        self.process.process_identifier_df(self.identifier_infos_df)
        self.process.process_play_df(self.play_activity_df)
        self.process.process_likes_dislikes_df(self.likes_dislikes_df)
        #we extract the useful objects from the process instance
        self.track_instance_dict = self.process.track_instance_dict
        self.artist_tracks_titles = self.process.artist_tracks_titles
        self.genres_list = self.process.genres_list
        self.items_not_matched = self.process.items_not_matched


    def test_init_TrackSummaryObject(self):
        result = TrackSummaryObject(self.track_instance_dict, self.artist_tracks_titles, self.genres_list, self.items_not_matched)
        # we verify that the track_instance_dict of the TrackSummaryObject is the one we passed as an input
        self.assertEqual(result.track_instance_dict, self.track_instance_dict)
        #idem for artist_tracks_titles and items_not_matched
        self.assertEqual(result.artist_tracks_titles, self.artist_tracks_titles)
        self.assertEqual(result.items_not_matched, self.items_not_matched)
        # genres_list has only one item to clean up, the nan item
        self.assertEqual(len(result.genres_list), len(self.genres_list))
        self.assertIn('', result.genres_list)
        #we validate that a new object is available for the TrackSummaryObject object
        self.assertEqual(result.match_index_instance, {})


    def test_get_track_instance_dict(self):
        track_summary_object = TrackSummaryObject(self.track_instance_dict, self.artist_tracks_titles, self.genres_list, self.items_not_matched)
        result = track_summary_object.get_track_instance_dict()
        self.assertEqual(result, self.track_instance_dict)

    def test_get_artist_tracks_titles(self):
        track_summary_object = TrackSummaryObject(self.track_instance_dict, self.artist_tracks_titles, self.genres_list, self.items_not_matched)
        result = track_summary_object.get_artist_tracks_titles()
        self.assertEqual(result, self.artist_tracks_titles)

    def test_get_genres_list(self):
        track_summary_object = TrackSummaryObject(self.track_instance_dict, self.artist_tracks_titles, self.genres_list, self.items_not_matched)
        result = track_summary_object.get_genres_list()
        self.assertEqual(len(result), len(self.genres_list))
        self.assertIn('', result)

    def test_get_items_not_matched(self):
        track_summary_object = TrackSummaryObject(self.track_instance_dict, self.artist_tracks_titles, self.genres_list, self.items_not_matched)
        result = track_summary_object.get_items_not_matched()
        self.assertEqual(result, self.items_not_matched)

    def test_get_match_index_instance(self):
        track_summary_object = TrackSummaryObject(self.track_instance_dict, self.artist_tracks_titles, self.genres_list, self.items_not_matched)
        result = track_summary_object.get_match_index_instance()
        self.assertEqual(result, {})


# class TrackSummaryObject():

#     def build_index_track_instance_dict(self, target_df_label):
#         '''
#             Returns a dictionary matching the index of the target dataframe with a reference to its
#             associated Track instance.
            
#             Argument can be of four types, for the four df we used to build the Track instances:
#                 - play_activity
#                 - library_tracks
#                 - likes_dislikes
#                 - identifier_infos
#         '''
#         for title_artist in self.track_instance_dict.keys():
#             instance = self.track_instance_dict[title_artist]
#             for appearance in instance.appearances:
#                 if target_df_label in appearance['source']:
#                     if appearance['df_index'] not in self.match_index_instance:
#                         self.match_index_instance[appearance['df_index']] = []
#                     if instance not in self.match_index_instance[appearance['df_index']]:
#                         self.match_index_instance[appearance['df_index']].append(instance)
#                         self.match_index_instance[appearance['df_index']].append(instance.is_in_lib)
#                         self.match_index_instance[appearance['df_index']].append(instance.rating)
#                         self.match_index_instance[appearance['df_index']].append(instance.genre)

#     @staticmethod
#     def simplify_genre_list(genres_list):
#         genres_list_clean = [x if str(x) != 'nan' else '' for x in genres_list]
#         genres_list_clean = [x.strip() for x in genres_list_clean]
#         return genres_list_clean


#     def build_genres_count_dict(self, genres_serie):
#         genres_count_dict = {}
#         for ref_genre in self.genres_list:
#             genres_count_dict[ref_genre] = 0
#         for genre_in_serie in genres_serie.tolist():
#             if '&&' in genre_in_serie:
#                 genres = genre_in_serie.split('&&')
#                 for genre in genres:
#                     if genre.strip() in genres_count_dict.keys():
#                         genres_count_dict[genre.strip()] += 1
#             else:
#                 if genre_in_serie in genres_count_dict.keys():
#                     genres_count_dict[genre_in_serie] += 1
#         return genres_count_dict

#     def build_count_dict(self, target_serie):
#         ref_list = target_serie.unique()
        
#         count_dict = {}
#         for ref_elem in ref_list:
#             if str(ref_elem) != 'nan':
#                 count_dict[ref_elem] = 0
#         for df_elem in target_serie.tolist():
#             if str(df_elem) != 'nan':
#                 if df_elem in count_dict.keys():
#                     count_dict[df_elem] += 1
#             else:
#                 continue      
#         return count_dict

#     def build_ranking_dict_per_year(self, df, ranking_target, query_params):
#         ranking_dict = {}
#         for year in query_params['year']:
#             instance_params = query_params
#             instance_params['year'] = [year]
#             query_instance = QueryFactory().create_query(df, instance_params)
#             filtered_df = query_instance.get_filtered_df()
#             if ranking_target == 'Genres':
#                 ranking_dict[year] = self.build_genres_count_dict(filtered_df[ranking_target])
#             elif ranking_target in ['Artist', 'Track_origin', 'Title']:
#                 ranking_dict[year] = self.build_count_dict(filtered_df[ranking_target])   
        
#         return ranking_dict


    @classmethod
    def tearDownClass(self):
        self.input_df = None
        self.parser = None
        self.likes_dislikes_df = None
        self.play_activity_df = None
        self.identifier_infos_df = None
        self.library_tracks_df = None
        self.library_activity_df = None
        self.process = None
        self.track_instance_dict = None
        self.artist_tracks_titles = None
        self.genres_list = None
        self.items_not_matched = None



if __name__ == '__main__':
    unittest.main()