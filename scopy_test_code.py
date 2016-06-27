from scopy import Scopus

from scopy.scopy_errors import *

api = Scopus()

neuro = api.search('neuromodulation')
neuro = neuro.entries
first = neuro[0]

eid_search = api.search('eid(%s)' % first.eid)

eid_bib = api.bibliography_retrieval.get_from_eid(first.eid)


results = api.search('PMID(3806812)')

doc = results.entries[0]

temp = api.abstract_retrieval.get_from_eid(doc.eid)


doi = '10.1016/S0021-9290(01)00201-9'
abs = api.abstract_retrieval.get_from_doi(doi)
print(abs)

#refs = api.bibliography_retrieval.get_from_doi(doi)

pubmed_id = '11826063'
#pubmed_id = '3806812' #Doesn't work! perhaps via search?

try:
    pubmed_refs = api.bibliography_retrieval.get_from_pubmed(pubmed_id)
    print(pubmed_refs)
except ReferencesNotFoundError as e:
    print(str(e))
    pass

try:
    doi_refs = api.bibliography_retrieval.get_from_doi(doi, return_json=True)
except Exception as exe:
    print(str(exe))

# TODO: figure out why this is returning None
entry = api.article_retrieval.get_from_doi(doi)