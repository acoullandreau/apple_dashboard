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




































