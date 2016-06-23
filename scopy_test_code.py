from scopy import Scopus

api = Scopus()

#api.search('neuromodulation')

api.search('PMID(3806812)')


doi = '10.1016/S0021-9290(01)00201-9'
abs = api.abstract_retrieval.get_from_doi(doi)
print(abs)

#refs = api.bibliography_retrieval.get_from_doi(doi)

pubmed_id = '11826063'
pubmed_id = '3806812' #Doesn't work!

refs = api.bibliography_retrieval.get_from_pubmed(pubmed_id)

# TODO: figure out why this is returning None
entry = api.article_retrieval.get_from_doi(doi)

import pdb
pdb.set_trace()
