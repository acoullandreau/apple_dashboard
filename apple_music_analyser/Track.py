

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
            if rating not in self.rating:
                self.rating.append(rating)
        elif rating == 'DISLIKE':
            if rating not in self.rating:
                self.rating.append(rating)