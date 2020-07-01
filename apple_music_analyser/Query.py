

class QueryFactory():

    def create_query(self, reference_df, params_dict=None):
        if params_dict == None:
            query_params_default = {
                'year':reference_df['Play_Year'].unique(),
                'genre':[],
                'artist':[],
                'title':[],
                'rating':[],
                'origin':[],
                'offline':[],
                'library':[],
                'skipped':[],
            }
            return Query(reference_df, query_params_default)

        else:
            return Query(reference_df, params_dict)




class Query():

    def __init__(self, reference_df, query_params):
        self.reference_df = reference_df
        self.query_params = query_params
        self.query_string = self.manage_query_filters()
        self.filtered_df = self.filter_df()

    def get_query_params(self):
        return self.query_params

    def get_query_string(self):
        return self.query_string

    def get_filtered_df(self):
        return self.filtered_df

    def filter_df(self):
        filtered_df = self.reference_df.query(self.query_string)
        return filtered_df

    def manage_query_filters(self):
        '''
            This function returns a query that can be used to filter the dataframe.
            It takes as an input a dictionary, query_params, that will contain the set of
            filters we want to apply on the dataframe. 
        '''
        query = Query.build_numeric_query_element('Play_Year', self.query_params['year'])
        query = query + self.build_data_query()
        return query


    @staticmethod
    def build_string_query_element(category, query_values):
        '''
            This function builds the string that is used as a query to filter the dataframe.
            Depending on the number of arguments passed in query_values, the format of the query changes.
            This function focusing on a single category, the logical operator between each value is
            always going to be OR.

            In this case the query will look for a string, and do an 'str.contains' comparison.

            Example:
            (genre 'Pop' OR 'Rock' OR 'Soundtrack')
        '''
        if len(query_values) == 1:
            query_element = '{0}.str.contains("{1}")'.format(category, query_values[0])
        elif len(query_values) == 2:
            first_item = '{0}.str.contains("{1}")'.format(category, query_values[0])
            last_item = '{0}.str.contains("{1}")'.format(category, query_values[-1])
            query_element = '(' + first_item + '|' + last_item + ')'
        else:
            first_item = '{0}.str.contains("{1}")'.format(category, query_values[0])
            last_item = '{0}.str.contains("{1}")'.format(category, query_values[-1])
            query_element = '(' + first_item + '|'
            for k in range(1, len(query_values)-1):
                query_element = query_element + '{0}.str.contains("{1}")'.format(category, query_values[k]) + '|'
            query_element = query_element + last_item + ')'
        
        return query_element

    @staticmethod
    def build_numeric_query_element(category, query_values):
        '''
            This function builds the string that is used as a query to filter the dataframe.
            Depending on the number of arguments passed in query_values, the format of the query changes.
            This function focusing on a single category, the logical operator between each value is
            always going to be OR.

            In this case the query will look for a numerical value, and do an '==' comparison.

            Example:
            (duration 0 OR 5 OR 10)
        '''
        if len(query_values) == 1:
            query_element = '{0}=={1}'.format(category, query_values[0])
        elif len(query_values) == 2:
            first_item = '{0}=={1}'.format(category, query_values[0])
            last_item = '{0}=={1}'.format(category, query_values[-1])
            query_element = '(' + first_item + '|' + last_item + ')'
        else:
            first_item = '{0}=={1}'.format(category, query_values[0])
            last_item = '{0}=={1}'.format(category, query_values[-1])
            query_element = '(' + first_item + '|'
            for k in range(1, len(query_values)-1):
                query_element = query_element + '{0}=={1}'.format(category, query_values[k]) + '|'
            query_element = query_element + last_item + ')'
        
        return query_element 
    
    @staticmethod
    def build_boolean_query_element(category, query_values):
        '''
            This function builds the string that is used as a query to filter the dataframe.
            As with boolean category the number of values can only be at most 2 (True, False),
            the logic is much simpler than for other categories - there is at most one OR logical
            operator between the values of the category. 
            
            In this case the query will look for a boolean value, and do an 'isin' comparison.

            Example:
            library_track False OR True
        '''
        query_element = ''
        if len(query_values) == 1:
            query_element = query_element + '{0}.isin([{1}])'.format(category, query_values[0])
        else:
            first_item = '{0}.isin([{1}]'.format(category, query_values[0])
            last_item = '{0}.isin([{1}])'.format(category, query_values[-1])
            query_element = query_element + '(' + first_item + '|' + last_item + ')'
        
        return query_element


    def build_data_query(self):
        '''
            This function is in charge of choosing which column to use in the query 
            depending on the keys of the query_params dict.
            It uses the few functions build_string_query_element and build_boolean_query_element
            to actually put together the query string.
        '''
        query = ''
        for query_category in self.query_params.keys():
            target_values = self.query_params[query_category]
            if query_category != 'year' and target_values != []:
                query = query + '&'
                if query_category == 'genre':
                    query = query + Query.build_string_query_element('Genres', target_values)
                elif query_category == 'artist':
                    query = query + Query.build_string_query_element('Artist', target_values)
                elif query_category == 'title':
                    query = query + Query.build_string_query_element('Title', target_values)
                elif query_category == 'rating':
                    query = query + Query.build_string_query_element('Rating', target_values)
                elif query_category == 'origin':
                    query = query + Query.build_string_query_element('Track_origin', target_values)
                elif query_category == 'offline':
                    # as here we compare with booleans, we do not use build_query_element
                    query = query + Query.build_boolean_query_element('Offline', target_values)
                elif query_category == 'library':
                    query = query + Query.build_boolean_query_element('Library_Track', target_values)
                elif query_category == 'skipped':
                    query = query + Query.build_boolean_query_element('Played_completely', target_values)
        return query



