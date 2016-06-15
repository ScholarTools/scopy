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


class Scopus(object):
    def __init__(self):
        self.base_url = 'http://api.elsevier.com/content'

        # Authentication
        self.key = self.api_key()

        self.authentication = Authentication(self)
        self.abstract = Abstract(self)

    def api_key(self):
        with open('api_key.txt', 'r') as file:
            key = file.read()
        return key

    def make_get_request(self, header=None, params=None):
        pass

    def search(self, search_string, date_range=None):
        # Build target URL for get request
        url = self.base_url + '/search/scopus'

        # Build request headers
        header = dict()
        header['Accept'] = 'application/json'
        header['X-ELS-APIKey'] = self.key

        params = dict()
        params['query'] = search_string
        params['view'] = 'COMPLETE'
        params['itemsPerPage'] = 50
        if date_range is not None:
            params['date'] = date_range

        resp = requests.get(url, headers=header, params=params)
        results = resp.json()['search-results']

        import pdb
        pdb.set_trace()


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


class Abstract(object):
    def __init__(self, parent):
        self.parent = parent

    def get_from_doi(self, doi):
        url = self.parent.base_url + '/abstract/doi/' + doi
        pass

    def get_from_pii(self, pii):
        url = self.parent.base_url + '/abstract/pii/' + pii
        pass
