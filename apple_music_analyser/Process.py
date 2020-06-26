from Track import Track
from Utility import Utility

class ProcessTracks():

    def __init__(self):
        ## this is used to assign a unique id to each track instance
        self.increment = 0
        ## this is used to keep track of the title/artist combination with the ref of the associated track instance
        self.track_instance_dict = {}
        ## this is used to keep track of all the titles of an artist, including different spellings of the same title
        self.artist_tracks_titles = {}
        ## this is used to keep track of all the unique values of genres
        self.genres_list = []
        ## this is used to keep track of the rows that were not matched in all dataframes processed
        ## can be used to spot why a given row was excluded from the track instances
        self.items_not_matched = {'library_tracks':[], 'identifier_info':[],
                             'play_activity':[], 'likes_dislikes':[]}


    def update_track_instance(self, origin_df, track_instance, index, row, title_artist):
        if origin_df == 'play_activity_df':
            track_instance.update_track_from_play_activity(index, row)
            if row['Genre'] not in self.genres_list:
                self.genres_list.append(row['Genre'])
        elif origin_df == 'library_tracks_df':
            track_instance.update_track_from_library(index, row)
            #we update the dictionary that keeps track of our instances, and increment
            if row['Genre'] not in self.genres_list:
                self.genres_list.append(row['Genre'])
            self.track_instance_dict[title_artist] = track_instance
        else:
            print('There is no method to update a track instance from another dataframe than play_activity_df or library_tracks_df')


    def compare_titles_for_artist(self, artist, title_to_compare):
        '''
            Compares the string similarity of any song associated to an artist and an unknown
            title for this artist. The goal here is to be able to match different spellings of 
            the same song. 
            If the similarity score is above the threshold set, it returns the track instance
            of the matching artist song we already know. 
            Otherwise it returns 'No match'.
        '''
        for artist_track in self.artist_tracks_titles[artist]:
            title_similarity_for_artist = Utility.compute_similarity_score(title_to_compare, artist_track)
            # value observed to bring consistently a match between similar songs
            if title_similarity_for_artist > 0.625:
                #we fetch the track instance associated with the close match
                title_artist = Utility.concat_title_artist(artist_track, artist)
                track_instance = self.track_instance_dict[title_artist]
                return track_instance
        return 'No match'


    def process_library_tracks_df(self, library_df):
        '''
            This function goes through each row of the library tracks dataframe, creating and updating
            track instances as they appear.
            As this is the first dataframe we go through, we want to create new instances whenever
            we are not facing unknown songs (NaN as a title)
            The logic works as follows, knowing that we do this for each row of the dataframe:
                - we look only at rows with a title different than NaN, and we set the artist to
                'No Artist' if the artist is also Nan
                - if the track is not in the dictionary of track instances, it means that we never
                saw the combination title/artist of this row. So two options here:
                    - either we know this artist and we can find a similar title in the artist dict, and in
                    this case we update the existing track using update_track_from_library
                    - or we do not know this artist, or we do not find a close match of title for this artist
                    and in this case we create a new track instance using instantiate_track and then
                    update_track_from_library
                - else, we update the existing track using update_track_from_library
        '''
        for index, row in library_df.iterrows():
            if str(row['Title']) != 'nan':
                title = row['Title']
                if str(row['Artist']) != 'nan':
                    artist = row['Artist']
                else:
                    artist = 'No Artist'

                title_artist = Utility.concat_title_artist(title, artist)

                if title_artist not in self.track_instance_dict.keys():
                    if artist in self.artist_tracks_titles.keys():
                        titles_comparison_result = self.compare_titles_for_artist(artist, title)

                        if titles_comparison_result == 'No match':
                            #we instantiate the Track object
                            track_instance = Track(self.increment)
                            track_instance.instantiate_track(title, artist)
                            self.update_track_instance('library_tracks_df', track_instance, index, row, title_artist)
                            self.increment += 1

                        else:
                            track_instance = titles_comparison_result
                            if not track_instance.has_title_name(title):
                                track_instance.add_title(title)
                            self.update_track_instance('library_tracks_df', track_instance, index, row, title_artist)
                            #self.artist_tracks_titles[artist].append(title)
                    
                    else:
                        #there was no close match, and the song was never seen, so we instantiate a new Track
                        track_instance = Track(self.increment)
                        track_instance.instantiate_track(title, artist)
                        self.update_track_instance('library_tracks_df', track_instance, index, row, title_artist)
                        self.increment += 1


                else:
                    self.update_track_instance('library_tracks_df', track_instance, index, row, title_artist)


                #we update the artist/track names dictionnary
                if artist not in self.artist_tracks_titles:
                    self.artist_tracks_titles[artist]=[]
                if title not in self.artist_tracks_titles[artist]:
                    self.artist_tracks_titles[artist].append(title)
            else:
                self.items_not_matched['library_tracks'].append(index)



    def process_identifier_df(self, identifier_df):
        '''
            This function goes through each row of the identifier information dataframe, updating
            track instances as they appear.
            Unlike for the tracks dataframe, we have very limited information here, just an identifier
            and a title (not even an artist name). So we need to have a different approach, only
            based on the identifiers. Which may excluse some songs... But prevents false positives.
            The logic works as follows, knowing that we do this for each row of the dataframe:
                - we loop through all the track instances we created so far, and see if any of their 
                identifier matches the id of the row we are looking at
                - if it matches, and if we didn't already have the associated title, we add it to the
                list of titles of that track
                - otherwise, we add it to the tracks we could not match and we ignored.
        '''
        for index, row in identifier_df.iterrows():
            found_match = False
            for title_name in self.track_instance_dict.keys():
                track_instance = self.track_instance_dict[title_name]
                if row['Identifier'] in track_instance.apple_music_id:
                    track_instance.add_appearance({'source': 'identifier_info', 'df_index':index})
                    if not track_instance.has_title_name(row['Title']):
                        track_instance.add_title(row['Title'])
                    found_match = True
                    break
            if found_match is False:
                self.items_not_matched['identifier_info'].append((index, row['Identifier']))


    def process_play_df(self, play_activity_df):
        '''
            This function goes through each row of the play activity dataframe, creating and updating
            track instances as they appear.
            As this is the dataframe we are able to get the most information from, we want to create
            new instances whenever we are not facing unknown songs (NaN as a title).The approach is
            very similar to the one used for the library tracks.
            
            The logic works as follows, knowing that we do this for each row of the dataframe:
                - if the track is in the dictionary of track instances, we update the existing
                track using update_track_from_play_activity
                - else, we have two options :
                    - either we know this artist and we can find a similar title in the artist dict,
                    and in this case we update the existing track using update_track_from_play_activity
                    - or we do not know this artist, or we do not find a close match of title for this
                    artist and in this case we create a new track instance using instantiate_track and
                    then update_track_from_play_activity
        '''
        for index, row in play_activity_df.iterrows():
            #we want to look only at rows where the name of the song is available
            if str(row['Title']) != 'nan':
                title = row['Title']
                if str(row['Artist']) != 'nan':
                    artist = row['Artist']
                else:
                    artist = 'No Artist'
            else:
                self.items_not_matched['play_activity'].append(index)
                continue

            #we check if we already saw this track (using title and artist names)
            title_artist = Utility.concat_title_artist(title, artist)
            if title_artist in self.track_instance_dict.keys():
                track_instance = self.track_instance_dict[title_artist]
                self.update_track_instance('play_activity_df', track_instance, index, row, title_artist)

            else:
                # if we had no match with title and artist, we look for similarity in the title for the artist
                if artist in self.artist_tracks_titles.keys():
                    titles_comparison_result = self.compare_titles_for_artist(artist, title)
                    if titles_comparison_result == 'No match':
                        #we instantiate the Track object
                        track_instance = Track(self.increment)
                        track_instance.instantiate_track(title, artist)
                        self.update_track_instance('play_activity_df', track_instance, index, row, title_artist)
                        #we update the dictionary that keeps track of our instances, and increment
                        self.track_instance_dict[title_artist] = track_instance
                        self.increment+=1

                    else:
                        track_instance = titles_comparison_result
                        if not track_instance.has_title_name(title):
                            track_instance.add_title(title)
                        track_instance.add_appearance({'source': 'play_activity', 'df_index':index})
                        #we also track the match in the track_instances and artist dicts
                        self.track_instance_dict[title_artist] = track_instance
                        self.artist_tracks_titles[artist].append(title)

                # else we know we never saw this track because the artist is unknown      
                else:
                    #we update the artist/track names dictionnary
                    self.artist_tracks_titles[artist]=[]
                    self.artist_tracks_titles[artist].append(title)

                    #we instantiate the Track object
                    track_instance = Track(self.increment)
                    track_instance.instantiate_track(title, artist)
                    self.update_track_instance('play_activity_df', track_instance, index, row, title_artist)

                    #we update the dictionary that keeps track of our instances, and increment
                    self.track_instance_dict[title_artist] = track_instance
                    self.increment+=1

    def process_likes_dislikes_df(self, likes_dislikes_df):
        '''
            This function goes through each row of the likes_dislikes dataframe, updating
            track instances as they appear.
            This dataframe contains a small proportion of all the tracks ever listened to, and/or in
            the library. As a result, we only want to update existing tracks, and not create new ones.
            The logic works as follows, knowing that we do this for each row of the dataframe:
                - we loop through all the track instances we created so far, and see if any of their 
                identifier matches the id of the row we are looking at
                - if we find a match, we update the track with the rating, appearance, and if we didn't
                already have the associated title, we add it to the list of titles of that track
                - else:
                    - if the track is in the dictionary of track instances, we update the existing
                track's rating and appearance
                    - otherwise, we have two options:
                        - either we know the artist and we can find a similar title in the artist dict,
                    and in this case we update the existing track
                        - or we do not know this artist, or we do not find a close match of title for this
                    artist and in this case we add it to the tracks we could not match and we ignored
        ''' 
        for index, row in likes_dislikes_df.iterrows():
            #we want to look only at rows where the name of the song is available
            if str(row['Title']) != 'nan':
                title = row['Title']
                if str(row['Artist']) != 'nan':
                    artist = row['Artist']
                else:
                    artist = 'No Artist'
            else:
                self.items_not_matched['likes_dislikes'].append(index)
                continue

            title_artist = Utility.concat_title_artist(title, artist)

            # first we check using the Item Reference as an id
            found_match = False
            for title_name in self.track_instance_dict.keys():
                track_instance = self.track_instance_dict[title_name]
                if row['Item Reference'] in track_instance.apple_music_id:
                    track_instance.add_appearance({'source': 'likes_dislikes', 'df_index':index})
                    track_instance.set_rating(row['Preference'])
                    if not track_instance.has_title_name(row['Title']):
                        track_instance.add_title(row['Title'])
                        self.track_instance_dict[title_artist] = track_instance
                        if row['Title'] not in self.artist_tracks_titles[artist]:
                            self.artist_tracks_titles[artist].append(title)
                    found_match = True
                    break

            if found_match is False:
                #we check if we already saw this track (using title and artist names)
                if title_artist in self.track_instance_dict.keys():
                    track_instance = self.track_instance_dict[title_artist]
                    track_instance.add_appearance({'source': 'likes_dislikes', 'df_index':index})
                    track_instance.set_rating(row['Preference'])

                else:
                    # if we had no match with title and artist, we look for similarity in the title for the artist
                    if artist in self.artist_tracks_titles.keys():
                        titles_comparison_result = self.compare_titles_for_artist(artist, title)
                        if titles_comparison_result == 'No match':
                            #we add the item to the items_not_matched
                            self.items_not_matched['likes_dislikes'].append(index)
                            continue
                        else:
                            track_instance = titles_comparison_result
                            if not track_instance.has_title_name(title):
                                track_instance.add_title(title)
                            track_instance.add_appearance({'source': 'likes_dislikes', 'df_index':index})
                            track_instance.set_rating(row['Preference'])
                            self.track_instance_dict[title_artist] = track_instance
                            self.artist_tracks_titles[artist].append(title)
                    else:
                        #we add the item to the items_not_matched,
                        #we choose not to add it to the Track instances as the amount of information is little
                        #and our reference really is the play activity!
                        self.items_not_matched['likes_dislikes'].append(index)
                        continue



