import json
import mimetypes
import posixpath
import urllib
import urlparse
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as helpers

from ckan.lib.base import request
from ckan.lib.helpers import parse_rfc_2822_date

from ckanext.lire.controllers.pan import (
    PANController,
)

from ckan.lib.base import BaseController

################
## LIRE RELIN ##
################
class RELINController(BaseController):

  #filter commutative relations
  def removeCommutative(self,eKey):
    
    eKey1 = eKey
    for q in eKey:
      for key,p in enumerate(eKey1):
        if ((q['subject'] == p['object']) and (q['object'] == p['subject'])):
          eKey1[key]['subject'] = q['subject']
          eKey1[key]['object'] = q['object']

    eKey1 = dict((v['subject'],v) for v in eKey1).values()
           
    return eKey1 

  #function to get all relations for each dataset
  def oneToAllRelationships(self,relationships,datasets):

    eKey = []

    for dataset in relationships:
      for p in datasets:
        if (len(datasets[p]['relationships']) > 0):
	  temp_rel = datasets[p]['relationships']
          for q in temp_rel:
            if (q['subject'] == dataset):
              temp = {'subject':datasets[p]['title'],'object':q['object']}
              eKey.append(temp)

    return eKey

