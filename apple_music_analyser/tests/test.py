import pandas as pd
import unittest
from unittest.mock import MagicMock

from apple_music_analyser.Utility import Utility
#from apple_music_analyser.VisualizationDataframe import VisualizationDataframe
#from apple_music_analyser.DataVisualization import SunburstVisualization, RankingListVisualization, HeatMapVisualization, PieChartVisualization, BarChartVisualization
#from apple_music_analyser.Query import Query, QueryFactory


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
	# 	'''
	# 		We only test the case where the path is wrong
	# 		This function relies on external package (ZipFile), well covered by tests.
	# 	'''
	# 	archive_path = None
	# 	result = Utility.get_df_from_archive(archive_path)
	# 	self.assertEqual(result, {})





# class TestTextClass(unittest.TestCase):

#     @classmethod
#     def setUpClass(self):
#         self.text = ContextualText('This is a test', (50, 50), (255, 255, 255))
#         self.cv2_original = cv2.putText
#         cv2.putText = MagicMock()

#     def test_init_text(self):
#         """
#         Test the proper instanciation of a ContextualText class object
#         """
#         self.assertEqual(self.text.text_content, 'This is a test')
#         self.assertEqual(self.text.position, (50, 50))
#         self.assertEqual(self.text.color, (255, 255, 255))
#         self.assertEqual(self.text.font, cv2.FONT_HERSHEY_SIMPLEX)
#         self.assertEqual(self.text.font_style, cv2.LINE_AA)
#         self.assertEqual(self.text.text_size, 1)
#         self.assertEqual(self.text.thickness, 1)
#         self.text.text_size = 10
#         self.assertEqual(self.text.text_size, 10)
#         self.text.thickness = 2
#         self.assertEqual(self.text.thickness, 2)

#     def test_display_text(self):
#         map_to_edit = 'Test Map'
#         text = self.text.text_content
#         pos = self.text.position
#         col = self.text.color
#         font = self.text.font
#         size = self.text.text_size
#         thick = self.text.thickness
#         style = self.text.font_style
#         cv2.putText(map_to_edit, text, pos, font, size, col, thick, style)
#         # assertion statement
#         cv2.putText.assert_called_once_with('Test Map', 'This is a test', (50, 50), 0, 1, (255, 255, 255), 1, 16)

#     @classmethod
#     def tearDownClass(self):
#         self.text = None
#         cv2.putText = self.cv2_original


if __name__ == '__main__':
    unittest.main()