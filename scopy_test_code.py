from scopy import Scopus

from scopy.scopy_errors import *

api = Scopus()

#api.search('neuromodulation')

results = api.search('PMID(3806812)')


doi = '10.1016/S0021-9290(01)00201-9'
abs = api.abstract_retrieval.get_from_doi(doi)
print(abs)

#refs = api.bibliography_retrieval.get_from_doi(doi)

pubmed_id = '11826063'
pubmed_id = '3806812' #Doesn't work! perhaps via search?

try:
    refs = api.bibliography_retrieval.get_from_pubmed(pubmed_id)
    print(refs)
except ReferencesNotFoundError as e:
    print(str(e))
    pass

# TODO: figure out why this is returning None
entry = api.article_retrieval.get_from_doi(doi)

import pdb
pdb.set_trace()
