"""
Implementing the Scopus APIs listed here:
http://dev.elsevier.com/api_docs.html

Interactive versions of these APIs are here:
http://dev.elsevier.com/interactive.html

--- Usage Notes ---
 * The IP address is checked on each request. The API key must be supplied
    in the header, but the IP address must also be registered with the correct
    credentials for the request to work.
 * Scopus.search uses OpenSearch and returns a few OpenSearch response elements
    in the response JSON, including totalResults, startIndex, and itemsPerPage.
    Look into increasing number of items per page so we get back a larger response.

--- TODOs ---
 * Look into increasing number of items per page in Scopus search.
"""

# Standard imports
from urllib.parse import quote

# Third-party imports
import requests

# Local imports
from . import models
from . import config
from scopy.scopy_errors import *
from pypub.paper_info import PaperInfo
from pypub.pypub_errors import *
import scopy.utils as utils


class Scopus(object):
    """
    Attributes
    ----------
    
    """
    
    base_url = 'http://api.elsevier.com/content'
    
    def __init__(self):

        # Authentication
        self.key = config.api_key

        self.abstract_retrieval = AbstractRetrieval(self)
        self.article_retrieval = ArticleRetrieval(self)

        #This doesn't look like it is currently being used        
        self.authentication = Authentication(self)

        self.bibliography_retrieval = BibliographyRetrieval(self)
        self.entry_retrieval = EntryRetrieval(self)
        self.get_all_data = GetAllData(self)

    def _get_default_headers(self):
        header = dict()
        header['Accept'] = 'application/json'
        header['X-ELS-APIKey'] = self.key

        return header

    def make_abstract_get_request(self, url=None, input_id=None, input_type=None):
        """

        Parameters
        ----------
        url : str
            Target URL of the API request. This is not none
            when searching by some other means besides a DOI lookup.
        doi : str
            DOI of target paper.

        Returns
        -------

        """
        if url is None:
            if input_id is None:
                raise LookupError('Need to enter a URL or DOI')
            url = self.base_url + '/abstract/' + input_type + '/' + input_id

        header = self._get_default_headers()
        
        #http://api.elsevier.com/documentation/retrieval/AbstractRetrievalViews.htm
        params = {'view' : 'FULL'}

        resp = requests.get(url, headers=header, params=params)

        #Removed last bits of the IP
        #401 - '{"service-error":{"status":{"statusCode":"AUTHENTICATION_ERROR","statusText":"Client IP Address: 24.211.***.*** does not resolve to an account"}}}'

        if not resp.ok:
            if resp.status_code == 401:
                raise ConnectionRefusedError('Client IP Address does not resolve to an account')
            if resp.status_code == 404:
                raise LookupError('Could not find DOI on Scopus.')
            raise ConnectionError('Failed to connect to Scopus with status code %d' % resp.status_code)

        resp_json = resp.json()
        retrieval_resp = resp_json.get('abstracts-retrieval-response')

        return retrieval_resp

    def search(self, search_string, view = 'standard', date_range=None):
        '''

        Documentation of function at:
        http://api.elsevier.com/documentation/SCOPUSSearchAPI.wadl

        Parameters
        ----------
        search_string : str
            The search term.
        date_range : str
            Range of dates to search over.
        view : str
            {'standard','complete'}
            See http://api.elsevier.com/documentation/search/SCOPUSSearchViews.htm
            The standard is currently the default as this doesn't return
            all of the possible information on a paper anyway, so let's make
            the request slightly quicker

        Returns
        -------

        '''
        '''
        Problem: limited to only 25 results per page. Sending an opensearch
        itemsPerPage request in the params as a Query object doesn't seem
        to increase the number of items per page that is returned.
        '''
        # Build target URL for get request
        url = self.base_url + '/search/scopus'

        # Build request headers
        header = dict()
        header['Accept'] = 'application/json'
        header['X-ELS-APIKey'] = self.key

        # Attempts to increase items per page by using opensearch formatting.
        # Not working so far.
        #query_dict = dict()
        
        #JAH: Where are these coming from? Why do we want to
        #increase the # of results per page?
        #query_dict['@searchTerms'] = search_string
        #query_dict['@itemsPerPage'] = 50

        params = dict()
        #params['opensearch:Query'] = query_dict

        # Mandatory params
        params['query'] = search_string
        params['view'] = view
        if date_range is not None:
            params['date'] = date_range

        resp = requests.get(url, headers=header, params=params)
        
        if not resp.ok:
            if resp.status_code == 401:
                raise ConnectionRefusedError('Client IP Address does not resolve to an account')
            print(resp.text)
            print(resp.status_code)
            raise ConnectionError('Failed to connect to Scopus')
           
        return models.SearchResults(resp.json()['search-results'])
        
        #entry_list = results['entry']



class AbstractRetrieval(object):

    """
    http://api.elsevier.com/documentation/AbstractRetrievalAPI.wadl
    
    """

    '''
    So it turns out that this Abstract request also returns a lot of other information,
    including title, author, publication, full bibliography, etc.
    Does not return full text of article, see Article() class for that.
    This could be a catch-all get request to extract bibliography, etc.
    '''
    def __init__(self, parent):
        self.parent = parent

    def get_from_eid(self,eid):
        retrieval_resp = self.parent.make_abstract_get_request(input_type='eid', input_id=eid)
        return self._abstract_from_json(retrieval_resp)

    def get_from_doi(self, doi):
        retrieval_resp = self.parent.make_abstract_get_request(input_type='doi', input_id=doi)
        return self._abstract_from_json(retrieval_resp)

    def get_from_pii(self, pii):
        retrieval_resp = self.parent.make_abstract_get_request(input_type='pii', input_id=pii)
        return self._abstract_from_json(retrieval_resp)

    def get_from_pubmed(self, pubmed_id):
        retrieval_resp = self.parent.make_abstract_get_request(input_type='pubmed_id', input_id=pubmed_id)
        return self._abstract_from_json(retrieval_resp)


    def _abstract_from_json(self, json):
        core_data = json.get('coredata')
        if core_data is not None:
            abstract = core_data.get('dc:description')
        else:
            abstract = None
        return abstract


class ArticleRetrieval(object):
    """
        
    """
    def __init__(self, parent):
        self.parent = parent

    def get_from_doi(self, doi, return_json=False):
        return self._generic_retrieval(input_id=doi, input_type='doi', return_json=return_json)
        
    def get_from_eid(self,eid,return_json=False):
        return self._generic_retrieval(input_id=eid, input_type='eid', return_json=return_json)

    def get_from_pii(self, pii, return_json=False):
        return self._generic_retrieval(input_id=pii, input_type='pii', return_json=return_json)

    def get_from_pubmed(self, pubmed_id, return_json=False):
        return self._generic_retrieval(input_id=pubmed_id, input_type='pubmed_id', return_json=return_json)

    def _generic_retrieval(self, input_id, input_type, return_json):
        
        """
        http://dev.elsevier.com/retrieval.html#!/Article_Retrieval/ArticleRetrieval
        """
        # Make sure input_id is a string
        if isinstance(input_id, int):
            input_id = str(input_id)

        input_id = quote(input_id)

        url = self.parent.base_url + '/article/' + input_type + '/' + input_id

        header = self.parent._get_default_headers()
        params = {}

        resp = requests.get(url, headers=header, params=params)

        # Verification of connection
        if not resp.ok:
            if resp.status_code in (401, 403):
                raise ConnectionRefusedError('Client IP Address does not resolve to an account')
            if resp.status_code == 400:
                raise AuthenticationError('Full article access limited by Scopus. May be available elsewhere.')
            else:
                raise ConnectionError('Failed to connect to Scopus')

        retrieval_resp = resp.json().get('full-text-retrieval-response')

        if retrieval_resp is None:
            return None

        if return_json:
            return retrieval_resp
        else:
            return models.ScopusEntry(retrieval_resp)


class Authentication(object):
    
    """
        
    """
    
    def __init__(self, parent):
        self.parent = parent
        self.url = 'http://api.elsevier.com/authenticate/?platform=SCOPUS'
        self.url = 'http://api.elsevier.com/content/object/pii/S0167527308011704?view=META'
        self.url = 'http://api.elsevier.com/content/search/scopus'

    def get_auth(self):
        header = dict()
        header['Accept'] = 'application/json'

        key = self.parent.api_key()

        params = dict()
        # params['apiKey'] = key
        params['query'] = 'stress incontinence'

        header['X-ELS-APIKey'] = key
        header['X-ELS-ResourceVersion'] = 'XOCS'

        resp = self.parent.session.get(self.url, headers=header, params=params)


class BibliographyRetrieval(object):
    """

    """
    # TODO: check if there is even an entry first before trying to get the refs

    def __init__(self, parent):
        self.parent = parent

    def get_from_doi(self, doi, return_json=False):
        return self._generic_retrieval(input_id=doi, input_type='doi', return_json=return_json)

    def get_from_pii(self, pii, return_json=False):
        return self._generic_retrieval(input_id=pii, input_type='pii', return_json=return_json)

    def get_from_eid(self, eid, return_json=False):
        return self._generic_retrieval(input_id=eid, input_type='eid', return_json=return_json)

    def get_from_pubmed(self, pubmed_id, return_json=False):
        return self._generic_retrieval(input_id=pubmed_id, input_type='pubmed_id', return_json=return_json)

    def _generic_retrieval(self, input_id, input_type, return_json):
        retrieval_resp = self.parent.make_abstract_get_request(input_type=input_type, input_id=input_id)
        ref_list = self._refs_from_json(retrieval_resp)

        if ref_list is None:
            return None

        if return_json:
            return ref_list
        else:
            ref_object_list = []
            for ref_json in ref_list:
                ref_object_list.append(models.ScopusRef(ref_json))
            return ref_object_list

    @classmethod
    def _refs_from_json(cls, json):
        # Descend through JSON tree to get references list
        # At each step, need to make sure that the level exists.
        # Otherwise, return None.
        next_level = json
        levels = ['item', 'bibrecord', 'tail', 'bibliography']
        x = 0
        while next_level is not None and x < len(levels):
            next_level = next_level.get(levels[x])
            x += 1

        if next_level is not None:
            ref_count = next_level.get('@refcount')
            if ref_count is not None:
                if int(ref_count) == 0:
                    raise ReferencesNotFoundError('No references found. Possibly due to zero search results.')

            next_level = next_level.get('reference')

        return next_level


class EntryRetrieval(object):
    """
    http://api.elsevier.com/documentation/AbstractRetrievalAPI.wadl

    """
    def __init__(self, parent):
        self.parent = parent

    def get_from_eid(self,eid):
        retrieval_resp = self.parent.make_abstract_get_request(input_type='eid', input_id=eid)
        return models.ScopusEntry(retrieval_resp)

    def get_from_doi(self, doi):
        retrieval_resp = self.parent.make_abstract_get_request(input_type='doi', input_id=doi)
        return models.ScopusEntry(retrieval_resp)

    def get_from_pii(self, pii):
        retrieval_resp = self.parent.make_abstract_get_request(input_type='pii', input_id=pii)
        return models.ScopusEntry(retrieval_resp)

    def get_from_pubmed(self, pubmed_id):
        retrieval_resp = self.parent.make_abstract_get_request(input_type='pubmed_id', input_id=pubmed_id)
        return models.ScopusEntry(retrieval_resp)


class GetAllData(object):
    """
    Returns both the entry information and the full references (if available).
    """
    def __init__(self, parent):
        self.parent = parent

    def get_from_eid(self,eid):
        retrieval_resp = self.parent.make_abstract_get_request(input_type='eid', input_id=eid)
        return self._construct_object(retrieval_resp)

    def get_from_doi(self, doi):
        retrieval_resp = self.parent.make_abstract_get_request(input_type='doi', input_id=doi)
        return self._construct_object(retrieval_resp)

    def get_from_pii(self, pii):
        retrieval_resp = self.parent.make_abstract_get_request(input_type='pii', input_id=pii)
        return self._construct_object(retrieval_resp)

    def get_from_pubmed(self, pubmed_id):
        retrieval_resp = self.parent.make_abstract_get_request(input_type='pubmed_id', input_id=pubmed_id)
        return self._construct_object(retrieval_resp)

    def _construct_object(self, json):
        if json is None:
            return None

        entry = models.ScopusEntry(json=json)

        # Get references from the API response
        ref_list = BibliographyRetrieval._refs_from_json(json=json)
        references = []
        if ref_list is not None:
            for ref_json in ref_list:
                references.append(models.ScopusRef(ref_json))

        paper_info = PaperInfo()
        #paper_info.entry = utils.convert_to_dict(entry)
        #paper_info.references = utils.refs_to_list(references)
        paper_info.entry = entry
        paper_info.references = references

        paper_info.doi = getattr(entry, 'doi', None)
        paper_info.pdf_link = None
        paper_info.publisher_interface = None
        paper_info.scraper_obj = None

        return paper_info
