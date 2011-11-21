import logging
log = logging.getLogger('zen.DeviceSearch')

import os
import Globals
from Products.CMFCore.DirectoryView import registerDirectory

skinsDir = os.path.join(os.path.dirname(__file__), 'skins')
if os.path.isdir(skinsDir):
    registerDirectory(skinsDir, globals())

from Products.ZenModel.ZenPack import ZenPack as ZenPackBase

class ZenPack(ZenPackBase):
    def install(self, dmd):
        super(ZenPack, self).install(dmd)
        
    def remove(self, dmd, leaveObjects=False):
        super(ZenPack, self).remove(dmd, leaveObjects)


from Products.ZenUtils.Utils import monkeypatch

try:
    from Products.Zuul.catalog.global_catalog import DeviceWrapper, IpInterfaceWrapper

    @monkeypatch('Products.Zuul.catalog.global_catalog.DeviceWrapper')
    def searchKeywords(self):
        device = self._context.primaryAq()
        return super(DeviceWrapper, self).searchKeywords() + (device.zSnmpCommunity,)
        #                                                         ^ Add other indexable properties (cProp, zProp, Attr) here as context device

    @monkeypatch('Products.Zuul.catalog.global_catalog.IpInterfaceWrapper')
    def searchKeywordsForChildren(self):
        """
        When searching, what things to search on
        """
        if self._context.titleOrId() in ('lo', 'sit0'):
            #                             ^ Add other interface names which are ignored from indexing
            return ()

        try:
            # If we find an interface IP address, link it to an interface
            ipAddresses = [x for x in self._context.getIpAddresses() \
                                 if not x.startswith('127.0.0.1/') and \
                                    not x.startswith('::1/')]
        except Exception:
            ipAddresses = []

        return super(IpInterfaceWrapper, self).searchKeywordsForChildren() + (
               self._context.description, self._context.titleOrId(),
               #        ^ Add other indexable properties (cProp, zProp, Attr) here as context self._context
               )

    @monkeypatch('Products.Zuul.catalog.global_catalog.IpInterfaceWrapper')
    def searchExcerpt(self):
        """
        How the results are displayed in the search drop-down
        """
        return super(IpInterfaceWrapper, self).searchExcerpt() + ' ' + ' '.join([
               self._context.description, self._context.titleOrId(),
               ])
               #        ^ Add other indexable properties (cProp, zProp, Attr) here as context self._context

except ImportError:
    pass
