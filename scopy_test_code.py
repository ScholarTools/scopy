from scopus_apis import *

api = Scopus()

#api.search('neuromodulation')

doi = '10.1016/S0021-9290(01)00201-9'
abs = api.abstract_retrieval.get_from_doi(doi)
print(abs)

#refs = api.bibliography_retrieval.get_from_doi(doi)

pubmed_id = '11826063'

refs = api.bibliography_retrieval.get_from_pubmed(pubmed_id)

entry = api.article_retrieval.get_from_doi(doi)

import pdb
pdb.set_trace()
