##Modified copy of zenoss DeviceSearch

from zope.component import adapts
from zope.interface import implements
from Products.AdvancedQuery import MatchGlob, And, Or, Eq, In, RankByQueries_Max
from Products.ZCatalog.interfaces import ICatalogBrain
from Products.ZenModel.DataRoot import DataRoot
from Products.Zuul.utils import allowedRolesAndGroups
from Products.Zuul.search import ISearchProvider
from Products.Zuul.search import ISearchResult

class DeviceSearchProvider(object):
    """
    Provider which searches Zenoss's global catalog for matching devices
    """
    implements(ISearchProvider)
    adapts(DataRoot)

    def __init__(self, dmd):
        self._dmd = dmd
    

    def getSearchResults(self, parsedQuery,
                         sorter=None, unrestricted=False):
        """
        Queries the catalog.  Searches the searchKeywords index
        using *keyword1* AND *keyword2* AND so on. 
        If there are preferred categories, find maxResults # of instances
        before searching other categories.

        @rtype generator of BrainSearchResult objects
        """
        operators = parsedQuery.operators
        keywords = parsedQuery.keywords

        if not keywords:
            return
        
        results = self.doMySearch( keywords, unrestricted )

        if sorter is not None:
            results = sorter.limitSort(results)

        return results

    def doMySearch( self, keywords, unrestricted=False ):

        def listMatchGlob(op, index, list):
            return op(*[ MatchGlob(index, '*%s*' % i ) for i in list ])
        
        full_query = listMatchGlob(And, 'searchKeywords', keywords)

        querySet = full_query
        if not unrestricted:
            # take permissions into account
            roles = In('allowedRolesAndUsers', allowedRolesAndGroups(self._dmd))
            querySet = [full_query, roles]
            querySet = And(*querySet)
            
        catalogItems = self._dmd.global_catalog.evalAdvancedQuery(querySet)
        brainResults = [DeviceSearchResult(catalogItem)
                        for catalogItem in catalogItems
                        if catalogItem.searchExcerpt is not None]
        return brainResults

    def getQuickSearchResults(self, parsedQuery, maxResults=None):
        """
        Currently just calls getSearchResults
        """
        return self.getSearchResults( parsedQuery, maxResults )


class DeviceSearchResult(object):
    """
    Wraps a brain from the search catalog for inclusion in search results.
    """

    implements(ISearchResult)

    def __init__(self, brain):
        self._brain = brain

    @property
    def url(self):
        return self._brain.getPath()

    @property
    def category(self):
        return self._brain.meta_type

    @property
    def excerpt(self):
        return self._brain.searchExcerpt

    iconTemplate = '<img src="%s"/>'
    
    @property
    def icon(self):
        return self.iconTemplate % self._brain.searchIcon
    
    @property
    def popout(self):
        return False

