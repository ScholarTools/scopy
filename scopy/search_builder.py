# -*- coding: utf-8 -*-
"""
Still trying to decide on the design of this ...
"""

#JAH: Perhaps we want to expose each field as a class?
#TODO: Also provide convenience methods that group search fields
#i.e. -> method to print common entries
#     -> method to print identifier fields
# authors, journal stuffs, paper stuffs (year, volume, issue, page #s)

#from search_builder import title, auth
#   title('Testing') and auth('Smith')
#
#   __and__
#   __or__
#   AND NOT => this would be tricky, but doable
#   - also tricky, the order of operations ...
#
#OR

#*********************************************
#import search_builder as s  
# s.title('Testing') and s.auth('Smith') #less importing work, more tab complete


#http://api.elsevier.com/content/search/fields/scopus
#http://api.elsevier.com/documentation/search/SCOPUSSearchTips.htm

#TODO: We may also want a GUI as well

all_fields = {'abs':'Abstract'}

class CombinedSearhTerms(object):

    #Keeps track of the individual terms
    #Able to call a method which computes the final result

    def __and__(self):
        pass
    
    def __or__(self):
        pass
    
    def __not__(self):
        pass
    

    def __repr__(self):
        pass


class SearchTerm(object):
    
    """

    #TODO: Define these attributes    
    
    Attributes
    ----------
    key
    value
    description
    Example
    children
    """

    def __and__(self):
        pass
    
    def __or__(self):
        pass
    
    def __not__(self):
        pass
    
    @property
    def query(self):
        return '%s(%s)' % (self.key,self.value)

    def __repr__(self):
        #Show attributes and include query
        pass
    
    #Attributes
 
#These could also perform filtering on the input text depending upon the field, see subjarea example

 
#NOTE: I am intentially buck the naming trend here, I might change these
#to functions that create a SearchTerm 
class pii(SearchTerm):

    key = 'PII'
    description = 'Publication Item Identifier'
    example = 'pii(S12345678) returns the document with the matching PII'
    children = None
    
    def __init__(self,text):
        self.value = text


class ref(SearchTerm):
    
    def __init__(self,text):
        self.key = 'ref'
        self.value = text
        self.description = 'References'
        self.example = 'TODO'
        self.children = ['refauth','reftitle','refscrtitle','refpubyear','refpage'] #TODO: Not sure if these fields are case sensitive, examples are all caps


class subjarea(SearchTerm):
    
    #Does this work for tab complete? Yes!
    #s.subjarea(s.subjarea.AGRI)
    #Options:
    AGRI = 'AGRI'
    ARTS = 'ARTS'
    BIOC = 'BIOC'

    # Potential other versions:
    agriculture = 'AGRI'
    arts = 'ARTS'
    biochemistry = 'BIOC'
    genetics = 'BIOC'
    molecular_biology = 'BIOC'
    business = 'BUSI'
    management = 'BUSI'
    accounting = 'BUSI'
    chemical_engineering = 'CENG'
    chemistry = 'CHEM'
    computer_science = 'COMP'
    decision_sciences = 'DECI'
    dentistry = 'DENT'
    earth_science = 'EART'
    economics = 'ECON'
    energy = 'ENER'
    engineering = 'ENGI'
    environmental_science = 'ENVI'
    health = 'HEAL'
    immunology = 'IMMU'
    microbiology = 'IMMU'
    mathematics = 'MATH'
    trade_publication = 'MEDI'
    medicine = 'NEUR'
    nursing = 'NURS'
    pharmacology = 'PHAR'
    psychology = 'PSYC'
    social_sciences = 'SOCI'
    veterinary = 'VETE'
    multidisciplinary = 'MULT'
    
    def __init__(self,text):

        #We could pass in         
        
        self.key = 'subjarea'
        self.value = text #We could validate this
        self.description = 'TODO'
        self.example = 'TODO'
        self.children = None


class title_abs_key(SearchTerm):

    key = 'title-abs-key'

    def __init__(self,text):
        
        self.key = 'title-abs-key' #Notice the rename
        self.value = text
        self.description = 'TODO'
        self.example = 'TODO'
        self.children = ['title','abs','key'] #these are sort of obvious



"""
class SearchTerm(object):


    FIELDS_AND_NAMES = {'abs','Abstract'}    
    
    
    def __setattr__(self, name, value):
        #TODO: Look if it is valid
    #TODO: On setting, add to a list and correct
        #TODO: On display, display the correct value
        pass
    
    def _null(self):
        #Setting up tab complete
        #http://api.elsevier.com/content/search/fields/scopus
    
        self.abs = None #Abstract
        self.affil = None #Affiliation
        self.affilcity = None #Affiliation city
        self.affilcountry = None #Affiliation country
        
        self.pmid = None        
        
        self.title = None #Title
        self.title_abs_key = None #Title abstract key - yikes, now we need a conversion to title-abs-key :/
        self.title_abs_key_auth = None #Title, abstract, key, authors
"""