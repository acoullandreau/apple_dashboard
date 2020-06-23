import pandas as pd
import time
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
		parsed_df = self.play_activity_df.rename(columns={'Content Name':'Title', 'Artist Name':'Artist'})
		# Add time related columns
		parsed_df['Activity date time'] = pd.to_datetime(parsed_df['Event Start Timestamp'])
		parsed_df['Activity date time'].fillna(pd.to_datetime(parsed_df['Event End Timestamp']), inplace=True)
		parsed_datetime_series = Utility.parse_date_time_column(parsed_df, 'Activity date time')
		Utility.add_time_related_columns(parsed_df, parsed_datetime_series, 'Play')
		parsed_df = parsed_df.rename(columns={'Play HOD':'Play HOD UTC'})
		parsed_df['Play HOD Local Time']= parsed_df['Play HOD UTC'] + parsed_df['UTC Offset In Seconds']/3600
		parsed_df['Play HOD Local Time'] = parsed_df['Play HOD Local Time'].astype(int)
		
		start = time.time()
		# Add partial listening column
		parsed_df['Played completely'] = parsed_df.apply(Utility.set_partial_listening, axis=1)
		end = time.time()
		print(end - start)
		
		# Add track origin column
		parsed_df['Track origin'] = parsed_df['Feature Name'].apply(Utility.get_track_origin)

		start = time.time()
		# Add play duration column
		parsed_df['Play duration in minutes'] = parsed_df.apply(Utility.compute_play_duration, axis=1)
		# we remove outliers from this column, saying that if a value if above the 99th percentile,
		# we drop it, and replace it by the duration of the media
		percentile = parsed_df['Play duration in minutes'].quantile(0.99)
		parsed_df['Play duration in minutes'] = parsed_df.apply(Utility.remove_play_duration_outliers, percentile=percentile, axis=1)
		end = time.time()
		print(end - start)
		#we can then remove the columns we do not need anymore!
		if drop_columns:
			parsed_df = parsed_df.drop(columns_to_drop, axis=1)

		self.play_activity_df = parsed_df


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
