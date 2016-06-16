from scopus_apis import *

api = Scopus()

#api.search('neuromodulation')

doi = '10.1016/S0021-9290(01)00201-9'
abs = api.abstract_retrieval.get_from_doi(doi)
print(abs)

refs = api.bibliography_retrieval.get_from_doi(doi)

