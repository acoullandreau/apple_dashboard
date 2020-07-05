

class Track():
    # the instances of this class are songs, identified using either a combination of their
    # title and artist names, or an identifier when available
    # we track in which file we found the track for (appearance), as well as rating, genre and whether
    # it is in the library or not
    
    def __init__(self, identifier):
        self.identifier = identifier
        self.titles = []
        self.artist = None
        self.is_in_lib = False
        self.appearances = []
        self.genre = []
        self.apple_music_id = []
        self.rating = []
    
    def has_title_name(self, title):
        if title in self.titles:
            return True
        return False
    
    def add_title(self, title):
        self.titles.append(title)
    
    def set_artist(self, artist):
        self.artist = artist
    
    def set_apple_music_id(self, apple_music_id):
        if apple_music_id not in self.apple_music_id:
            self.apple_music_id.append(apple_music_id)
               
    def set_library_flag(self):
        self.is_in_lib = True
    
    def set_genre(self, genre):
        if type(genre) != float:
            if genre not in self.genre:
                self.genre.append(genre.strip())
        
    def add_appearance(self, appearance_dict):
        self.appearances.append(appearance_dict)

    def set_rating(self, rating):
        if rating == 'LOVE' or rating == 'LIKE':
            if 'LOVE' not in self.rating:
                self.rating.append(rating)
        elif rating == 'DISLIKE':
            if rating not in self.rating:
                self.rating.append(rating)


    def instantiate_track(self, title, artist):
        '''
            Creates an instance of the Track class, setting both the title and artist
            names used when creating it (multiple titles may be found latter on and added 
            to the list of titles for this track
        '''
        self.add_title(title)
        self.set_artist(artist)


    def update_track_from_library(self, index, row):
        '''
            For a given track instance, updates the properties of the track using the library
            tracks dataframe:
                - its appearance in the library_tracks_info_df, and at which index
                - the genre and rating of the song when available
                - the flag is_in_lib
                - any of the available identifiers used to identify the track
        '''
        self.set_library_flag()
        self.add_appearance({'source': 'library_tracks', 'df_index':index})
        self.set_genre(row['Genre'])
        self.set_rating(row['Track Like Rating'])
        if str(row['Apple Music Track Identifier'])!='nan':
            self.set_apple_music_id(str(int(row['Apple Music Track Identifier'])))
            if str(row['Tag Matched Track Identifier']) !='nan' and row['Tag Matched Track Identifier'] != row['Apple Music Track Identifier']:
                self.set_apple_music_id(str(int(row['Tag Matched Track Identifier'])))
        else:
            self.set_apple_music_id(str(int(row['Track Identifier'])))
            if str(row['Purchased Track Identifier']) !='nan':
                self.set_apple_music_id(str(int(row['Purchased Track Identifier'])))

    def update_track_from_play_activity(self, index, row):
        '''
            For a given track instance, updates the properties of the track using the play
            activity dataframe:
                - its appearance in the play_activity_df, and at which index
                - the genre of the song when available
                - the flag is_in_lib whenever the song was found from the library
        '''
        self.add_appearance({'source': 'play_activity', 'df_index':index})
        self.set_genre(row['Genre'])
        if row['Track origin'] == 'library' and self.is_in_lib is False:
            self.set_library_flag()

