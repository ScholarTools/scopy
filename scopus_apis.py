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
import json

# Third-party imports
import requests

# Local imports
from scopy_errors import *
import models


class Scopus(object):
    def __init__(self):
        self.base_url = 'http://api.elsevier.com/content'

        # Authentication
        self.key = self.api_key()

        self.authentication = Authentication(self)
        self.abstract_retrieval = Abstract_Retrieval(self)
        self.bibliography_retrieval = Bibliography_Retrieval(self)

    def api_key(self):
        with open('api_key.txt', 'r') as file:
            key = file.read()
        return key

    def get_default_headers(self):
        header = dict()
        header['Accept'] = 'application/json'
        header['X-ELS-APIKey'] = self.key

        return header

    def make_abstract_get_request(self, url=None, doi=None):
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
            if doi is not None:
                url = self.base_url + '/abstract/doi/' + doi
            else:
                raise LookupError('Need to enter a URL or DOI')

        header = self.get_default_headers()
        params = {'view' : 'FULL'}

        resp = requests.get(url, headers=header, params=params)
        retrieval_resp = resp.json()['abstracts-retrieval-response']

        return retrieval_resp

    def search(self, search_string, date_range=None):
        '''

        Parameters
        ----------
        search_string : str
            The search term.
        date_range : str
            Range of dates to search over.

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
        query_dict = dict()
        query_dict['@searchTerms'] = search_string
        query_dict['@itemsPerPage'] = 50

        params = dict()
        params['opensearch:Query'] = query_dict

        # Mandatory params
        params['query'] = search_string
        params['view'] = 'COMPLETE'
        if date_range is not None:
            params['date'] = date_range

        resp = requests.get(url, headers=header, params=params)
        results = resp.json()['search-results']
        entry_list = results['entry']

        print('Total results: ' + results['opensearch:totalResults'])


class Abstract_Retrieval(object):
    """

    """
    '''
    So it turns out that this Abstract request also returns a lot of other information,
    including title, author, publication, full bibliography, etc.
    Does not return full text of article. See Article() class for that.
    This could be a catch-all get request to extract bibliography, etc.
    '''
    def __init__(self, parent):
        self.parent = parent

    def get_from_doi(self, doi):
        retrieval_resp = self.parent.make_abstract_get_request(doi=doi)
        return self._abstract_from_json(retrieval_resp)

    def get_from_pii(self, pii):
        url = self.parent.base_url + '/abstract/pii/' + pii
        retrieval_resp = self.parent.make_abstract_get_request(url=url)
        return self._abstract_from_json(retrieval_resp)

    def _abstract_from_json(self, json):
        core_data = json.get('coredata')
        abstract = core_data.get('dc:description')
        return abstract


class Authentication(object):
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

class Bibliography_Retrieval(object):
    def __init__(self, parent):
        self.parent = parent

    def get_from_doi(self, doi, return_json=False):
        retrieval_resp = self.parent.make_abstract_get_request(doi=doi)
        ref_list = self._refs_from_json(retrieval_resp)

        import pdb
        pdb.set_trace()

        if return_json:
            return ref_list
        else:
            return models.Bibliography(ref_list)

    def _refs_from_json(self, json):
        # Descend through JSON tree to get references list
        item = json.get('item')
        bibrecord = item.get('bibrecord')
        tail = bibrecord.get('tail')
        bibliography = tail.get('bibliography')
        refs = bibliography.get('reference')
        return refs
