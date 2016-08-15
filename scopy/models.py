"""

"""

#DC:
#https://en.wikipedia.org/wiki/Dublin_Core
#
#PRISM
#http://www.idealliance.org/specifications/prism-metadata-initiative

from .utils import get_truncated_display_string as td
from .utils import get_list_class_display as cld
from .utils import property_values_to_string as pv

from pypub.scrapers.base_objects import *

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
        elif new_name in self.object_fields:
            #Here we return the value after passing it to a method
            #fh => function handle
            #
            #Only the value is explicitly passed in
            #Any other information needs to be explicitly bound
            #to the method
            method_fh = self.object_fields[new_name]
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


class SearchResultsLinks(object):
    
    def __init__(self,json):
        
        names = {'self':'self','first':'first','next':'next','last':'last'}
        
        self.json = json
        self.self = None
        self.first = None
        self.next = None
        self.last = None
                
        for temp in json:
            if temp['@ref'] in names:
                setattr(self,names[temp['@ref']],temp['@href'])       

    def __repr__(self):
        return pv([
            'self',self.self,
            'first', self.first,
            'next',self.next,
            'last',self.last])
            

class SearchResults(ResponseObject):
    
    """
    Class contains results from a search.
    """
    
    object_fields = {'links':SearchResultsLinks}    
        
    renamed_fields = {
        'total_results':'opensearch:totalResults',
        'items_per_page':'opensearch:itemsPerPage',
        'start_index':'opensearch:startIndex',
        'query':'opensearch:Query',
        'links':'link'}
    
    def __init__(self,json):
        
        super(SearchResults, self).__init__(json)
        entries = json.get('entry') #list       
        self.entries = [SearchResultEntry(x) for x in entries]        

    def __repr__(self):
        return pv([
            'total_results',self.total_results,
            'start_index',self.start_index,
            'items_per_page',self.items_per_page,
            'entries',cld(self.entries),
            'links',cld(self.links)])
    
    #TODO: Bring in navigation        

class SearchResultEntryLinks(object):
    
    def __init__(self, json):
        #super(SearchEntryLinks, self).__init__(json)
        
        #TODO: We might just want to make this object right away, rather than inherting from response
        #TODO: We need to be able to handle the links

        #TODO: Use an input output mapping name

        names = {'self':'self','author-affiliation':'author_affiliation','scopus':'scopus','scopus-citedby':'scopus_cited_by'}
        
        self.self = None
        self.author_affiliation = None
        self.scopus = None
        self.scopus_cited_by = None
        
        
        for temp in json:
            if temp['@ref'] in names:
                setattr(self,names[temp['@ref']],temp['@href'])
                #TODO: otherwise raise an error


       
        #ref - Observed values include: self, author-affiliation, scopus, scopus-citedby
        #href - the link value
        #@_fa - ????
        #
        #e.g. {'@ref': 'self', '@href': 'http://api.elsevier.com/content/abstract/scopus_id/0023137155', '@_fa': 'true'}        
        
    def __repr__(self):
        return pv([
            'self',self.self,
            'author_affiliation', self.author_affiliation,
            'scopus', self.scopus,
            'scopus-cited_by', self.scopus_cited_by])


class SearchResultEntry(ResponseObject):
    
    """
    It looks like the search entry is more minimal than information that can be obtained via other methods
    
    Attributes
    ----------
    creator : string
        Author
        
    """

    #TODO: Support affiliation as an object
    #TODO: Do we need to switch based on subtype?
    object_fields = {'links': SearchResultEntryLinks}    
        
    renamed_fields = {
        'aggregation_type': 'prism:aggregationType',
        'author_count': 'author-count',
        'cited_by_count': 'citedby-count',
        'cover_date': 'prism:coverDate',
        'cover_display_date' : 'prism:coverDisplayDate',
        'creator' : 'dc:creator',
        'description' : 'dc:description',
        'issn' : 'prism:issn',
        'issue' : 'prism:issueIdentifier',
        'links': 'link',
        'page_range' : 'prism:pageRange',
        'publication' : 'prism:publicationName',
        'pubmed_id': 'pubmed-id',
        'source_id' : 'source-id',
        'subtype_description' : 'subtypeDescription',
        'volume' : 'prims:volume'}
            
    def __init__(self, json):
        """
        Parameters
        ----------
        json : dict

        """
        super(SearchResultEntry, self).__init__(json)

    @classmethod
    def fields(cls):
        return ['eid','affiliation','subtype']
   
    def __repr__(self):
        return pv([
        'description',self.description,        
        'aggregation_type',self.aggregation_type,
        'subtype',self.subtype,
        'subtype_description',self.subtype_description,
        'creator',self.creator,
        'affiliation',self.affiliation,
        'publication',self.publication,
        'source_id',self.source_id,
        'volume',self.volume,
        'issue',self.issue,
        'page_range',self.page_range,
        'cited_by_count',self.cited_by_count,
        'author_count',self.author_count,
        'pubmed_id',self.pubmed_id,
        'issn',self.issn,
        'eid',self.eid,
        'links',cld(self.links),
        'cover_display_date',self.cover_display_date,
        'cover_date',self.cover_date])
        
    def get_abstract(self):
        pass        


class ScopusRef(BaseRef):
    def __init__(self, json):
        super().__init__()
        self.authors = []

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


class ScopusEntry(BaseEntry):
    """
    These are populated by search results. Each result contains these fields.

    """

    def __init__(self, json):
        super().__init__()

        self.type = None
        self.issn = None
        self.authors = []
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
        self.publication = coredata.get('prism:publicationName')
        self.type = coredata.get('prism:aggregationType')
        self.issn = coredata.get('prism:issn')
        self.volume = coredata.get('prism:volume')
        self.issue = coredata.get('prism:issueIdentifier')
        self.pages = coredata.get('prism:pageRange')
        self.date = coredata.get('prism:coverDate')
        self.abstract = coredata.get('dc:description')

        # Get authors
        author_section = coredata.get('dc:creator')
        if isinstance(author_section, dict) and 'author' in author_section.keys():
            author_section = author_section.get('author')

        if author_section is not None:
            if isinstance(author_section, list):
                for author in author_section:
                    name = author.get('$')
                    if name is None:
                        name = author.get('ce:indexed-name')
                    if name is not None:
                        auth = BaseAuthor()
                        auth.name = name
                        self.authors.append(auth)
            else:
                name = author_section.get('$')
                if name is None:
                    name = author_section.get('ce:indexed-name')
                if name is not None:
                    auth = BaseAuthor()
                    auth.name = name
                    self.authors.append(auth)

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
