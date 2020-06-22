from Utility import Utility


class VisualizationDataframe():

	def __init__(self, input_df):
		self.input_df = input_df
		self.likes_dislikes_df = None
		self.play_activity_df = None
		self.identifier_infos_df = None
		self.library_tracks_df = None
		self.library_activity_df = None

	def parse_input_df(self):

		error_message_bad_input = ("Please ensure that the input_df object has the following structure...\n"

		'{	"identifier_infos_df" : identifier_infos_df, "library_tracks_df" : library_tracks_df,\n'
		'"library_activity_df" : library_activity_df, "likes_dislikes_df" : likes_dislikes_df, "play_activity_df" : play_activity_df	}\n'

		'...And that the values in this dictionary are pandas dataframes.')

		if len(self.input_df) != 5:
			print(error_message_bad_input)

		else:
			if Utility.validate_input_df_files(self.input_df):
				self.likes_dislikes_df = self.input_df['likes_dislikes_df']
				self.play_activity_df = self.input_df['play_activity_df']
				self.identifier_infos_df = self.input_df['identifier_infos_df']
				self.library_tracks_df = self.input_df['library_tracks_df']
				self.library_activity_df = self.input_df['library_activity_df']
			else:
				print(error_message_bad_input)

