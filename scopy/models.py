"""

"""

#DC:
#https://en.wikipedia.org/wiki/Dublin_Core
#
#PRISM
#http://www.idealliance.org/specifications/prism-metadata-initiative



class ResponseObject(object):
    # I made this a property so that the user could change this processing
    # if they wanted. For example, this would allow the user to return authors
    # as just the raw json (from a document) rather than creating a list of
    # Persons
    object_fields = {}
    
    #Name mapping, keys are new, values are old
    renamed_fields = {}

    def __init__(self, json):
        """
        This class stores the raw JSON in case an attribute from this instance
        is requested. The attribute is accessed via the __getattr__ method.

        This design was chosen instead of one which tranfers each JSON object
        key into an attribute. This design decision means that we don't spend
        time populating an object where we only want a single attribute.
        
        Note that the request methods should also support returning the raw JSON.
        """
        self.json = json

    def __getattr__(self, name):

        """
        By checking for the name in the list of fields, we allow returning
        a "None" value for attributes that are not present in the JSON. By
        forcing each class to define the fields that are valid we ensure that
        spelling errors don't return none:
        e.g. document.yeear <= instead of document.year
        """
        
        #TODO: We need to support renaming
        #i.e. 
        if name in self.fields():
            new_name = name
        elif name in self.renamed_fields:
            new_name = name #Do we want to do object lookup on the new name?
            name = self.renamed_fields[name]
        else:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))
          
        value = self.json.get(name)          
          
        #We don't call object construction methods on None values
        if value is None:
            return None
        elif name in self.object_fields:
            #Here we return the value after passing it to a method
            #fh => function handle
            #
            #Only the value is explicitly passed in
            #Any other information needs to be explicitly bound
            #to the method
            method_fh = self.object_fields[name]
            return method_fh(value)
        else:
            return value

            

    @classmethod
    def __dir__(cls):
        d = set(dir(cls) + cls.fields())
        d.remove('fields')
        d.remove('object_fields')

        return sorted(d)

    @classmethod
    def fields(cls):
        """
        This should be overloaded by the subclass.
        """
        return []


class SearchResults(object):
    
    def __init__(self,json):
        
        #dict_keys(['opensearch:totalResults', 'opensearch:startIndex', 'entry', 'link', 'opensearch:Query', 'opensearch:itemsPerPage'])
        
        self.total_results = json.get('opensearch:totalResults')
        self.items_per_page = json.get('opensearch:itemsPerPage')
        
        entries = json.get('entry') #list       
        
        self.entries = [SearchEntry(x) for x in entries]        
        

        #TODO: Is a SearchEntry different than a ScopusEntry
        # KSA: No. They're the same.



#JAH: Need to create a parent response object like in Mendeley
#Don't assign everything

class SearchEntry(ResponseObject):
    
    """
    It looks like the search entry is more minimal than information that can be obtained via other methods
    """
    
    #TODO: Replace with relevant values for this class
    #object_fields = {
    #    'authors': Person.initialize_array,
    #    'identifiers': DocumentIdentifiers}    
    
    def __init__(self, json):
        """
        Parameters
        ----------
        json : dict

        """
        super(SearchEntry, self).__init__(json)

    @classmethod
    def fields(cls):
        return ['citedby-count', 'author-count', 'pubmed-id', 'eid']

        import pdb
        pdb.set_trace()

        #TODO: We should just store the json, and then retrieve these as needed by the user
        #self.pubmed_id = json.get('pubmed-id')
        #self.eid = json.get('eid')
        #self.link = json.get('link')      
        #Links
        #-----
        #ref - Observed values include: self, author-affiliation, scopus, scopus-citedby
        #href - the link value
        #@_fa - ????
        #
        #e.g. {'@ref': 'self', '@href': 'http://api.elsevier.com/content/abstract/scopus_id/0023137155', '@_fa': 'true'}
        
        #???? What does dc stand for?
        #What is @_fa??????
        '''
        dict_keys(['prism:coverDate', 'citedby-count', 'pubmed-id', 'link', 
        'eid', 'prism:aggregationType', '@_fa', 'affiliation', 'subtype', 
        'prism:coverDisplayDate', 'prism:pageRange', 'prism:issn', 'dc:description', 
        'prism:publicationName', 'prism:issueIdentifier', 'dc:creator', 
        'subtypeDescription', 'source-id', 'prism:volume', 
        'prism:doi', 'author-count', 'prism:url', 
        'dc:identifier', 'author', 'dc:title', 'intid'])   
        '''

class ScopusRef(object):
    def __init__(self, json):
        self.authors = []
        self.title = None
        self.volume = None
        self.issue = None
        self.date = None
        self.pages = None
        self.publication = None

        self._populate_fields(json)

    def __repr__(self):
        return u'' \
            'authors: %s\n' % self.authors + \
            'title: %s\n' % self.title + \
            'volume: %s\n' % self.volume + \
            'issue: %s\n' % self.issue + \
            'date: %s\n' % self.date + \
            'pages: %s\n' % self.pages + \
            'publication: %s\n' % self.publication

    def _populate_fields(self, json):
        info = json.get('ref-info')

        # Descend through author JSON tree
        next_level = info
        x = 0
        author_levels = ['ref-authors', 'author']
        while next_level is not None and x < len(author_levels):
            next_level = next_level.get(author_levels[x])
            x += 1

        # The above returns a list of authors.
        # Iterate through and add the names to self.authors
        if next_level is not None:
            if not isinstance(next_level, dict):
                for author in next_level:
                    if 'ce:indexed-name' in author.keys():
                        self.authors.append(author.get('ce:indexed-name'))
                    elif ('ce:surname', 'ce:initials') in author.keys():
                        name = ' '.join([author['ce:surname'], author['ce:initials']])
                        self.authors.append(name)
            else:
                if 'ce:indexed-name' in next_level.keys():
                    self.authors.append(next_level.get('ce:indexed-name'))
                elif ('ce:surname', 'ce:initials') in next_level.keys():
                    name = ' '.join([next_level['ce:surname'], next_level['ce:initials']])
                    self.authors.append(name)

        # Get page ranges
        next_level = info
        x = 0
        page_levels = ['ref-volisspag', 'pagerange']
        while next_level is not None and x < len(page_levels):
            next_level = next_level.get(page_levels[x])
            x += 1

        if next_level is not None:
            if ('@first', '@last') in next_level.keys():
                self.pages = '-'.join([next_level['@first'], next_level['@last']])

        # Get issue and volume:
        voliss = info.get('voliss')
        if voliss is not None:
            self.issue = voliss.get('@issue')
            self.volume = voliss.get('@volume')

        # Get publication year
        pubyear = info.get('ref-publicationyear')
        if pubyear is not None:
            self.date = pubyear.get('@first')

        # Get title
        title = info.get('ref-title')
        if title is not None:
            self.title = title.get('ref-titletext')

        # Get publication
        self.publication = info.get('ref-sourcetitle')


class ScopusEntry(object):
    """
    These are populated by search results. Each result contains these fields.

    """

    def __init__(self, json):
        self.doi = None
        self.eid = None
        self.pii = None
        self.title = None
        self.publisher = None
        self.type = None
        self.issn = None
        self.volume = None
        self.issue = None
        self.pages = None
        self.date = None
        self.authors = []
        self.abstract = None
        self.link = None
        self.article = None

        self._populate_fields(json)

    def _populate_fields(self, json):

        coredata = json.get('coredata')
        if coredata is None:
            coredata = json.get('entry')

        self.doi = coredata.get('prism:doi')
        self.eid = coredata.get('eid')
        self.pii = coredata.get('pii')
        self.title = coredata.get('dc:title')
        self.publisher = coredata.get('prism:publicationName')
        self.type = coredata.get('prism:aggregationType')
        self.issn = coredata.get('prism:issn')
        self.volume = coredata.get('prism:volume')
        self.issue = coredata.get('prism:issueIdentifier')
        self.pages = coredata.get('prism:pageRange')
        self.date = coredata.get('prism:coverDate')
        self.abstract = coredata.get('dc:description')

        # Get authors
        author_section = coredata.get('dc:creator')
        if author_section is not None:
            if isinstance(author_section, list):
                for author in author_section:
                    name = author.get('$')
                    if name is not None:
                        self.authors.append(name)
            else:
                name = author_section.get('$')
                if name is not None:
                    self.authors.append(name)

        # Get article links
        links = coredata.get('link')
        if isinstance(links, list):
            self.link = []
            for item in links:
                link = item.get('@href')
                if link is not None:
                    self.link.append(link)
        else:
            link = links.get('@href')
            if link is not None:
                self.link = link

        # Get article (if returned in JSON)
        article_text = json.get('originalText')
        if isinstance(article_text, dict):
            self.article = ''
        else:
            self.article = article_text
